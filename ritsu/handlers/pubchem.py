"""Handlers for commands in pubchem component"""

import typing

import alluka
import hikari
import tanjun
import yarl

from ritsu.utils.pubchem import gen_action_row

hooks = tanjun.SlashHooks()


@hooks.with_on_success
async def handle_inters(
    ctx: tanjun.abc.SlashContext,
    bot: alluka.Injected[hikari.RESTAware],
    action_row: hikari.api.ActionRowBuilder = (
        tanjun.cached_inject(gen_action_row)
    )
) -> None:
    """Callback for a hook to handle interactions after a message"""

    og_msg: hikari.Message = await ctx.fetch_initial_response()
    embed: hikari.Embed = og_msg.embeds[0]

    if embed.title == "Error":
        return

    image_url: yarl.URL = yarl.URL(embed.image.url)
    flag: int = 1
    # For disabling the button even if no interaction was made afterwards by the
    # user

    with bot.stream(hikari.InteractionCreateEvent, timeout=30).filter(
        ("interaction.type", hikari.InteractionType.MESSAGE_COMPONENT),
        ("interaction.component_type", hikari.ComponentType.BUTTON),
        ("interaction.message.id", og_msg.id),
        ("interaction.user", ctx.author),
        lambda e: e.interaction.custom_id.startswith("chem-struct-")
    ) as stream:
        async for event in stream:
            interaction = typing.cast(hikari.ComponentInteraction, event.interaction)
            flag: int = int(interaction.custom_id[-1])
            embed.set_image(str(
                image_url.update_query(record_type=f"{flag + 2}d")
            ))
            buttons = typing.cast(
                typing.Sequence[hikari.api.ButtonBuilder], action_row.components
            )
            buttons[flag ^ 1].set_is_disabled(False)
            buttons[flag].set_is_disabled(True)
            await interaction.create_initial_response(
                response_type=hikari.ResponseType.MESSAGE_UPDATE,
                embed=embed,
                component=action_row
            )
    try:
        action_row.components[flag].set_is_disabled(True)
        await ctx.edit_initial_response(component=action_row)
    except hikari.NotFoundError:
        pass


@hooks.with_on_error
async def handle_errors(ctx: tanjun.abc.SlashContext, err: Exception) -> None:
    """Callback for a hook to handle errors while responding to an interaction"""

    await ctx.respond(
        content="An error occurred while executing the command",
        embed=hikari.Embed(
            title="Error",
            description=err,
            color=0xFF0000
        )
    )
