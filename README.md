<a href="https://discord.com/api/oauth2/authorize?client_id=776112201734815786&scope=applications.commands"><img src="https://cdn.discordapp.com/avatars/776112201734815786/b2b1856e81f0b0a1607756a76d1a3851.webp" alt="Bot logo" align="right"/></a>

# Ritsu

**An always-online Discord bot to fetch information from various API**

## Info

- 📄 Licensed under Apache-2.0
- 🔶 Powered by [Cloudflare Workers](https://workers.cloudflare.com)
- 🔗 [Bot Invite Link](https://discord.com/api/oauth2/authorize?client_id=776112201734815786&permissions=0&scope=bot%20applications.commands)

## Features

- Searching and fetching articles from Wikipedia.
- Searching and fetching articles from various fandom pages.
- Searching and fetching the details of a compound from PubChem using their PUG API.

## Development notes

### Setup

1. Install `node.js` and `npm`.
2. Clone this repository: `git clone https://github.com/supershadoe/ritsu`.
3. Create a worker in Cloudflare's [dashboard](https://dash.cloudflare.com).
4. Run `npm install` to download all node modules.
5. Set your worker's name and domain/routes in `wrangler.toml`.
6. Generate types for the project using `npx wrangler types`.
7. Copy `.dev.vars.example` to `.dev.vars` and set the values specific
   to your bot.
8. Run the bot locally using `npx wrangler dev`.

### How to sync commands with discord

1. Start the development server using `npx wrangler dev`.
2. Go to the `/sync-cmds` route on the local server.
3. The commands should have synced with Discord after credential grant.

### Deployment

1. Login to your Cloudflare account using wrangler: `npx wrangler login`.
2. Bundle and upload the code using `npx wrangler deploy`.
