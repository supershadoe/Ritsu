`use strict`;

import {
    APIApplicationCommandInteractionDataStringOption,
    APIApplicationCommandInteractionDataSubcommandOption,
    APIChatInputApplicationCommandInteraction,
    APIChatInputApplicationCommandInteractionData, APIInteraction,
    APIInteractionResponse, APIMessageComponentSelectMenuInteraction,
    APIMessageStringSelectInteractionData, ApplicationCommandType,
    ComponentType, InteractionResponseType, InteractionType,
    RESTPatchAPIWebhookWithTokenMessageJSONBody
} from "discord-api-types/v10";
import { Env } from "..";
import { deferResponse, editInteractionResp, jsonResponse, not_impl } from "../utils";

/** Structure of the subcommand object sent in the slash command interaction. */
interface SubcommandStructure extends
APIApplicationCommandInteractionDataSubcommandOption {
    name: "fandom" | "wikipedia",
    options: (APIApplicationCommandInteractionDataStringOption & {
        name: "fandom_name" | "search_term" | "language"
    })[]
}

/** Structure of the data object in slash command interaction. */
interface CmdInterDataStructure extends
APIChatInputApplicationCommandInteractionData {
    options: [SubcommandStructure]
}

/** Structure of the interaction object sent for a slash command. */
interface WikiCommandInteraction extends
APIChatInputApplicationCommandInteraction {
    data: CmdInterDataStructure
};

/** Structure of the interaction object sent for a message component. */
interface WikiComponentInteraction extends
APIMessageComponentSelectMenuInteraction {
    data: APIMessageStringSelectInteractionData & {
        custom_id: "wiki_search"
    }
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

/**
 * Type guard to guarantee that the given interaction is of a slash command.
 * 
 * @param interaction The interaction object.
 * @returns whether the given interaction is of a slash command.
 */
function isSlashCommandInt(interaction: APIInteraction): interaction is WikiCommandInteraction {
    return (
        (interaction.type === InteractionType.ApplicationCommand) && (interaction.data.type === ApplicationCommandType.ChatInput)
    );
}

/**
 * Type guard to guarantee that a given interaction is of a message component. 
 *
 * @param interaction The interaction object.
 * @returns whether the given interaction is of a message component.
 */
function isComponentInt(interaction: APIInteraction): interaction is WikiComponentInteraction {
    return (
        (interaction.type === InteractionType.MessageComponent) &&
        (interaction.data.component_type === ComponentType.StringSelect)
    );
}

/** API URLS of the wikis. */
const WIKI_URLS = {
    fandom: (fandom_name: string) =>
        `https://${fandom_name}.fandom.com/api.php`,
    wikipedia: (language: string) =>
        `https://${language}.wikipedia.org/w/api.php`
};

/**
 * Performs an opensearch using MediaWiki API and responds to the interaction.
 *
 * @param searchTerm The search term to fetch the data for.
 * @param subdomain To use a particular fandom/language for the search.
 * @param behaviourFlag To use either fandom or wikipedia.
 * @param appID The application ID of the bot.
 * @param ctx The execution context to use for caching.
 * @param interactionToken The token for the current interaction to edit the
 * deferred message.
 */
async function fetchArticleAndRespond(
    searchTerm: string, subdomain: string,
    behaviourFlag: "fandom" | "wikipedia", appID: string,
    ctx: ExecutionContext, interactionToken: string
) {
    const queryString = new URLSearchParams({
        action: "opensearch",
        search: searchTerm,
        limit: "5"
    });
    const requestURL =
        `${WIKI_URLS[behaviourFlag](subdomain)}?${queryString.toString()}`;
    let response = await fetch(requestURL);
    const interactionResponse: RESTPatchAPIWebhookWithTokenMessageJSONBody = {};
    if (! response.ok) {
        interactionResponse.content =
            "Error while fetching the article.\nAPI responded with "
            + `**${response.status}**: **${response.statusText}**.`;
        return await editInteractionResp(
            appID, interactionToken, interactionResponse
        );
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
        `Found this article for '${searchTerm}'.\n`
        + `Direct link: [Click here](${results[3][0]})`;
    if (results[1].length > 1)
        interactionResponse.components = [{
            type: ComponentType.ActionRow,
            components: [{
                type: ComponentType.StringSelect,
                custom_id: "wiki_search",
                placeholder: "Select another article",
                options: results[1].map((value, index) => ({
                    value: results[3][index].split('/').pop()!,
                    label: value
                }))
            }]
        }];

    await editInteractionResp(
        appID, interactionToken, interactionResponse
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
    interaction: APIInteraction, env: Env, ctx: ExecutionContext
) {
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
    } else if (isComponentInt(interaction)) {
        const oldContent = interaction.message.content.split("/");
        oldContent.pop();
        return jsonResponse({
            type: InteractionResponseType.UpdateMessage,
            data: {
                content: `${oldContent.join('/')}/${interaction.data.values[0]})`
            }
        } satisfies APIInteractionResponse);
    }
    return not_impl();
}
