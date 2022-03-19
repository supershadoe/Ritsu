#!/usr/bin/env python3

"""Code snippet to purge all slash commands from global scope and all guilds"""

import asyncio
import hikari
import os

try:
    from guilds import guilds
except ModuleNotFoundError:
    guilds = []


async def purge_app_commands() -> None:
    rest_app = hikari.RESTApp()
    async with rest_app.acquire(os.getenv("BOT_TOKEN"), hikari.TokenType.BOT) as rest_client:
        application = await rest_client.fetch_application()
        # To remove global commands
        await rest_client.set_application_commands(application.id, [])
        # Loop to remove guild commands
        for guild in guilds:
            await rest_client.set_application_commands(application.id, [], guild)

asyncio.run(purge_app_commands())
