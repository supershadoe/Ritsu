"""Helper functions for Wikis component"""

import alluka
import aiohttp
import hikari
import tanjun
import yarl

from ritsu.handlers.wiki import handle_inters


api_links: dict[str, str] = {
    "wikipedia": "https://{}.wikipedia.org/w/api.php",
    "fandom": "https://{}.fandom.com/api.php"
}


async def fetch_article(
    search_term: str,
    command: str,
    subdomain: str,
    session: alluka.Injected[aiohttp.ClientSession]
) -> tuple[list[str], list[str]]:
    """To fetch an article using the MediaWiki API"""

    request_url: yarl.URL = (
        yarl.URL(api_links[command].format(subdomain))
        .with_query(action="opensearch", search=search_term, limit=5)
    )
    async with session.get(request_url) as req:
        # 1 is title, 3 is results
        if req.status == 200:
            data: dict[int, str | list] = await req.json()
            if not data[1]:
                raise tanjun.CommandError(
                    f'No search results found for "{search_term}".'
                )
            return data[1], data[3]
        raise tanjun.CommandError(
            "Some unknown error has occurred!\n"
            "Try again later or contact the bot developer if the issue persists\n"
            f"HTTP Status: {req.status}\n"
            f"Provided reason: ```json\n{req.reason}```"
        )


async def send_initial_resp(
    ctx: tanjun.abc.SlashContext,
    search_term: str,
    bot: alluka.Injected[hikari.GatewayBot],
    injector: alluka.Injected[alluka.Client],
    fandom_name: str = None
) -> None:
    """To send a message with search results from MediaWiki"""

    titles, links = await injector.call_with_async_di(
        fetch_article,
        search_term,
        ctx.command.name,
        "en" if fandom_name is None else fandom_name
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
        (
            "Here's the search result for the requested term.\n"
            f"Direct link: _[Click here]({links[0]})_"
        ),
        component=action_row
    )

    await handle_inters(ctx, links, msg.id, action_row, bot)
