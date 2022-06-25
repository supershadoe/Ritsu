<a href="https://discord.com/api/oauth2/authorize?client_id=776112201734815786&scope=applications.commands"><img src="https://cdn.discordapp.com/avatars/776112201734815786/b2b1856e81f0b0a1607756a76d1a3851.webp" alt="Bot logo" align="right"/></a>

# Ritsu
**A discord bot to fetch information from various API**

<a href="https://apache.org/licenses/LICENSE-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue" alt="License: Apache" align="right" /></a>
<a href="https://canary.discord.com/api/oauth2/authorize?client_id=776112201734815786&permissions=0&scope=bot%20applications.commands"><img src="https://img.shields.io/badge/Bot%20Invite-Link-blue" alt="Bot invite link" align="right" /></a>

<img src="https://img.shields.io/badge/Python-3.10+-green" alt="Python >=3.10" align="left" />
<hr />

## Note
The bot isn't maintained on a regular basis and also in a very alpha stage so
code that works today may not work tomorrow.

## How to run this bot
1. Clone this repository
2. Add your bot's token to an environment variable called `BOT_TOKEN_PROD`
3. Also, setup a virtualenv and install dependencies from `requirements.txt`
4. Run `python -m ritsu`

## Features
- Fetching the details of a compound from PubChem using their PUG API
- Fetching release schedule of SubsPlease using their API
- More to come

(very niche stuff ik)

## FAQ
### Why aren't you using a RESTBot?
Because I can't get a domain name right now to add to discord as interaction
server.
### Will there be more features coming up?
Yeah, but not soon. Can't promise when or what.
### Why is the code Python (>=3.10)?
Because it would be annoying to use `typing.Union[T1, T2]` instead of
`T1 | T2`.

