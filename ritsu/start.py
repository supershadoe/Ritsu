"""Code to initialize the discord bot"""

import os

import aiohttp
import alluka
import asyncpg
import hikari
import tanjun

import components

if os.name != "nt":
    import uvloop

async def tasks_startup(client: alluka.Injected[tanjun.Client]) -> None:
    """Tasks to execute while the bot starts up"""
    http_s: aiohttp.ClientSession = aiohttp.ClientSession()
    # Check why adding password here doesn't work (nor does psql ask for pwd)
    db_conn: asyncpg.Connection = await asyncpg.connect(
        "postgresql://ritsu:@localhost/ritsu_db"
    )
    (
        client.set_type_dependency(aiohttp.ClientSession, http_s)
        .set_type_dependency(asyncpg.Connection, db_conn)
    )


async def tasks_shutdown(
    client: alluka.Injected[tanjun.Client],
    http_s: alluka.Injected[aiohttp.ClientSession],
    db_conn: alluka.Injected[asyncpg.Connection]
) -> None:
    """Tasks to execute while the bot shuts down"""
    await http_s.close()
    await db_conn.close()
    (
        client.remove_type_dependency(aiohttp.ClientSession)
        .remove_type_dependency(asyncpg.Connection)
    )

def start_bot() -> tuple[hikari.GatewayBot, hikari.Activity]:
    """Function to start discord bot"""

    if "uvloop" in dir():
        uvloop.install()

    bot: hikari.GatewayBot = hikari.GatewayBot(
        os.getenv("BOT_TOKEN_TEST") or os.getenv("BOT_TOKEN_PROD")
    )

    client: tanjun.Client = (
        tanjun.Client.from_gateway_bot(bot, declare_global_commands=True)
        .add_client_callback(tanjun.ClientCallbackNames.STARTING, tasks_startup)
        .add_client_callback(tanjun.ClientCallbackNames.CLOSING, tasks_shutdown)
    )

    for component in components.__all__:
        client.add_component(getattr(components, component))

    activity: hikari.Activity =hikari.Activity(
        name="commands", type=hikari.ActivityType.LISTENING
    )

    return bot, activity
