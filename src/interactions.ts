import { InteractionType } from "discord-api-types/v10"
import { Env } from ".";
import { jsonResponse } from "./utils"

/**
 * Main interaction handler function
 * 
 * @param request The request that was received from Discord.
 * @param _args The env and ctx for this request.
 * @returns A promise for the response which is to be sent.
 */
export async function handleInteractions(
    request: Request, ..._args: [Env, ExecutionContext]
): Promise<Response> {
    const body: any = await request.json();
    if (body.type === InteractionType.Ping) {
        return jsonResponse({type: 1});
    }
    return new Response("Handling not implemented yet", { status: 501 });
}
