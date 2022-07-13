"""Handlers for commands in Wikis component"""

import typing

import hikari
import tanjun

hooks = tanjun.SlashHooks()


async def handle_inters(
    ctx: tanjun.abc.SlashContext,
    links: list[str],
    msg_id: hikari.Snowflake,
    action_row: hikari.api.ActionRowBuilder,
    bot: hikari.GatewayBot
) -> None:
    """Callback for a hook to handle interactions after a message"""
    with bot.stream(hikari.InteractionCreateEvent, timeout=30).filter(
        ("interaction.type", hikari.InteractionType.MESSAGE_COMPONENT),
        ("interaction.component_type", hikari.ComponentType.SELECT_MENU),
        ("interaction.message.id", msg_id),
        ("interaction.user", ctx.author)
    ) as stream:
        async for event in stream:
            inter = typing.cast(hikari.ComponentInteraction, event.interaction)
            i = int(inter.values[0])
            await event.interaction.create_initial_response(
                hikari.ResponseType.MESSAGE_UPDATE,
                (
                    "Here's the search result for the requested term."
                    f"[​]({links[i]})"
                )
            )
    try:
        action_row.components[0].set_is_disabled(True)
        await ctx.edit_initial_response(component=action_row)
    except hikari.NotFoundError:
        pass


@hooks.with_on_error
async def handle_errors(_: tanjun.abc.SlashContext, err: Exception) -> None:
    """Callback for a hook to handle errors while responding to interactions"""
    raise tanjun.CommandError(
        content="An error occurred while executing the command",
        embed=hikari.Embed(
            title="Error",
            description=err,
            color=0xFF0000
        )
    )
