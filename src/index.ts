`use strict`;

import { Router } from "itty-router";
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
}

const router = Router();
router
    .get("/sync-cmds", syncCommands)
    .get("*", (..._args) => new Response(
        "This API is supposed to be accessed using discord", { status: 400 }
    ))
    .post("*", checkForSigAndTS, verifySig, handleInteractions)
    .all("*", (..._args) => new Response(
        /*
        * 501 imo means more like a proper request but I haven't implemented it
        * server-side while 400 is just a bad request... An issue on the part of
        * user.
        */
        "Not something that I was designed to do", { status: 400 }
    ))
    ;

export default { fetch: router.handle };
