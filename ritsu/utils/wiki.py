"""Helper functions for Wikis component"""

import alluka
import aiohttp
import tanjun
import yarl


async def fetch_article(
    search_term: str,
    session: alluka.Injected[aiohttp.ClientSession]
) -> tuple[list[str], list[str]]:
    request_url: yarl.URL = (
        yarl.URL("https://en.wikipedia.org/w/api.php")
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
