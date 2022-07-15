"""Code to initialize the discord bot"""

import os
import typing

import alluka
import hikari
import tanjun

import ritsu.dependencies as deps
from ritsu.dependency import DependencyProto
from ritsu.handlers.common import ComponentInteractionHandler

if os.name != "nt":
    import uvloop


async def tasks_startup(client: alluka.Injected[tanjun.Client]) -> None:
    """Tasks to execute while the bot starts up"""

    for dep in deps.__all__:
        dependency: DependencyProto = typing.cast(
            DependencyProto, getattr(deps, dep)
        )
        await client.injector.call_with_async_di(dependency.loader)


async def tasks_shutdown(client: alluka.Injected[tanjun.Client]) -> None:
    """Tasks to execute while the bot shuts down"""
    for dep in deps.__all__:
        dependency: DependencyProto = typing.cast(
            DependencyProto, getattr(deps, dep)
        )
        await client.injector.call_with_async_di(dependency.unloader)


def start_bot() -> tuple[hikari.RESTBot, tanjun.Client]:
    """Function to start discord bot"""

    if "uvloop" in dir():
        uvloop.install()

    bot: hikari.RESTBot = hikari.RESTBot(
        os.getenv("BOT_TOKEN_TEST") or os.getenv("BOT_TOKEN_PROD"),
        hikari.TokenType.BOT
    )

    client: tanjun.Client = (
        tanjun.Client.from_rest_bot(bot, declare_global_commands=True)
        .add_client_callback(tanjun.ClientCallbackNames.STARTING, tasks_startup)
        .add_client_callback(tanjun.ClientCallbackNames.CLOSING, tasks_shutdown)
        .load_modules("ritsu.components")
    )
    bot.set_listener(hikari.ComponentInteraction, ComponentInteractionHandler())

    return bot, client
