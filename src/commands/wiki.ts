`use strict`;

import {
    APIApplicationCommandInteractionDataStringOption,
    APIApplicationCommandInteractionDataSubcommandOption,
    APIChatInputApplicationCommandInteraction,
    APIChatInputApplicationCommandInteractionData, APIEmbed, APIInteraction,
    APIInteractionResponse, APIMessage, APIMessageComponentSelectMenuInteraction,
    APIMessageStringSelectInteractionData, ApplicationCommandType,
    ComponentType, InteractionResponseType, InteractionType,
    RESTPatchAPIWebhookWithTokenMessageJSONBody
} from "discord-api-types/v10";
import { Env } from "..";
import { deferResponse, editInteractionResp, generateErrorResp, jsonResponse, not_impl } from "../utils";

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
    message: Omit<APIMessage, "embeds" | "content"> & {
        content: string, 
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
 * Perform a prefix search on the wiki pages using the API and return the
 * results.
 * 
 * @param searchTerm The string to search for.
 * @param requestURL The URL to send the request to.
 * @returns Search results object if any response is received.
 */
async function mediaWikiPrefixSearch(searchTerm: string, requestURL: URL) {
    requestURL.search = "";
    Object.entries({
        action: "query",
        list: "prefixsearch",
        pssearch: searchTerm,
        pslimit: "5",
        format: "json"
    }).forEach(query => requestURL.searchParams.set(...query));
    const response = await fetch(requestURL);
    return (
        response.ok
        ? (await response.json<PrefixSearchResponse>()).query.prefixsearch
        : {
            "ritsu_error": "Failed to perform the prefixsearch.",
            "status_code": response.status,
            "status_text": response.statusText
        }
    );
}

/**
 * Fetches the introductory part and thumbnail of an article from wikipedia.
 * 
 * @param pageid Unique ID of the article.
 * @param requestURL The URL to send the request to.
 * @returns The result object if the response is ok.
 */
async function wikipediaExtracts(pageid: string, requestURL: URL) {
    requestURL.search = "";
    Object.entries({
        action: "query",
        prop: "extracts|pageimages",
        piprop: "thumbnail",
        pithumbsize: "100",
        pageids: pageid,
        exintro: "true",
        explaintext: "true",
        format: "json"
    }).forEach(query => requestURL.searchParams.set(...query));
    const response = await fetch(requestURL);
    return (
        response.ok
        ? (await response.json<ExtractsResponse>()).query.pages[pageid]
        : {
            "ritsu_error": "Failed to extract text from the article.",
            "status_code": response.status,
            "status_text": response.statusText
        }
    );
}

/**
 * Generates an embed if the command is for Wikipedia search.
 * 
 * @param article An article fetched from Wikipedia.
 * @returns An array (of length 1) of embed to send to Discord.
 */
function generateWikipediaEmbed(
    article: ExtractsResponse["query"]["pages"][string], articleLink: string
) {
    return [{
        title: article.title,
        description: article.extract,
        color: 0xF6CEE7,
        image: { url: article.thumbnail.source },
        url: articleLink
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
    interactionToken: string, pageid?: string
) {
    let firstLink: string;
    let article: Awaited<ReturnType<typeof wikipediaExtracts>> | null;
    const requestURL = new URL(WIKI_URLS[behaviourFlag](subdomain));
    const interactionResponse: RESTPatchAPIWebhookWithTokenMessageJSONBody = {};

    if (pageid) {
        firstLink = `${requestURL.origin}/?curid=${pageid})`;
        article = await wikipediaExtracts(pageid, requestURL);
    } else {
        const results = await mediaWikiPrefixSearch(searchTerm, requestURL);
        if ("ritsu_error" in results)
            return await editInteractionResp(
                appID, interactionToken, generateErrorResp(results)
            );

        if (results.length < 1) {
            interactionResponse.content =
                `No search results found for ${searchTerm}`;
            return await editInteractionResp(
                appID, interactionToken, interactionResponse
            );
        }

        interactionResponse.content = `Found this article for '${searchTerm}'.`;
        firstLink = `${requestURL.origin}/?curid=${results[0].pageid})`;

        if (behaviourFlag === "wikipedia")
            article = await wikipediaExtracts(
                results[0].pageid.toString(), requestURL
            );
        else
            article = null;

        if (results.length > 1)
        interactionResponse.components = [{
            type: ComponentType.ActionRow,
            components: [{
                type: ComponentType.StringSelect,
                custom_id: "wiki_search",
                placeholder: "Select another article",
                options: results.map(result => ({
                    value: result.pageid.toString(),
                    label: result.title
                }))
            }]
        }];
    }

    const directLink = `Direct link: [Click here](${firstLink})`;

    if (article) {
        if ("ritsu_error" in article) {
            interactionResponse.content += directLink;
        } else {
            interactionResponse.embeds = generateWikipediaEmbed(
                article, firstLink
            );
        }
    } else {
        interactionResponse.content += directLink;
    }

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
            searchTerm, subdomain, subcmd.name, env.RITSU_APP_ID,
            interaction.token
        ));

        return deferResponse();
    } else if (isComponentInt(interaction)) {
        // TODO change logic for wikipedia
        const pageid = interaction.data.values[0];
        if (interaction.message.interaction?.name === "wiki wikipedia") {
            ctx.waitUntil(fetchArticleAndRespond(
                "", 
            ))
            ctx.waitUntil(async function() {
                const oldContent = interaction.message.content.split("\n");
                if (oldContent.length > 1) oldContent.pop();
                let content = oldContent.join("\n");
                let embeds: APIEmbed[];
                let requestURL: URL;
                if (interaction.message.embeds.length > 0) {
                    requestURL = new URL(interaction.message.embeds[0].url);
                } else {
                    requestURL = new URL(
                        interaction.message.content.split("k](").pop()
                        ?? WIKI_URLS["wikipedia"]("en")
                    );
                }
                const replaceLink = `${requestURL.origin}/?curid=${pageid})`;
                const article = await wikipediaExtracts(
                    interaction.data.values[0], requestURL
                );
                if (("ritsu_error" in article)) {
                    content += `\n[Direct Link](${replaceLink})`;
                } else {
                    embeds = generateWikipediaEmbed(
                        article, replaceLink
                    );
                }
                return jsonResponse({
                    type: InteractionResponseType
                })
            }());
            return jsonResponse({
                type: InteractionResponseType.DeferredMessageUpdate
            } satisfies APIInteractionResponse);
        }
        const oldContent = interaction.message.content.split("=");
        oldContent.pop();
        return jsonResponse({
            type: InteractionResponseType.UpdateMessage,
            data: {
                content: `${oldContent.join('=')}=${interaction.data.values[0]})`
            }
        } satisfies APIInteractionResponse);
    }
    return not_impl();
}
