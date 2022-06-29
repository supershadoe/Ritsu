"""Handlers for Clash of Clans Component"""

import asyncio
import functools
import typing

import alluka
import hikari
import tanjun

from ritsu.utils.clash_of_clans import (
    add_roles_to_db, drop_guild_from_table, generic_predicate,
    gen_clan_action_row, gen_role_action_row
)


async def _disable_components(
    ctx: tanjun.abc.SlashContext,
    action_row: hikari.api.ActionRowBuilder
) -> None:
    try:
        components = typing.cast(
            typing.Sequence[hikari.impl.InteractiveButtonBuilder],
            action_row.components
        )
        for component in components:
            component.set_is_disabled(True)
        await ctx.edit_last_response(
            component=action_row
        )
    except hikari.NotFoundError:
        pass


async def set_clan_tag_tag_exists(
    ctx: tanjun.abc.SlashContext,
    data: typing.Optional[tuple[str, str]],
    client: tanjun.Client,
    bot: alluka.Injected[hikari.GatewayBot]
) -> bool:
    """
    Used to handle the interaction for when a clan tag already exists in db
    for that particular guild.
    """

    action_row: hikari.api.ActionRowBuilder = gen_clan_action_row(bot)
    predicate_msg: hikari.Message = await ctx.edit_initial_response(
        "This guild already has a clan linked to it.\n"
        f"_{data[0]}: {data[1]}_\n\n"
        "Do you want to erase this and use another clan for this guild?",
        component=action_row
    )

    force_erase_predicate: functools.partial = functools.partial(
        client.injector.call_with_di, generic_predicate,
        ctx, predicate_msg.id, "coc-clan-del-"
    )
    flag: bool = False
    try:
        event: hikari.InteractionCreateEvent = await bot.wait_for(
            hikari.InteractionCreateEvent, timeout=60,
            predicate=force_erase_predicate
        )
        inter = typing.cast(hikari.ComponentInteraction, event.interaction)
        if int(inter.custom_id[-1]):
            flag: bool = True
            await inter.create_initial_response(
                hikari.ResponseType.MESSAGE_UPDATE,
                f"{predicate_msg.content}\n\nTrying to remove it from DB..."
            )
            await client.injector.call_with_async_di(drop_guild_from_table, ctx)
        else:
            await inter.create_initial_response(
                hikari.ResponseType.MESSAGE_UPDATE,
                f"{predicate_msg.content}\n\nOk, not updating it."
            )
    except asyncio.TimeoutError:
        pass
    finally:
        await _disable_components(ctx, action_row)
    return flag


async def create_roles_to_sync_qn(
    ctx: tanjun.abc.SlashContext,
    bot: alluka.Injected[hikari.GatewayBot],
    client: alluka.Injected[tanjun.Client]
) -> None:
    """Ask user if they want to create 4 roles"""

    action_row: hikari.api.ActionRowBuilder = gen_role_action_row(bot)

    await client.injector.call_with_async_di(
        create_roles_to_sync, ctx, await ctx.edit_initial_response(
           "You haven't provided any/all roles to sync. "
           "Do you wish to create 4 new roles for use with this bot?",
           component=action_row
        ), action_row, bot, client
    )


async def handle_create_roles_qn(
    ctx: tanjun.abc.SlashContext,
    bot: alluka.Injected[hikari.GatewayBot],
    client: alluka.Injected[tanjun.Client]
) -> None:
    """Ask user if they want to create roles to sync after setting clan tag"""

    action_row: hikari.api.ActionRowBuilder = gen_role_action_row(bot)
    await client.injector.call_with_async_di(
        create_roles_to_sync, ctx, await ctx.create_followup(
            "Do you want to create roles to link with roles in COC?",
            component=action_row
        ), action_row, bot, client
    )


async def create_roles_to_sync(
    ctx: tanjun.abc.SlashContext,
    predicate_msg: hikari.Message,
    action_row: hikari.api.ActionRowBuilder,
    bot: hikari.GatewayBot,
    client: tanjun.Client,
) -> None:
    create_role_predicate: functools.partial = functools.partial(
        client.injector.call_with_di, generic_predicate,
        ctx, predicate_msg.id, "coc-role-create-"
    )
    try:
        event: hikari.InteractionCreateEvent = await bot.wait_for(
            hikari.InteractionCreateEvent, timeout=60,
            predicate=create_role_predicate
        )
        inter = typing.cast(hikari.ComponentInteraction, event.interaction)
        if int(inter.custom_id[-1]):
            response: str = f"Creating roles..."
            await inter.create_initial_response(
                hikari.ResponseType.MESSAGE_UPDATE,
                f"{predicate_msg.content}\n\n{response}"
            )
            roles: list[int] = []
            for role_name in ("Member", "Elder", "Co-Leader", "Leader"):
                role: hikari.Role = await bot.rest.create_role(
                    ctx.guild_id, name=role_name,
                    reason="For syncing with COC API"
                )
                roles.append(role.id)  # smh asyncpg
            await client.injector.call_with_async_di(
                add_roles_to_db, ctx, roles
            )
            await inter.edit_initial_response(
                f"{predicate_msg.content}\n\n~~{response}~~\nCreated roles!"
            )
        else:
            await inter.create_initial_response(
                hikari.ResponseType.MESSAGE_UPDATE,
                f"{predicate_msg.content}\n\nCancelled creation of roles. "
                "You can use `/coc sync_roles_with_coc` anytime later to create"
                "/to sync roles."
            )
    except asyncio.TimeoutError:
        pass
    finally:
        await _disable_components(ctx, action_row)


async def handle_errors(clan_info: dict, tag: str) -> None:
    """To handle errors from COC API for set_clan_tag command"""
    err: tuple[int, dict] = clan_info["ritsu_error"]
    if err[0] == 404:
        raise tanjun.CommandError(f"User/Clan of tag {tag} Not found")
    elif err[0] == 500:
        raise tanjun.CommandError(
            "Some server error on Supercell's side\n"
            f"Reason provided: {err[1]['reason']}\n"
            f"Message from Supercell: {err[1]['message']}"
        )
    elif err[0] == 503:
        raise tanjun.CommandError(
            "Game is under maintenance. Try again later.\n"
            f"Message: {err[1]['reason']}"
        )
    else:
        raise tanjun.CommandError(
            "Some unknown error has occurred!\n"
            "Try again later or contact the bot developer if the issue persists\n"
            f"HTTP Status: {err[0]}\n"
            f"Response body: ```json\n{err[1]}```"
        )
