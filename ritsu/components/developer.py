"""Slash commands for some bot-dev commands"""

import hikari
import tanjun

import ritsu.components


@tanjun.as_slash_command("ping", "To check the bot latency", default_to_ephemeral=True)
async def cmd_ping(
        ctx: tanjun.abc.SlashContext, bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot)
) -> None:
    """To reply to a ping command"""

    await ctx.create_initial_response(content=f"Pong!: The latency is **{bot.heartbeat_latency * 1000:.0f} ms**.")


@tanjun.as_slash_command(
    "invite", "To get invite link as this bot is hidden from server list", default_to_ephemeral=True
)
async def cmd_invite(
        ctx: tanjun.abc.SlashContext, bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot)
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


@tanjun.with_owner_check
@tanjun.with_str_slash_option(
    "operation", "What to do with the component?", choices=["Load", "Unload", "Reload"], default="Reload"
)
@tanjun.with_str_slash_option(
    "component_name", "Name of component",
    autocomplete=lambda autocmp_ctx, typed_str: autocmp_ctx.set_choices(
        {component: component for component in ritsu.components.__all__ if typed_str == "" or typed_str in component}
    )
)
@tanjun.as_slash_command("component", "Perform operations on a component", default_to_ephemeral=True)
async def cmd_component(
        ctx: tanjun.abc.SlashContext,
        component_name: str,
        operation: str,
        client: tanjun.Client = tanjun.inject(type=tanjun.Client)
) -> None:
    """Takes care of loading or unloading components in tanjun"""

    if component_name not in ritsu.components.__all__:
        return await ctx.create_initial_response(
            content="No such component exists in this bot! \n Maybe try reloading the bot if this is a new component"
        )

    match operation:
        case "Load":
            try:
                client.add_component(getattr(ritsu.components, component_name).copy())
            except ValueError as err:
                await ctx.create_initial_response(err)
                return
        case "Unload":
            client.remove_component_by_name(component_name)
        case "Reload":
            try:
                client.remove_component_by_name(component_name)
            except KeyError:
                pass
            client.add_component(getattr(ritsu.components, component_name).copy())

    await ctx.create_initial_response(operation + "ed the specified component")


@tanjun.with_owner_check
@tanjun.as_slash_command("shutdown", "To shutdown the bot", default_to_ephemeral=True)
async def cmd_shutdown(
    ctx: tanjun.abc.SlashContext,
    bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot)
) -> None:
    """To shut down the bot"""

    await ctx.create_initial_response("Bye-bye!")
    await bot.close()

comp_developer: tanjun.Component = tanjun.Component(name="comp_developer").load_from_scope()
comp_developer.make_loader()

__all__: tanjun.typing.Final[list[str]] = ['comp_developer']
