import { RouteBases, Routes } from "discord-api-types/v10";
import { Env } from ".";
import * as commands from "./commands";
import { jsonHeaders, jsonResponse } from "./utils";

/**
 * The structure of a client credential access token response sent by Discord
 * if the request is successful.
 */
interface ClientCredAccessTokenResp {
    access_token: string;
    token_type: string;
    expires_in: number;
    scope: string;
};

/**
 * Callback that gets executed on receiving a request at "/sync-cmds".
 *
 * Fetches a bearer token with applications.commands.update scope using client
 * credential grant OAuth2 to update all commands.
 *  
 * @param _req Useless request object.
 * @param env Cloudflare secrets and KV added via wranger/dashboard.
 * @param _ctx The unused ExecutionContext obj sent by Cloudflare.
 * @returns A response as a result of all the functions that run.
 */
export async function syncCommands(
    _req: Request, env: Env, _ctx: ExecutionContext
): Promise<Response> {

    if (! env.TRUSTED_LOCAL_ENV)
        return new Response(
            "This API is supposed to be accessed using discord", { status: 400 }
        );
    if (! (env.RITSU_APP_ID && env.RITSU_CLIENT_SECRET))
        return new Response(
            "Bruh, add app id and client secrets", { status: 500 }
        );

    const app_id = env.RITSU_APP_ID;
    const urlencoded_data = new URLSearchParams({
        client_id: app_id,
        client_secret: env.RITSU_CLIENT_SECRET,
        grant_type: "client_credentials",
        scope: "applications.commands.update"
    });
    const tokenURL = RouteBases.api + Routes.oauth2TokenExchange();

    const request = new Request(tokenURL, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: urlencoded_data
    });
    const response = await fetch(request);
    if ( ! response.ok )
        return jsonResponse(
            {
                "ritsu_error":
                    "Failed to get an OAuth2 Bearer token from Discord to sync"
                    + " commands.",
                "discord_status_code": response.status,
                "discord_status_text": response.statusText,
                "discord_error_body": await response.json()
            },
            { headers: jsonHeaders, status: 500 }
        );
    const body = <ClientCredAccessTokenResp> await response.json();
    return await registerGlobalCommands(app_id, body.access_token);
}

/**
 * The piece of code which actually registers all global commands.
 * 
 * @param app_id The application ID/Client ID.
 * @param access_token The access token obtained from OAuth2.
 * @returns A response to indicate success/failure.
 */
async function registerGlobalCommands(
    app_id: string, access_token: string
): Promise<Response> {
    const commandsURL = RouteBases.api + Routes.applicationCommands(app_id);
    const response = await fetch(commandsURL, {
        method: "PUT",
        headers: { ...jsonHeaders, Authorization: `Bearer ${access_token}` },
        body: JSON.stringify(Object.values(commands))
    });
    if (response.ok)
        return new Response("Registered all global commands!");
    else
        return jsonResponse(
            {
                "ritsu_error": "Failed to register all global commands :(",
                "discord_status_code": response.status,
                "discord_status_text": response.statusText,
                "discord_error_body": await response.json()
            },
            { headers: jsonHeaders, status: 500 }
        );
}
