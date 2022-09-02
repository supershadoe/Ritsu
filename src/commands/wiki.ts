`use strict`;

import {
    APIApplicationCommandInteractionDataStringOption,
    APIApplicationCommandInteractionDataSubcommandOption,
    APIChatInputApplicationCommandInteraction,
    ComponentType,
    RESTPatchAPIWebhookWithTokenMessageJSONBody
} from "discord-api-types/v10";
import { Env } from "..";
import { deferResponse, editInteractionResp, not_impl } from "../utils";

/** API URLS of the wikis. */
const WIKI_URLS = {
    fandom: (fandom_name: string) =>
        `https://${fandom_name}.fandom.com/api.php`,
    wikipedia: (language: string) =>
        `https://${language}.wikipedia.org/w/api.php`
};

function knownCommand(cmdName: string): cmdName is "fandom" | "wikipedia" {
    return ["fandom", "wikipedia"].includes(cmdName)
}

/** A model of the response from MediaWiki opensearch. */
interface WikiResponse {
    /** The search term */
    0: string;
    /** Titles of the articles */
    1: string[];
    /** Short descriptions of the articles (usually blank for some reason) */
    2: string[];
    /** Links to articles */
    3: string[];
}

async function fetchArticleAndRespond(
    searchTerm: string, subdomain: string,
    behaviourFlag: "fandom" | "wikipedia", appID: string,
    ctx: ExecutionContext, interactionToken: string
): Promise<Response> {
    const cache = caches.default;
    const queryString = new URLSearchParams({
        action: "opensearch",
        search: searchTerm,
        limit: "5"
    });
    const requestURL =
        `${WIKI_URLS[behaviourFlag](subdomain)}?${queryString.toString()}`;
    let response = await cache.match(requestURL);
    const interactionResponse: RESTPatchAPIWebhookWithTokenMessageJSONBody = {};

    if (! response) {
        response = await fetch(requestURL);
        if (! response.ok) {
            interactionResponse.content =
                "Error while fetching the article.\nAPI responded with"
                + `**${response.status}**: **${response.statusText}**.`;
            return editInteractionResp(
                appID, interactionToken, interactionResponse
            );
        }
        ctx.waitUntil(cache.put(requestURL, response.clone()));
    }

    const results = await response.json<WikiResponse>();
    if (results[1].length < 1) {
        interactionResponse.content =
            `No search results found for ${searchTerm}`;
        return editInteractionResp(
            appID, interactionToken, interactionResponse
        );
    }

    interactionResponse.content =
        `Here's the search results for '${searchTerm}'.\n`
        + `Direct link: [Click here](${results[3][0]})`;
    if (results[1].length > 1)
        interactionResponse.components = [{
            type: ComponentType.ActionRow,
            components: [{
                type: ComponentType.SelectMenu,
                custom_id: "wiki-search",
                placeholder: "Select another article",
                options: results[1].map((value, index) => ({
                    value: index.toString(),
                    label: value
                }))
            }]
        }];

    return editInteractionResp(appID, interactionToken, interactionResponse);
}

export function wiki(interaction: APIChatInputApplicationCommandInteraction, env: Env, ctx: ExecutionContext): Response {
    const subcmd =
        <APIApplicationCommandInteractionDataSubcommandOption>
            interaction.data.options![0];
    if (! knownCommand(subcmd.name))
        return not_impl();

    const options =
        <APIApplicationCommandInteractionDataStringOption[]>
            subcmd.options!;
    let [searchTerm, subdomain] = ["", "en"];
    options.forEach(opt => {
        if (opt.name === "fandom_name")
            subdomain = opt.value;
        else if (opt.name === "search_term")
            searchTerm = opt.value;
    });

    ctx.waitUntil(fetchArticleAndRespond(
        searchTerm, subdomain, subcmd.name, env.RITSU_APP_ID, ctx,
        interaction.token
    ));

    return deferResponse();
}
