import { InteractionType } from "discord-api-types/v10"

/**
 * Creates a Response object from JSON objects.
 *
 * Made just for convenience.
 *
 * @param responseBody The response object to stringify.
 * @param options Custom settings like headers/status code.
 * @returns A new response object generated with the required defaults.
 */
function jsonResponse(
    responseBody: object,
    options: object = {
        headers: {
            "Content-Type": "application/json;charset=UTF-8"
        }
    }
): Response {
    return new Response(JSON.stringify(responseBody), options);
}

/**
 * Main interaction handler function
 * 
 * @param interactionBody The body of request sent by Discord.
 * @returns A promise for the response which is to be sent.
 */
export async function handleInteractions(interactionBody: any): Promise<Response> {
    if (interactionBody.type === InteractionType.Ping) {
        return jsonResponse({type: 1});
    }
    return new Response("Handling not implemented yet", { status: 501 });
}
