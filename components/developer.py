"""Slash commands for some bot-dev commands"""

__author__ = "supershadoe"
__license__ = "Apache v2.0"

import hikari
import tanjun
import typing

import components


@tanjun.as_slash_command("ping", "To check the bot latency")
async def cmd_ping(
    ctx: tanjun.abc.SlashContext,
    bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot)
) -> None:
    """To reply to a ping command"""

    await ctx.create_initial_response(embed=(
        hikari.Embed(
            title="Pong",
            color=0xF6CEE7,
            description=f"The latency is **{bot.heartbeat_latency * 1000:.0f} ms**."
        )
    ))


@tanjun.as_slash_command("invite", "To get invite link as this bot is hidden from server list")
async def cmd_invite(
    ctx: tanjun.abc.SlashContext,
    bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot)
) -> None:
    """To invite the bot"""

    await ctx.create_initial_response(
        f"Either click on my profile and click on `Add to Server` or click on the button below!",
        component=(
            bot.rest.build_action_row()
            .add_button(
                hikari.ButtonStyle.LINK,
                f"https://discord.com/api/oauth2/authorize?client_id={bot.get_me().id}&scope=applications.commands"
            )
            .set_label("Invite link")
            .set_emoji("🔗")
            .add_to_container()
        )
    )


async def autocmp_component(
        autocmp_ctx: tanjun.abc.AutocompleteContext,
        typed_str: str
) -> None:
    """Autocomplete function for the cmd_component to fill in with the components in the bot right now"""
    d = {}
    for component in components.__all__:
        if typed_str == "" or typed_str in component:
            d[component] = component
    await autocmp_ctx.set_choices(d)


@tanjun.with_owner_check
@tanjun.with_str_slash_option(
    "operation", "What to do with the component?", choices=["Load", "Unload", "Reload"], default="Reload")
@tanjun.with_str_slash_option("component_name", "Name of component", autocomplete=autocmp_component)
@tanjun.as_slash_command("component", "Perform operations on a component")
async def cmd_component(
    ctx: tanjun.abc.SlashContext,
    operation: str,
    component_name: str,
    client: tanjun.Client = tanjun.inject(type=tanjun.Client)
) -> None:
    """Loads a module into Tanjun client"""

    def err_msgs(err: ValueError, msg: str) -> typing.Awaitable:
        return ctx.create_initial_response(
            content=msg,
            embed=hikari.Embed(title="Error", description=f"`{err}`", color=0xFF0000)
        )

    if component_name not in components.__all__:
        await err_msgs(
            ValueError("No such component exists in this bot!"),
            "Maybe try reloading the bot if this is a new component"
        )

    match operation:
        case "Load":
            try:
                client.add_component(getattr(components, component_name).copy())
                await ctx.create_initial_response("Loaded the specified component!")
            except ValueError as err:
                await err_msgs(err, "Can't load the mentioned component :thinking:")
        case "Unload":
            try:
                client.remove_component_by_name(component_name)
                await ctx.create_initial_response("Unloaded the specified component!")
            except ValueError as err:
                await err_msgs(err, "Can't unload the mentioned component :thinking:")
        case "Reload":
            try:
                client.remove_component_by_name(component_name)
                client.add_component(getattr(components, component_name).copy())
                await ctx.create_initial_response("Reloaded the specified component!")
            except ValueError as err:
                await err_msgs(err, "Can't reload the mentioned component :thinking:")


@tanjun.with_owner_check
@tanjun.as_slash_command("shutdown", "To shutdown the bot")
async def cmd_shutdown(
    ctx: tanjun.abc.SlashContext,
    bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot)
) -> None:
    """To shut down the bot"""

    await ctx.create_initial_response("Bye-bye!")
    await bot.close()

component = tanjun.Component(name="developer").load_from_scope()
component.make_loader()
