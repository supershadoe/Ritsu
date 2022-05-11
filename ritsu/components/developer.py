"""Slash commands for some bot-dev commands"""

import alluka
import hikari
import tanjun

import ritsu.components


@tanjun.as_slash_command("ping", "To check the bot latency", default_to_ephemeral=True)
async def cmd_ping(ctx: tanjun.abc.SlashContext, bot: alluka.Injected[hikari.GatewayBot]) -> None:
    """To reply to a ping command"""

    await ctx.create_initial_response(content=f"Pong!: The latency is **{bot.heartbeat_latency * 1000:.0f} ms**.")


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
@tanjun.as_slash_command("component", "To modify bot's components at runtime", default_to_ephemeral=True)
async def cmd_component(
    ctx: tanjun.abc.SlashContext, component_name: str, operation: str, client: alluka.Injected[tanjun.Client]
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


comp_developer: tanjun.Component = tanjun.Component(name="comp_developer").load_from_scope()
comp_developer.make_loader()

__all__: tanjun.typing.Final[list[str]] = ['comp_developer']
