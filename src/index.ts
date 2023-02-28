`use strict`;

import {
    APIInteraction, InteractionType, InteractionResponseType
} from "discord-api-types/v10";
import { syncCommands } from "./commandSync"
import pubchem from "./commands/pubchem";
import wiki from "./commands/wiki";
import { jsonResponse } from "./utils";
import { checkForSigAndTS, verifySig } from "./verifyInter";

/** 
 * A typed object to describe the data in the environment of workers
 * (like env vars, KV bindings, etc.)
 */
 export interface Env {
    RITSU_APP_PUB_KEY: string;
    RITSU_APP_ID: string;

    TRUSTED_LOCAL_ENV: boolean | undefined;
    RITSU_CLIENT_SECRET: string | undefined;
};

type HandlerArgs = [Request, Env, ExecutionContext];

const callbacks = { pubchem, wiki };

/**
 * Main interaction handler function
 * 
 * @param request The request that was received from Discord.
 * @param env The env for this request.
 * @param ctx The execution context for performing certain tasks.
 * @returns A promise for the response which is to be sent.
 */
async function handleInteractions(
    request: Request, env: Env, ctx: ExecutionContext
): Promise<Response> {
    let body = await request.json<APIInteraction>();
    let name = null;
    switch(body.type){
        case InteractionType.Ping:
            return jsonResponse({type: InteractionResponseType.Pong});
        case InteractionType.ApplicationCommand:
        case InteractionType.ApplicationCommandAutocomplete:
            name = body.data.name as keyof typeof callbacks;
            return callbacks[name](body, env, ctx);
        case InteractionType.MessageComponent:
        case InteractionType.ModalSubmit:
            name = body.data.custom_id.split('_')[0] as keyof typeof callbacks;
            return callbacks[name](body, env, ctx)
    }
}

const routeMap: Record<string, (a: HandlerArgs) => Promise<Response>> = {
    async POST(a) {
        return (
            await checkForSigAndTS(...a)
            ?? await verifySig(...a)
            ?? await handleInteractions(...a)
        );
    },
    async GET(a) {
        if (new URL(a[0].url).pathname === "/sync-cmds") {
            return await syncCommands(...a);
        }
        return this.default(a);
    },
    async default(a) {
        return Response.redirect(
            "Invalid request: Access through discord.", 301
        );
    }
}

export default {
    async fetch(...a: HandlerArgs): Promise<Response> {
        const meth = a[0].method;
        return (
            meth in routeMap
            ? await routeMap.meth(a)
            : await routeMap.default(a)
        );
    }
};
