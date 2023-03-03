`use strict`;

import {
    APIApplicationCommandInteractionDataStringOption,
    APIApplicationCommandInteractionDataSubcommandOption,
    APIChatInputApplicationCommandInteraction,
    APIChatInputApplicationCommandInteractionData, APIEmbed, APIInteraction,
    APIInteractionResponse, APIMessage,
    APIMessageComponentSelectMenuInteraction,
    APIMessageStringSelectInteractionData, ApplicationCommandType,
    ComponentType, InteractionResponseType, InteractionType,
    RESTPatchAPIWebhookWithTokenMessageJSONBody
} from "discord-api-types/v10";
import { Env } from "..";
import {
    deferResponse, editInteractionResp, jsonHeaders, jsonResponse, not_impl
} from "../utils";

/** Type of embed sent in response */
type ResponseEmbedT = Omit<APIEmbed, "image" | "url"> & Required<Pick<APIEmbed, "image" | "url">>

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
    },
    message: Omit<APIMessage, "embeds"> & {
        embeds: [ResponseEmbedT]
    }
}

/** Model for prefixsearch response on any MediaWiki API */
interface PrefixSearchResponse {
    batchcomplete: "",
    "continue"?: {
        psoffset: number,
        continue: string
    },
    query: {
        prefixsearch: ({
            /** Namespace of the article */
            ns: number,
            /** Title of the article */
            title: string,
            /** Unique ID of the article */
            pageid: number
        })[]
    }
}

/** Model for query for extract of the intro of an article in wikipedi */
interface ExtractsResponse {
    batchcomplete: "",
    query: {
        pages: Record<string, {
            /** Unique ID of an article */
            pageid: number,
            /** Namespace of the article -- usually 0 */
            ns: number,
            /** Title of the article */
            title: string,
            /** Extract of the intro of the article */
            extract: string,
            /** Thumbnail of the article */
            thumbnail: {
                source: string,
                width: number,
                height: number
            }
        }>
    }
}

/**
 * Type guard to guarantee that the given interaction is of a slash command.
 * 
 * @param interaction The interaction object.
 * @returns whether the given interaction is of a slash command.
 */
function isSlashCommandInt(interaction: APIInteraction):
interaction is WikiCommandInteraction {
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
function isComponentInt(interaction: APIInteraction): 
interaction is WikiComponentInteraction {
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
 * Perform a prefix search on the wiki pages using the API and adds to the
 * response object if the data can be fetched.
 * 
 * @param searchTerm The string to search for.
 * @param requestURL The URL to send the request to.
 * @param responseObj The response object to add data to.
 */
async function mediaWikiPrefixSearch(
    searchTerm: string, requestURL: URL,
    responseObj: RESTPatchAPIWebhookWithTokenMessageJSONBody
) {
    requestURL.search = "";
    Object.entries({
        action: "query",
        list: "prefixsearch",
        pssearch: searchTerm,
        pslimit: "5",
        format: "json"
    }).forEach(query => requestURL.searchParams.set(...query));
    const response = await fetch(requestURL);

    if (! response.ok)
        throw new Error(
            "Failed to perform the prefixsearch: "
            + `**${response.status} __${response.statusText}.__**`
        );

    const results =
        (await response.json<PrefixSearchResponse>()).query.prefixsearch;
    responseObj.content = 
        results.length > 0
        ? `Found this article for ${searchTerm}.\n`
        : `No articles found for ${searchTerm}`;
    if (results.length > 1)
        responseObj.components = [{
            type: ComponentType.ActionRow,
            components: [{
                type: ComponentType.StringSelect,
                custom_id: "wiki_search",
                placeholder: "Select another article",
                options: results.map(result => ({
                    value: result.pageid.toString(),
                    label: result.title,
                    description: result.pageid.toString()
                }))
            }]
        }];

    return (
        results.length > 0
        ? results[0].pageid
        : 0
    );
}

/**
 * Fetches the introductory part and thumbnail of an article from wikipedia
 * and generates an embed if data can be fetched.
 * 
 * @param pageid Unique ID of the article.
 * @param requestURL The URL to send the request to.
 * @param responseObj The response object to add data to.
 */
async function wikipediaExtracts(
    pageid: string, requestURL: URL,
    responseObj: RESTPatchAPIWebhookWithTokenMessageJSONBody
) {
    const directLink = `${requestURL.origin}/?curid=${pageid}`;
    requestURL.search = "";
    Object.entries({
        action: "query",
        prop: "extracts|pageimages",
        piprop: "thumbnail",
        pithumbsize: "100",
        pilicense: "any",
        pageids: pageid,
        exchars: "1200",
        exintro: "true",
        explaintext: "true",
        format: "json"
    }).forEach(query => requestURL.searchParams.set(...query));
    const response = await fetch(requestURL);

    if (! response.ok)
        throw new Error(
            "Failed to extract data from the article: "
            + `**${response.status} __${response.statusText}.__**`
        );

    const article = 
        (await response.json<ExtractsResponse>()).query.pages[pageid];
    responseObj.embeds = [{
        title: article.title,
        description: article.extract,
        color: 0xF6CEE7,
        image: { url: article.thumbnail.source },
        url: directLink
    } satisfies APIEmbed];
}

/**
 * Performs an opensearch using MediaWiki API and responds to the interaction.
 *
 * @param searchTerm The search term to fetch the data for.
 * @param subdomain To use a particular fandom/language for the search.
 * @param behaviourFlag To use either fandom or wikipedia.
 * @param appID The application ID of the bot.
 * @param interactionToken The token for the current interaction to edit the
 * deferred message.
 */
async function fetchArticleAndRespond(
    searchTerm: string, subdomain: string,
    behaviourFlag: keyof typeof WIKI_URLS, appID: string,
    interactionToken: string
) {
    try {
        const requestURL = new URL(WIKI_URLS[behaviourFlag](subdomain));
        const interactionResponse = {
            } as RESTPatchAPIWebhookWithTokenMessageJSONBody;
        const pageid = await mediaWikiPrefixSearch(
            searchTerm, requestURL, interactionResponse
        );

        if (behaviourFlag === "wikipedia" && pageid) {
            if (pageid)
                await wikipediaExtracts(
                    pageid.toString(), requestURL, interactionResponse
                );
        } else
            interactionResponse.content +=
                `${requestURL.origin}/?curid=${pageid}`;

        await editInteractionResp(
            appID, interactionToken, interactionResponse
        );
    } catch(e) {
        return editInteractionResp(
            appID, interactionToken, { content: (e as Error).message }
        );
    }
}

/**
 * Changes the embed on selecting another search result from the string select
 * menu.
 *
 * @param interaction For obtaining necessary information from the context.
 * @param pageid To fetch details of the selected article.
 */
async function switchWikipediaEmbed(
    interaction: WikiComponentInteraction, pageid: string
) {
    const url = new URL(interaction.message.embeds[0].url)
    url.pathname = "/w/api.php";
    url.search = "";
    const response:
        RESTPatchAPIWebhookWithTokenMessageJSONBody = {};
    response.content = interaction.message.content.split("\n").shift();
    try {
        await wikipediaExtracts(pageid, url, response);
        return await editInteractionResp(
            interaction.application_id, interaction.token, response
        );
    } catch(e) {
        response.content +=
            `\n\nError while switching links: ${(e as Error).message}`;
        return await editInteractionResp(
            interaction.application_id, interaction.token, response
        );
    }
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
            searchTerm, subdomain, subcmd.name, env.RITSU_APP_ID,
            interaction.token
        ));

        return deferResponse();
    } else if (isComponentInt(interaction)) {
        const pageid = interaction.data.values[0];
        switch(interaction.message.interaction?.name) {
            case "wiki fandom":
                const oldContent = interaction.message.content.split("=");
                oldContent.pop();
                return jsonResponse({
                    type: InteractionResponseType.UpdateMessage,
                    data: {
                        content: `${oldContent.join('=')}=${interaction.data.values[0]}`
                    }
                } satisfies APIInteractionResponse);
            case "wiki wikipedia":
                ctx.waitUntil(switchWikipediaEmbed(interaction, pageid));
                return jsonResponse({
                    type: InteractionResponseType.DeferredMessageUpdate
                } satisfies APIInteractionResponse);
        }
    }
    return not_impl();
}
