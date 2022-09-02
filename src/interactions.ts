`use strict`;

import {
    APIChatInputApplicationCommandInteraction, APIInteraction,
    ApplicationCommandType,
    InteractionResponseType, InteractionType
} from "discord-api-types/v10"
import { Env } from ".";
import { jsonResponse } from "./utils";
import * as commands from "./commands";

type CommandHandler = {
    [cmd_name: commands.RitsuSlashCommand["name"]]:
        commands.RitsuSlashCommand["callback"]
};
const commandHandler: CommandHandler = {};
for (const cmd of Object.values(commands)) {
    commandHandler[cmd.name] = cmd.callback;
}

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
    /* Let all hell break loose when I add a new command and forget
     * to sync it. (its like 1 am in the morning and idw create
     * error handling for this)
     * 
     * Refer interactions.ts [line 44]
     */

    let body: APIInteraction = await request.json();
    switch(body.type){
        case InteractionType.Ping:
            return jsonResponse({type: InteractionResponseType.Pong});
        case InteractionType.ApplicationCommand:
            if (body.data.type === ApplicationCommandType.ChatInput) {
                body = <APIChatInputApplicationCommandInteraction> body;
                return commandHandler[body.data.name](body, env, ctx);
            }
            break;
        case InteractionType.MessageComponent:
            break;
        case InteractionType.ModalSubmit:
            break;
    }
    return new Response("Handling not implemented yet", { status: 501 });
}
