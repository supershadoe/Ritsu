#!/usr/bin/env python3

"""Code snippet to purge messages from some channel"""

import asyncio
import hikari
import os


channel_id = int(input("Channel ID: "))
no_of_msgs = int(input("No of Messages to purge: "))


async def purge_messages() -> None:
    rest_app = hikari.RESTApp()
    async with rest_app.acquire(os.getenv("BOT_TOKEN"), hikari.TokenType.BOT) as rest_client:
        iterator = rest_client.fetch_messages(channel_id).limit(no_of_msgs)
        async for messages in iterator.chunk(100):
            await rest_client.delete_messages(channel_id, messages)


asyncio.run(purge_messages())
