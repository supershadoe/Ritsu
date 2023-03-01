`use strict`;

import {
    APIApplicationCommandInteractionDataStringOption,
    APIApplicationCommandInteractionDataSubcommandOption,
    APIChatInputApplicationCommandInteraction,
    APIChatInputApplicationCommandInteractionData,
    APIInteraction, ApplicationCommandType, ComponentType, InteractionType,
    RESTPatchAPIWebhookWithTokenMessageJSONBody
} from "discord-api-types/v10";
import { Env } from "..";
import { deferResponse, editInteractionResp, not_impl } from "../utils";

interface SubcommandStructure extends APIApplicationCommandInteractionDataSubcommandOption {
    name: "fandom" | "wikipedia",
    options: (APIApplicationCommandInteractionDataStringOption & {
        name: "fandom_name" | "search_term" | "language"
    })[]
}

export interface WikiCommandInteraction extends APIChatInputApplicationCommandInteraction {
    data: APIChatInputApplicationCommandInteractionData & {
        options: [SubcommandStructure]  
    }
};

/** API URLS of the wikis. */
const WIKI_URLS = {
    fandom: (fandom_name: string) =>
        `https://${fandom_name}.fandom.com/api.php`,
    wikipedia: (language: string) =>
        `https://${language}.wikipedia.org/w/api.php`
};

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

/**
 * The primary command handler for `wiki {}` command which performs an
 * opensearch using MediaWiki API and responds to the interaction.
 *
 * @param searchTerm The search term to fetch the data for.
 * @param appID The application ID of the bot.
 * @param ctx The execution context to use for caching.
 * @param interactionToken The token for the current interaction to edit the
 * deferred message.
 */
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
                "Error while fetching the article.\nAPI responded with "
                + `**${response.status}**: **${response.statusText}**.`;
            return await editInteractionResp(
                appID, interactionToken, interactionResponse
            );
        }
        ctx.waitUntil(cache.put(requestURL, response.clone()));
    }

    const results = await response.json<WikiResponse>();
    if (results[1].length < 1) {
        interactionResponse.content =
            `No search results found for ${searchTerm}`;
        return await editInteractionResp(
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
                type: ComponentType.StringSelect,
                custom_id: "wiki_search",
                placeholder: "Select another article",
                options: results[1].map((value, index) => ({
                    value: index.toString(),
                    label: value
                }))
            }]
        }];

    return await editInteractionResp(
        appID, interactionToken, interactionResponse
    );
}

function isSlashCommandInt(interaction: APIInteraction): interaction is WikiCommandInteraction {
    return (
        (interaction.type === InteractionType.ApplicationCommand) && (interaction.data.type === ApplicationCommandType.ChatInput)
    );
}

/**
 * Interaction handler for `/wiki` command.
 *
 * @param interaction The interaction object sent by Discord.
 * @param env The env at the time of execution.
 * @param ctx The execution context.
 * @returns A deferred response object to wait till data is fetched.
 */
export default function(
    interaction: APIInteraction,
    env: Env, ctx: ExecutionContext
): Response {
    if (isSlashCommandInt(interaction)) {
        const subcmd = interaction.data.options[0];

        let [searchTerm, subdomain] = ["", "en"];
        if (subcmd.name === "wikipedia") {
            subdomain = interaction.locale.split('-')[0];
        }
        subcmd.options.forEach(opt => {
            switch(opt.name) {
                case "fandom_name": subdomain = opt.value; break;
                case "search_term": searchTerm = opt.value; break;
                case "language": subdomain = opt.value; break;
            }
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
    return not_impl();
}
