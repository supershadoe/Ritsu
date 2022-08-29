import {
    APIApplicationCommandInteractionDataStringOption, APIChatInputApplicationCommandInteraction,
    APIInteraction, APIInteractionResponse, InteractionResponseType,
    InteractionType, MessageFlags
} from "discord-api-types/v10"
import { Env } from ".";
import { deferResponse, jsonResponse } from "./utils";
import { pubchem } from "./commands/pubchem";

/**
 * Main interaction handler function
 * 
 * @param request The request that was received from Discord.
 * @param env The env for this request.
 * @param ctx The execution context for performing certain tasks.
 * @returns A promise for the response which is to be sent.
 */
export async function handleInteractions(
    request: Request, env: Env, ctx: ExecutionContext
): Promise<Response> {
    let body: APIInteraction = await request.json();
    switch(body.type){
        //TODO make some simple application command handler which breaks out of
        // the indentation hell i create with switch...case

        case InteractionType.Ping:
            return jsonResponse({type: InteractionResponseType.Pong});
        case InteractionType.ApplicationCommand:
            body = body as APIChatInputApplicationCommandInteraction;
            switch(body.data.name) {
                case "pubchem":
                    const compound_name = body.data.options![0] as
                        APIApplicationCommandInteractionDataStringOption;
                    ctx.waitUntil(pubchem(
                        compound_name.value, env.RITSU_APP_ID, ctx, body.token
                    ));
                    return deferResponse();
                default:
                    const response: APIInteractionResponse = {
                        type: InteractionResponseType.ChannelMessageWithSource,
                        data: {
                            content: "Will be implemented soon",
                            flags: MessageFlags.Ephemeral
                        }
                    };
                    return jsonResponse(response);
            }
        case InteractionType.MessageComponent:
            break
        case InteractionType.ModalSubmit:
            break
    }
    return new Response("Handling not implemented yet", { status: 501 });
}
