`use strict`;

/** 
 * A typed object to describe the data in the environment of workers
 * (like env vars, KV bindings, etc.)
 */
export interface Env {
    DISCORD_APP_ID: BigInt;
    DISCORD_PUB_KEY: string;
    DISCORD_TEST_GUILD_ID: BigInt;
    DISCORD_TOKEN: string;
}