import {
    APIInteractionResponse, InteractionResponseType, MessageFlags, RESTPatchAPIWebhookWithTokenMessageJSONBody, RouteBases, Routes
} from "discord-api-types/v10";

/** Days of week for using in some commands. */
export const DAYS_OF_WEEK = [
    "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
]

/** Content-Type header for response with JSON body. */
export const jsonHeaders = {
    "Content-Type": "application/json;charset=UTF-8"
}

/**
 *  A helper generic to generate optional types
 */
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

/**
 * Creates a Response object from JSON objects.
 *
 * Made just for convenience.
 *
 * @param responseBody The response object to stringify.
 * @param options Custom settings like headers/status code.
 * @returns A new response object generated with the required defaults.
 */
export const jsonResponse = (
    responseBody: object, options: ResponseInit = { headers: jsonHeaders }
): Response => new Response(JSON.stringify(responseBody), options);

/**
 * To generate a json response for deferring interactions.
 * @returns An interaction response object.
 */
export const deferResponse = () => jsonResponse(<APIInteractionResponse> {
    type: InteractionResponseType.DeferredChannelMessageWithSource
}, { headers: jsonHeaders });

/**
 * Convenience function to edit an interaction response (usually for deferred
 * messages or for post interaction edits).
 * 
 * @param appID The application ID of the bot.
 * @param interactionToken The token of the webhook to edit.
 * @param interactionResponse The response to send.
 * @returns A promise for response from sending fetch req to Discord.
 */
export const editInteractionResp = (
    appID: string, interactionToken: string,
    interactionResponse: RESTPatchAPIWebhookWithTokenMessageJSONBody
): Promise<Response> => fetch(
    RouteBases.api + Routes.webhookMessage(appID, interactionToken),
    {
        method: "PATCH",
        headers: jsonHeaders,
        body: JSON.stringify(interactionResponse)
    }
    // FIXME using phenyl as search term breaks this :hmm:
    // also some stuff are missing in resp check that
    // also it feels kinda slower idk
);

/**
 * The default response sent for commands that don't have an implementation yet.
 *
 * @returns An ephemeral response object.
 */
 export const not_impl = (..._args: any[]): Response =>
 jsonResponse(<APIInteractionResponse> {
     type: InteractionResponseType.ChannelMessageWithSource,
     data: {
         content: "Will be implemented soon",
         flags: MessageFlags.Ephemeral
     }
 });
