#!/usr/bin/env python3

"""Code snippet to purge all slash commands from global scope and all guilds"""

import asyncio
import hikari
import logging
import os

"""
try:
    from guilds import guilds
except ModuleNotFoundError:
    guilds = []
"""  # Commented out as guild commands aren't being used


async def purge_app_commands() -> None:
    rest_app: hikari.RESTApp = hikari.RESTApp()
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO
    )
    async with rest_app.acquire(os.getenv("BOT_TOKEN"), hikari.TokenType.BOT) as rest_client:
        application: hikari.Application = await rest_client.fetch_application()
        logging.info("Clearing global application commands")
        await rest_client.set_application_commands(application.id, [])

        """
        logging.info("Clearing guild-level application commands")
        for guild in guilds:
            try:
                guild_name = (await rest_client.fetch_guild(guild)).name
            except hikari.ForbiddenError:
                guild_name = "None {Hidden guild}"
            logging.info("    Guild %s of the name %s", guild, guild_name)
            await rest_client.set_application_commands(application.id, [], guild)
        """  # Commented out until I use guild commands again

asyncio.run(purge_app_commands())
