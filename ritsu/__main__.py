#!/usr/bin/env python3

"""The main code for the new Ritsu bot written in hikari"""

if __name__ != "__main__":
    raise ImportError("This script isn't intended to be imported!")

import aiohttp
import asyncio
import os
import hikari
import tanjun

import ritsu.components as components

if os.name != "nt":
    import uvloop
    uvloop.install()


async def main() -> None:
    """
    Main function which runs the code

    This asynchronous function is a blocking function which is defined due to aiohttp
    requiring an asyncio event loop for creating a session
    """

    aiohttp_session: aiohttp.ClientSession = aiohttp.ClientSession()

    client: tanjun.Client = (
        tanjun.Client.from_gateway_bot(bot, declare_global_commands=True)
        .set_type_dependency(aiohttp.ClientSession, aiohttp_session)
        .add_client_callback(tanjun.ClientCallbackNames.CLOSING, aiohttp_session.close)
    )

    # Custom importing components to later use in load/reload command
    for component in components.__all__:
        client.add_component(getattr(components, component).copy())

    await bot.start(activity=hikari.Activity(name="commands", type=hikari.ActivityType.LISTENING))
    await bot.join()

bot: hikari.GatewayBot = hikari.GatewayBot(os.getenv("BOT_TOKEN"))
loop: asyncio.AbstractEventLoop = asyncio.get_event_loop_policy().get_event_loop()

try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    loop.run_until_complete(bot.close())
