`use strict`;

import { Router } from "itty-router";
import { handleInteractions } from "./interactions";
import { checkForSigAndTS, verifySig } from "./verifyInter";

/** 
 * A typed object to describe the data in the environment of workers
 * (like env vars, KV bindings, etc.)
 */
 export interface Env {
    RITSU_APP_PUB_KEY: string;
}

const router = Router();
router
    .get("*", (..._args) => new Response(
        "This API is supposed to be accessed using discord", { status: 400 }
    ))
    .all("*", (..._args) => new Response(
        /*
        * 501 imo means more like a proper request but I haven't implemented it
        * server-side while 400 is just a bad request... An issue on the part of
        * user.
        */
        "Not something that I was designed to do", { status: 400 }
    ))
    .post("/generate-admin-token", () => new Response("test")) // TODO
    .post("/sync-cmds", (request: Request, env: Env, _: ExecutionContext) => {
        const auth = request.headers.get("Authentication"); // TODO
        return new Response(
            `Processing request to sync commands.
            Try not to run this endpoint multiple times to not get ratelimited.`,
            { status: 200 }
        );
    })
    .post("*", checkForSigAndTS, verifySig, handleInteractions)
    ;

export default { fetch: router.handle };
