"""Handlers for commands in subsplease component"""

import alluka
import hikari
import tanjun

from ritsu.utils.subsplease import (
    fetch_schedule, gen_schedule_embed, gen_action_row
)

hooks = tanjun.SlashHooks()


@hooks.with_on_success
async def handle_inters(
    ctx: tanjun.abc.SlashContext,
    bot: alluka.Injected[hikari.GatewayBot],
    schedule: dict = tanjun.cached_inject(fetch_schedule, expire_after=300),
    action_row: hikari.api.ActionRowBuilder = (
        tanjun.cached_inject(gen_action_row)
    )
) -> None:
    """Callback for a hook to handle interactions after a message"""
    with bot.stream(hikari.InteractionCreateEvent, timeout=30).filter(
        ("interaction.type", hikari.InteractionType.MESSAGE_COMPONENT),
        ("interaction.component_type", hikari.ComponentType.SELECT_MENU),
        ("interaction.message.id", (await ctx.fetch_initial_response()).id),
        ("interaction.user", ctx.author)
    ) as stream:
        async for event in stream:
            await event.interaction.create_initial_response(
                response_type=hikari.ResponseType.MESSAGE_UPDATE,
                embed=gen_schedule_embed(
                    schedule, event.interaction.values[0]
                )
            )
    try:
        action_row.components[0].set_is_disabled(True)
        await ctx.edit_initial_response(component=action_row)
    except hikari.NotFoundError:
        pass


@hooks.with_on_error
async def handle_errors(ctx: tanjun.abc.SlashContext, err: Exception) -> None:
    """Callback for a hook to handle errors while responding to interactions"""
    await ctx.respond(
        content="An error occurred while executing the command",
        embed=hikari.Embed(
            title="Error",
            description=err,
            color=0xFF0000
        )
    )
