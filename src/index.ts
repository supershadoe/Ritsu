`use strict`;

import { Env } from "./env";
import { importPubKey, verify } from "./interactions";

export default {
    async fetch(
        request: Request,
        env: Env,
        ctx: ExecutionContext
    ): Promise<Response> {
        if (request.method == "GET") {
            return new Response(
                "👋 This is supposed to be accessed using discord"
            );
        }
        const pubKey = await importPubKey(env.RITSU_APP_PUB_KEY)
        return verify(pubKey, request)
    },
};
