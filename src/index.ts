`use strict`;

import { Router } from "itty-router";
import { handleInteractions } from "./interactions";
import { importPubKey, verify } from "./verifyInter";

/** 
 * A typed object to describe the data in the environment of workers
 * (like env vars, KV bindings, etc.)
 */
 export interface Env {
    RITSU_APP_PUB_KEY: string;
}

const router = Router();
router
    .get("*", () => new Response(
        "This API is supposed to be accessed using discord", { status: 400 }
    ))
    .all("*", () => new Response(
        /*
        * 501 imo means more like a proper request but I haven't implemented it
        * server-side while 400 is just a bad request... An issue on the part of
        * user.
        */
        "Not something that I was designed to do", { status: 400 }
    ))
    .post("*", processPOST) // Won't work
    ;

async function processPOST(request: Request, publicKey: string): Promise<Response> {

    const url = new URL(request.url);
    switch(url.pathname) {
        case "/generate-admin-token":
        case "/sync-cmds":
            const auth = request.headers.get("Authentication");
            return new Response(
                `Processing request to sync commands.
                Try not to run this endpoint multiple times to not get ratelimited.`,
                { status: 200 }
            );
        default:
            const pubKey = await importPubKey(publicKey);
            const signature = request.headers.get("X-Signature-ED25519");
            const timestamp = request.headers.get("X-Signature-Timestamp");
            const body = await request.text();
            if ( ! (signature && timestamp) ) {
                return new Response(
                    "Missing signature and timestamp for verification",
                    { status: 401 }
                );
            }
            const isVerified = await verify(pubKey, signature, timestamp, body)
            if (!isVerified) {
                return new Response(
                    "Received a request with invalid signature", { status: 401 }
                );
            }

            try {
                const json = JSON.parse(body);
                return handleInteractions(json);
            }
            catch (e) {
                if (!(e instanceof SyntaxError)) { throw e; }
                return new Response("Malformed JSON body", { status: 400 });
            }
    }
}


export default {
    async fetch(
        request: Request,
        env: Env,
        _: ExecutionContext
    ): Promise<Response> {
        return router.handle(request, env.RITSU_APP_PUB_KEY);
    }
};
