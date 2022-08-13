import { Env } from ".";
import * as commands from "./commands";
import { jsonResponse } from "./utils";

interface ClientCredAccessTokenResp {
    access_token: string;
    token_type: string;
    expires_in: number;
    scope: string;
}

class RegisteringError extends Error {}

async function registerCommands(app_id: string, access_token: string) {
    //TODO jsdoc + func for global and guild commands
    //Also first fetch commands and then update (ref 1.1.1.1 bot)
    const commandsURL =
        `https://discord.com/api/v10/applications/${app_id}/commands`;
    const response = await fetch(commandsURL, {
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${access_token}`
        },
        method: "PUT",
        body: JSON.stringify(Object.values(commands))
    });
    const text = await response.text();
    if (response.ok) {
        console.log("Registered all commands!");
    } else {
        console.log(`Error while registering commands for ${commandsURL}`)
        throw new RegisteringError(text)
    }
    return {}
}

export async function syncCommands(
    _req: Request, env: Env, _ctx: ExecutionContext
) {

    /** Base64-encoded credentials for HTTP Basic Authentication */
    const app_id = env.RITSU_APP_ID;
    const client_creds = btoa(`${app_id}:${env.RITSU_CLIENT_SECRET}`);

    /** {"grant_type":"client_credentials","scope":"identify"} */
    const urlencoded_data = (
        "%7B%22grant_type%22%3A%22client_credentials%22%2C"
        + "%22scope%22%3A%22identify%22%7D"
    );

    return await fetch(new Request("https://discord.com/api/v10/oauth2/token"),
        {
            method: "POST",
            headers: {
                "Authentication": `Basic ${client_creds}`,
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: urlencoded_data
        }
    ).then((response: Response) => {
        if (!response.ok) {
            return new Response(
                `Failed to get an OAuth2 Bearer token from Discord to sync commands. (${response.status})`,
                { status: 401 }
            )
        }
    })?.then(async (response?: Response) => {
        const body = <ClientCredAccessTokenResp> await response?.json()
        return jsonResponse(await registerCommands(app_id, body.access_token))
    })
}
