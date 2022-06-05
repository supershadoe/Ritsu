"""
Slash commands for using subsplease API

Disclaimer: This code only provides a way to communicate with the API of
subsplease site. Procuring anime using the information from this bot is totally
the act of the user and does not concern the bot or the bot's author in anyway.
"""

import datetime

import hikari
import tanjun

from handlers.subsplease import hooks
from utils.subsplease import (
    days_of_week, fetch_schedule, gen_schedule_embed, gen_action_row
)

cmd_grp: tanjun.SlashCommandGroup = tanjun.slash_command_group(
    "subsplease", "Commands to access subsplease API"
)

@hooks.add_to_command
@cmd_grp.with_command
@tanjun.with_str_slash_option(
    "day_of_week", "Day of week to fetch schedule for",
    choices = days_of_week,
    default=days_of_week[datetime.date.today().weekday()]
)
@tanjun.as_slash_command(
    "schedule", "Shows release schedule of Subsplease", always_defer=True
)
async def cmd_schedule(
    ctx: tanjun.abc.SlashContext,
    day_of_week: str,
    schedule: dict = tanjun.cached_inject(fetch_schedule, expire_after=300),
    action_row: hikari.api.ActionRowBuilder = (
        tanjun.cached_inject(gen_action_row)
    )
) -> None:
    "The main slash command function for fetching latest schedule"

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

comp_subsplease: tanjun.Component = (
    tanjun.Component(name="comp_subsplease").load_from_scope()
)
comp_subsplease.make_loader()

__all__: tanjun.typing.Final[list[str]] = ["comp_subsplease"]
