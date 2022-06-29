"""Helper functions for Clash of Clans component"""

import typing

import aiohttp
import alluka
import asyncpg
import hikari
import tanjun
import yarl

CocApiTokenT = typing.NewType("CocApiTokenT", str)
coc_api: yarl.URL = yarl.URL("https://api.clashofclans.com/v1")


async def fetch_coc_info(
    url: yarl.URL,
    session: alluka.Injected[aiohttp.ClientSession],
    token: alluka.Injected[CocApiTokenT]
) -> dict[str, typing.Any]:
    """To fetch anything from COC API"""
    headers: dict[str, str] = {"Authorization": f"Bearer {token}"}
    async with session.get(url, headers=headers) as req:
        if req.status == 200:
            return await req.json()
        else:
            return {"ritsu_error": (req.status, await req.json())}


async def add_clan_to_db(
    ctx: tanjun.abc.SlashContext,
    clan_name: str,
    db_conn: alluka.Injected[asyncpg.Connection]
) -> None:
    """To add a clan to db for later use"""
    if db_conn is not None:
        await db_conn.execute(
            """
            INSERT INTO clan_info(guild_id, clan_tag, clan_name)
            VALUES ($1, $2, $3);
            """,
            ctx.guild_id, ctx.options["clan_tag"].string().upper(), clan_name
        )
    else:
        raise tanjun.CommandError(
            "Cannot add Clan to database due to being unable to connect to it."
            "\nTry again later."
        )


async def add_roles_to_db(
    ctx: tanjun.abc.SlashContext,
    roles: list[int],
    db_conn: alluka.Injected[asyncpg.Connection]
) -> None:
    if db_conn is not None:
        await db_conn.execute(
            "UPDATE clan_info SET roles=$1 WHERE guild_id=$2;",
            roles, ctx.guild_id
        )
    else:
        raise tanjun.CommandError(
            "Cannot add roles to database due to being unable to connect to it"
            ".\nTry again later."
        )


async def fetch_roles_for_guild(
    ctx: tanjun.abc.SlashContext,
    db_conn: alluka.Injected[asyncpg.Connection]
) -> typing.Optional[list[int]]:
    """To return a list of roles stored for a guild"""
    if db_conn is not None:
        row: tuple[list[int]] = await db_conn.fetchrow(
            "SELECT roles FROM clan_info WHERE guild_id=$1",
            ctx.guild_id
        )
        if row is not None:
            return row[0]
    else:
        raise tanjun.CommandError(
            "The database isn't online and thus, can't fetch the data required."
        )


async def fetch_tag_for_guild(
    ctx: tanjun.abc.SlashContext,
    db_conn: alluka.Injected[asyncpg.Connection]
) -> typing.Optional[tuple[str, str]]:
    """To check if a clan exists in database already"""
    if db_conn is not None:
        return await db_conn.fetchrow(
            "SELECT clan_tag, clan_name FROM clan_info WHERE guild_id=$1",
            ctx.guild_id
        )
    else:
        raise tanjun.CommandError(
            "The database isn't online and thus, can't fetch the data required."
        )


async def drop_guild_from_table(
    ctx: tanjun.abc.SlashContext,
    db_conn: alluka.Injected[asyncpg.Connection]
) -> None:
    """To drop a guild from table"""
    if db_conn is not None:
        await db_conn.execute(
            "DELETE FROM clan_info WHERE guild_id=$1", ctx.guild_id
        )
    else:
        raise tanjun.CommandError(
            "The database isn't online and thus, can't perform the reqd task."
        )


def generic_predicate(
    ctx: tanjun.abc.SlashContext,
    msg_id: int,
    custom_id: str,
    event: hikari.InteractionCreateEvent
) -> bool:
    """
    A generic predicate used to check for interactions with the buttons
    """
    i: hikari.PartialInteraction = event.interaction
    return all((
        i.type is hikari.InteractionType.MESSAGE_COMPONENT,
        i.component_type is hikari.ComponentType.BUTTON,
        i.message.id == msg_id,
        i.user == ctx.author,
        i.custom_id.startswith(custom_id)
    ))


def gen_clan_action_row(bot: hikari.GatewayBot) -> hikari.api.ActionRowBuilder:
    """Generator for action_row to show in predicate_msg"""
    return (
        bot.rest.build_action_row()
        .add_button(hikari.ButtonStyle.DANGER, "coc-clan-del-1")
        .set_emoji("🗑")
        .set_label("Change clan anyway")
        .add_to_container()
        .add_button(hikari.ButtonStyle.PRIMARY, "coc-clan-del-0")
        .set_emoji("✅")
        .set_label("Cancel")
        .add_to_container()
    )


def gen_role_action_row(bot: hikari.GatewayBot) -> hikari.api.ActionRowBuilder:
    """Generator for action_row to show in predicate_msg"""
    return (
        bot.rest.build_action_row()
        .add_button(hikari.ButtonStyle.SUCCESS, "coc-role-create-1")
        .set_emoji("✅")
        .set_label("Create 4 roles")
        .add_to_container()
        .add_button(hikari.ButtonStyle.PRIMARY, "coc-role-create-0")
        .set_emoji("❌")
        .set_label("Cancel")
        .add_to_container()
    )
