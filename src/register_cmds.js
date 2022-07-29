`use strict`;

import * as commands from "./commands.js"
import fetch from "node-fetch"

const appToken = process.env.RITSU_APP_TOKEN_TEST ||
    process.env.RITSU_APP_TOKEN_PROD;
const appID = process.env.RITSU_APP_ID;
const guildIDs = process.env.RITSU_APP_GUILD_IDS;
var jsonGuilds = null;
if (guildIDs) { jsonGuilds = JSON.parse(guildIDs) }

if (!appID) {
    throw new Error("RITSU_APP_ID env var is required!")
}
if (!appToken) {
    throw new Error(
        "RITSU_APP_TOKEN_[TEST | PROD] is required!"
    )
}

function registerGuildCommands() {
    if (!Array.isArray(jsonGuilds)) {
        throw new SyntaxError(
            "Guild IDs should be an array of BigInts (guild IDs)"
        );
    }
    jsonGuilds.forEach(async (guild) => {
        const url = `https://discord.com/api/v10/applications/${appID}/guilds/${guild}/commands`;
        try {
            const responseText = await registerCommands(url)
            const json = JSON.parse(responseText)
            json.forEach(async (cmd) => {
            const response = await fetch(`${url}/${cmd.id}`);
            if (!response.ok) {
                console.error("Problem receiving command ${cmd.id}")
            }
        });
        } catch (e) {
            if (!(e instanceof RegisteringError)) { throw e; }
            console.error(e.message)
        }
    });
}

class RegisteringError extends Error {}

async function registerGlobalCommands() {
    const url = `https://discord.com/api/v10/applications/${appID}/commands`;
    await registerCommands(url)
}

async function registerCommands(url) {
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bot ${appToken}`
        },
        method: "PUT",
        body: JSON.stringify(Object.values(commands))
    });
    const text = await response.text();

    if (response.ok) {
        console.log("Registered all commands!");
    } else {
        console.log(`Error while registering commands for ${url}`)
        throw new RegisteringError(text)
    }
    return text
}

await registerGlobalCommands();
// registerGuildCommands();
