#!/usr/bin/env python3

"""The main code for the new Ritsu bot written in hikari"""

import asyncio
from ritsu.start import start_bot

if __name__ != "__main__":
    raise ImportError("This script isn't intended to be imported!")


async def main() -> None:
    """The main async function to start the bot"""
    await bot.start()
    async with client:
        await bot.join()

bot, client = start_bot()
loop = asyncio.get_event_loop_policy().get_event_loop()
try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    loop.run_until_complete(bot.close())
