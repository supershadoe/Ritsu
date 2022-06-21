"""
Slash commands for using subsplease API

Disclaimer: This code only provides a way to communicate with the API of
subsplease site. Procuring anime using the information from this bot is totally
the act of the user and does not concern the bot or the bot's author in any way.
"""

import datetime
from typing import Any, Final, ItemsView

import hikari
import tanjun

from ritsu.handlers.subsplease import hooks
from ritsu.utils.subsplease import (
    days_of_week, fetch_schedule, gen_schedule_embed, gen_action_row
)

cmd_grp: tanjun.SlashCommandGroup = tanjun.slash_command_group(
    "subsplease", "Commands to access subsplease API"
)


@hooks.add_to_command
@cmd_grp.with_command
@tanjun.with_str_slash_option(
    "day_of_week", "Day of week to fetch schedule for",
    choices=days_of_week,
    default=days_of_week[datetime.date.today().weekday()]
)
@tanjun.as_slash_command(
    "schedule", "Shows release schedule of Subsplease", always_defer=True
)
async def cmd_schedule(
    ctx: tanjun.abc.SlashContext,
    day_of_week: str,
    schedule: ItemsView | tuple[str, tuple[int, Any]] = tanjun.cached_inject(fetch_schedule, expire_after=300),
    action_row: hikari.api.ActionRowBuilder = (
        tanjun.cached_inject(gen_action_row)
    )
) -> None:
    """The main slash command function for fetching latest schedule"""

    if "ritsu_error" in schedule:
        err: tuple = schedule["ritsu_error"]
        five_mins: int = int(datetime.datetime.timestamp(
            datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        ))
        await ctx.edit_initial_response(
            embed=hikari.Embed(
                title="Error",
                description=f"_{0}: {1}_".format(*err),
                color=0xFF0000
            ),
            content=(
                "Oh no! An error has occurred while trying to fetch the "
                f"required data! :fearful:\nTry <t:{five_mins}:R> later "
                ":pensive:\n\n_Or contact the bot developer for debugging_"
            )
        )
        return

    await ctx.edit_initial_response(
        "Here's the release schedule of SubsPlease.",
        embed=gen_schedule_embed(schedule, day_of_week),
        component=action_row
    )


@hooks.add_to_command
@cmd_grp.with_command
@tanjun.with_str_slash_option(
    "resolution", "Select the resolution to use",
    choices=("480p", "720p", "1080p")
)
@tanjun.with_str_slash_option("anime_name", "The name of the anime")
@tanjun.as_slash_command(
    "episode", "Fetch information about a particular episode of an anime"
)
async def cmd_episode(
    ctx: tanjun.abc.SlashContext,
    anime_name: str,
    resolution: str
) -> None:
    """Command to fetch information about a particular episode of an anime"""

    raise tanjun.CommandError("Not yet implemented")


@hooks.add_to_command
@cmd_grp.with_command
@tanjun.with_str_slash_option("anime_name", "The name of anime to subscribe to")
@tanjun.as_slash_command(
    "subscribe",
    "Subscribe to notifications of an ongoing anime available on subsplease"
)
async def cmd_subscribe(
    ctx: tanjun.abc.SlashContext,
    anime_name: str
) -> None:
    """Command to subscribe to notifications of an ongoing anime"""

    raise tanjun.CommandError("Not yet implemented")


@hooks.add_to_command
@cmd_grp.with_command
@tanjun.with_str_slash_option(
    "anime_name", "The name of anime to unsubscribe from", choices=['1', '2']
)
@tanjun.as_slash_command(
    "unsubscribe",
    "Unsubscribe from notifications for an ongoing anime available on "
    "subsplease"
)
async def cmd_unsubscribe(
    ctx: tanjun.abc.SlashContext,
    anime_name: str
) -> None:
    """Command to unsubscribe from notifications of an ongoing anime"""

    raise tanjun.CommandError("Not yet implemented")

loader_subsplease: tanjun.abc.ClientLoader = (
    tanjun.Component(name="Subsplease").load_from_scope().make_loader()
)

__all__: Final[list[str]] = ["loader_subsplease"]
