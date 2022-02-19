#!/usr/bin/env python3

"""The main code for the new Ritsu bot written in hikari"""

__author__ = "supershadoe"
__license__ = "Apache v2.0"

import aiohttp
import asyncio
import os
import hikari
import tanjun

import components
from guilds import guilds

if os.name != "nt":
    import uvloop
    uvloop.install()

if __name__ != "__main__":
    raise ImportError("This script isn't intended to be imported!")


async def main() -> None:
    """
    Main function which runs the code
    """

    # Using an async function just for aiohttp to not get DeprecationWarnings
    aiohttp_session = aiohttp.ClientSession()

    client = (
        # Create a tanjun client from GatewayBot
        tanjun.Client.from_gateway_bot(bot, declare_global_commands=guilds)
        # Add a dependency of aiohttp session to reuse the same session for multiple requests
        .set_type_dependency(aiohttp.ClientSession, aiohttp_session)
        # Callback to close the aiohttp session when the bot shuts down
        .add_client_callback(tanjun.ClientCallbackNames.CLOSING, aiohttp_session.close)
    )

    # Custom importing components to later use in load/reload command
    for component in components.__all__:
        client.add_component(getattr(components, component).copy())

    await bot.start(
        activity=hikari.Activity(name="commands", type=hikari.ActivityType.LISTENING))
    await bot.join()

bot = hikari.GatewayBot(os.getenv("BOT_TOKEN"))
loop = asyncio.get_event_loop_policy().get_event_loop()

try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    loop.run_until_complete(bot.close())
