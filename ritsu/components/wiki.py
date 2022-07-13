"""Slash commands for searching wikis"""

import alluka
import hikari
import tanjun

from ritsu.handlers.wiki import handle_inters, hooks
from ritsu.utils.wiki import fetch_article


@hooks.add_to_command
@tanjun.with_str_slash_option("search_term", "Term to search for")
@tanjun.as_slash_command(
    "wikipedia", "Search for any article from wikipedia", always_defer=True
)
async def cmd_wikipedia(
    ctx: tanjun.abc.SlashContext,
    search_term: str,
    bot: alluka.Injected[hikari.GatewayBot],
    injector: alluka.Injected[alluka.Client]
) -> None:
    titles, links = await injector.call_with_async_di(
        fetch_article, search_term
    )

    action_row: hikari.api.ActionRowBuilder = bot.rest.build_action_row()
    select_menu: hikari.api.SelectMenuBuilder = (
        action_row.add_select_menu("wiki-search")
        .set_min_values(1)
        .set_placeholder("Select another article")
    )
    for index, title in enumerate(titles):
        select_menu.add_option(title, f"{index}").add_to_menu()
    select_menu.add_to_container()

    msg = await ctx.respond(
        f"Here's the search result for the requested term.[​]({links[0]})",
        component=action_row
    )

    await handle_inters(ctx, links, msg.id, action_row, bot)


loader_wiki: tanjun.abc.ClientLoader = (
    tanjun.Component(name="Wikis").load_from_scope().make_loader()
)
