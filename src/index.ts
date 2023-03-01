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
    RITSU_CLIENT_SECRET: string;

    TRUSTED_LOCAL_ENV: boolean | undefined;
};

/** The type of arguments streamed to and fro each function in this code. */
type HandlerArgs = [Request, Env, ExecutionContext];

/** Callbacks used for handle interactions. */
const callbacks = { pubchem, wiki };

/**
 * Handles all the requests which pass the signature verification.
 * 
 * @param a The usual arguments streamed through.
 * @param body The content of the request from Discord.
 * @returns A promise for the response to send.
 */
function handleInteractions(a: HandlerArgs, body?: string) {
    if (!body)
        return new Response("Bad request.", {status: 400});

    const [_, ...b] = a;
    const inter = JSON.parse(body) as APIInteraction;
    let name = null;

    switch(inter.type){
        case InteractionType.Ping:
            return jsonResponse({type: InteractionResponseType.Pong});

        case InteractionType.ApplicationCommand:
        case InteractionType.ApplicationCommandAutocomplete:
            name = inter.data.name as keyof typeof callbacks;
            return callbacks[name](inter, ...b);

        case InteractionType.MessageComponent:
        case InteractionType.ModalSubmit:
            name = inter.data.custom_id.split('_')[0] as keyof typeof callbacks;
            return callbacks[name](inter, ...b);
    }
}

/**
 * Maps the request methods to functions which handle
 * the request and provide a response.
 *
 * Used for executing code based on the method of request and the endpoint used.
 */
const routeMap: Record<string, (a: HandlerArgs) => Promise<Response>> = {
    async POST(a) {
        const _body: {body?: string} = {};
        return (
            await checkForSigAndTS(...a)
            ?? await verifySig(...a, _body)
            ?? handleInteractions(a, _body.body)
        );
    },
    async GET(a) {
        if (new URL(a[0].url).pathname === "/sync-cmds") {
            return await syncCommands(...a);
        }
        return this.default(a);
    },
    async default(a) {
        return new Response(
            "Invalid request: Access through discord.", { status: 400 }
        );
    }
}

/**
 * The default exported object which acts as the entrypoint of the worker.
 */
export default {
    async fetch(...a: HandlerArgs): Promise<Response> {
        const meth = a[0].method;
        return (
            meth in routeMap
            ? await routeMap[meth](a)
            : await routeMap.default(a)
        );
    }
};
