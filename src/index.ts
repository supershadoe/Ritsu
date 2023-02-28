`use strict`;

import { syncCommands } from "./commandSync"
import { handleInteractions } from "./interactions";
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
