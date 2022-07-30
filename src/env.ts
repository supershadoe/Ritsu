`use strict`;

/** 
 * A typed object to describe the data in the environment of workers
 * (like env vars, KV bindings, etc.)
 */
export interface Env {
    RITSU_APP_PUB_KEY: BigInt;
}
