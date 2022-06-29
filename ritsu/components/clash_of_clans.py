"""Slash commands related to the Clash of Clans API"""

import os
import re
import typing

import alluka
import hikari
import tanjun

from ritsu.handlers.clash_of_clans import (
    create_roles_to_sync_qn, handle_create_roles_qn, handle_errors, set_clan_tag_tag_exists
)

from ritsu.utils.clash_of_clans import (
    coc_api, CocApiTokenT, add_clan_to_db, add_roles_to_db, drop_guild_from_table, fetch_coc_info,
    fetch_roles_for_guild, fetch_tag_for_guild
)


cmd_grp: tanjun.SlashCommandGroup = tanjun.slash_command_group(
    "coc", "Commands to access Clash of Clans API"
)


@cmd_grp.with_command
@tanjun.with_author_permission_check(
    hikari.Permissions.MANAGE_GUILD | hikari.Permissions.MANAGE_ROLES,
    error_message="You aren't a mod of this server, are you?"
)
@tanjun.with_own_permission_check(
    hikari.Permissions.MANAGE_ROLES,
    error_message="Bot doesn't have MANAGE_ROLES permission."
)
@tanjun.with_role_slash_option(
    "leader", "The role to assign for the leader",
    default=None, pass_as_kwarg=False
)
@tanjun.with_role_slash_option(
    "co_leader", "The role to assign for co-leaders",
    default=None, pass_as_kwarg=False
)
@tanjun.with_role_slash_option(
    "elder", "The role to assign for elders",
    default=None, pass_as_kwarg=False
)
@tanjun.with_role_slash_option(
    "member", "The role to assign for members",
    default=None, pass_as_kwarg=False
)
@tanjun.as_slash_command(
    "sync_roles_with_coc", "To sync roles in discord with COC",
    always_defer=True
)
async def cmd_sync_roles_with_coc(
    ctx: tanjun.abc.SlashContext,
    client: alluka.Injected[tanjun.Client]
) -> None:

    options = dict.fromkeys(("member", "elder", "co_leader", "elder"))
    options |= ctx.options  # merge both with ctx.options overwriting options

    data: typing.Optional[tuple[str, str]] = (
        await client.injector.call_with_async_di(fetch_tag_for_guild, ctx)
    )
    if data is None:
        raise tanjun.CommandError(
            "Run `/coc set_clan_tag` first and then run this."
        )

    if not all(options.values()):  # if any option doesn't have a value
        data: typing.Optional[list[int]] = await client.injector.call_with_async_di(
            fetch_roles_for_guild, ctx
        )
        if data is None:
            return await client.injector.call_with_async_di(
                create_roles_to_sync_qn, ctx
            )
        else:
            raise tanjun.CommandError("Provide all the 4 roles.")

    msg: str = "Syncing roles to database..."
    await ctx.edit_initial_response(msg)
    await client.injector.call_with_async_di(
        add_roles_to_db, ctx, [
            int(opt.resolve_to_role().id) for opt in options.values() if opt
        ]
    )
    await ctx.edit_initial_response(f"{msg}\nSynced!")


@cmd_grp.with_command
@tanjun.with_cooldown("comp_coc")
@tanjun.with_author_permission_check(
    hikari.Permissions.MANAGE_GUILD,
    error_message="You aren't a mod of this server, are you?"
)
@tanjun.with_str_slash_option("clan_tag", "The tag of your clan")
@tanjun.as_slash_command(
    "set_clan_tag", "To store clan tag for use in other commands"
)
async def cmd_coc_set_clan_tag(
    ctx: tanjun.abc.SlashContext,
    clan_tag: str,
    client: alluka.Injected[tanjun.Client]
) -> None:
    """Command to store clan tag for later use"""

    clan_tag: str = clan_tag.upper()
    if re.match(r"^#[A-Z\d]{9}$", clan_tag) is None:
        raise tanjun.CommandError(
            "Enter a proper clan tag in the format of `#XXXXXXXXX` "
            "(including the #)."
        )
    await ctx.defer()

    data: typing.Optional[tuple[str, str]] = (
        await client.injector.call_with_async_di(fetch_tag_for_guild, ctx)
    )
    if data is not None:
        if data[0] != clan_tag:
            await client.injector.call_with_async_di(
                set_clan_tag_tag_exists, ctx, data, client
            )
        else:
            raise tanjun.CommandError(
                "Hey, this guild is already linked to the provided clan tag!"
            )

    clan_info: dict = await client.injector.call_with_async_di(
        fetch_coc_info, coc_api / "clans" / clan_tag
    )

    if "ritsu_error" in clan_info:
        return await client.injector.call_with_async_di(
            handle_errors, clan_info, clan_tag
        )

    clan_name: str = clan_info["name"]
    await client.injector.call_with_async_di(add_clan_to_db, ctx, clan_name)
    await ctx.edit_initial_response(
        f"Found clan _{clan_name}_ for the tag {clan_tag}!\n"
        "Added the clan to the database!\n\n"
        f"Now, you can use `/coc sync_user user:@{ctx.author.username}` to sync "
        "your clan roles and nickname with this server.",
        components=None
    )
    await client.injector.call_with_async_di(handle_create_roles_qn, ctx)


@cmd_grp.with_command
@tanjun.with_author_permission_check(
    hikari.Permissions.MANAGE_GUILD,
    error_message="You aren't a mod of this server, are you?"
)
@tanjun.as_slash_command(
    "remove_clan_tag", "To remove the clan tag from guild", always_defer=True
)
async def cmd_remove_clan_tag(
    ctx: tanjun.abc.SlashContext,
    client: alluka.Injected[tanjun.Client]
) -> None:
    data: typing.Optional[tuple[str, str]] = (
        await client.injector.call_with_async_di(fetch_tag_for_guild, ctx)
    )
    if data is not None:
        await client.injector.call_with_async_di(drop_guild_from_table, ctx)
        await ctx.edit_initial_response("Removed the clan tag from this guild.")
    else:
        raise tanjun.CommandError("There was no clan tag attached to the guild.")


@cmd_grp.with_command
@tanjun.with_cooldown("comp_coc")
@tanjun.with_own_permission_check(
    hikari.Permissions.MANAGE_ROLES | hikari.Permissions.MANAGE_NICKNAMES,
    error_message=(
        "Bot doesn't have these required permissions: {missing_permissions}"
    )
)
@tanjun.with_str_slash_option("user_tag", "The tag of your COC account")
@tanjun.as_slash_command(
    "sync_user", "To sync discord user with data from COC"
)
async def cmd_sync_user(
    ctx: tanjun.abc.SlashContext,
    user_tag: str,
    client: alluka.Injected[tanjun.Client]
) -> None:
    """Command to sync server nick and role with COC"""

    user_tag: str = user_tag.upper()
    if re.match(r"^#[A-Z\d]{9}$", user_tag) is None:
        raise tanjun.CommandError(
            "Enter a proper user tag in the format of `#XXXXXXXXX` "
            "(including the #)."
        )
    await ctx.defer()

    user_info: dict = await client.injector.call_with_async_di(
        fetch_coc_info, coc_api / "players" / user_tag
    )

    if "ritsu_error" in user_info:
        return await client.injector.call_with_async_di(
            handle_errors, user_info, user_tag
        )

    clan_info: dict[str, typing.Any] = user_info["clan"]
    clan_tag: str = clan_info["tag"]
    clan_name: str = clan_info["name"]
    clan_level: str = clan_info["clanLevel"]
    user_name: str = user_info["name"]
    await ctx.edit_initial_response(
        f"Found clan _{user_name}_ for the tag {user_tag}!\n"
        "Added the clan to the database!\n\n"
        f"Now, you can use `/coc sync_user user:@{ctx.author.username}` to sync "
        "your clan roles and nickname with this server.",
        components=None
    )


comp_coc: tanjun.Component = (
    tanjun.Component(name="Clash of Clans")
    .load_from_scope().add_check(tanjun.checks.GuildCheck())
)


@tanjun.as_loader
def loader_coc(client: tanjun.Client):
    if (token := os.getenv("COC_API_TOKEN")) is not None:
        (
            client.set_type_dependency(CocApiTokenT, token)
            .add_component(comp_coc)
        )


@tanjun.as_unloader
def unloader_coc(client: tanjun.Client):
    (
        client.remove_component_by_name(comp_coc.name)
        .remove_type_dependency(CocApiTokenT)
    )


_all__: typing.Final[tuple[str]] = ("loader_coc",)
