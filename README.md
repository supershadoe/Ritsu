<a href="https://discord.com/api/oauth2/authorize?client_id=776112201734815786&scope=applications.commands"><img src="https://cdn.discordapp.com/avatars/776112201734815786/b2b1856e81f0b0a1607756a76d1a3851.webp" alt="Bot logo" align="right"/></a>

# Ritsu
**An always-online Discord bot to fetch information from various API**

## Info
- 📄 Licensed under Apache-2.0
- ⚙️ Requires TypeScript 4.9 or 4.9+ (particularly due to use of `satisfies` operator)
- ⚙️ Uses ES modules and not CJS
- 🚀 Minimal amount of dependencies
- 🔶 Powered by [Cloudflare Workers](https://workers.cloudflare.com)
- 🔗 [Bot Invite Link](https://discord.com/api/oauth2/authorize?client_id=776112201734815786&permissions=0&scope=bot%20applications.commands)

## Features
- Searching and fetching articles from Wikipedia.
- Searching and fetching articles from various fandom pages.
- Searching and fetching the details of a compound from PubChem using their PUG API.

## How to run this bot
1. Install `node.js` and `npm`.
2. Clone this repository: `git clone https://github.com/supershadoe/ritsu`.
3. Create a worker in Cloudflare's [dashboard](https://dash.cloudflare.com).
4. Run `npm update` to download all node modules.
5. Set your worker's name and domain/routes in `wrangler.toml`.
6. Login to your Cloudflare account using wrangler: `npx wrangler login`.
7. Run a locally hosted bot for development purposes using `npx wrangler dev` additionally with `--local` if you want to just use miniflare and not connect to a Cloudflare server for using KV and durable objects (this bot doesn't need those right now).
8. Upload the code to run serverlessly on any cloudflare datacenter using `npx wrangler publish`.
