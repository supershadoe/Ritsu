"""Helper functions for subsplease component"""

import aiohttp
import alluka
import hikari

days_of_week: tuple[str, ...] = (
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
)

async def fetch_schedule(
    session: alluka.Injected[aiohttp.ClientSession]
) -> dict:
    """Async function to fetch the latest release schedule from subsplease"""

    subsplease_url: str = "https://subsplease.org/api/?f=schedule&tz=UTC"
    async with session.get(subsplease_url) as req:
        if req.status == 200:
            return (await req.json(content_type="text/html"))["schedule"]
        return {"ritsu_error": (req.status, req.reason)}

def gen_schedule_embed(schedule: dict, day_of_week: str) -> hikari.Embed:
    """To generate an embed with the schedule for that day"""

    embed: hikari.Embed = hikari.Embed(title=f"Schedule for {day_of_week}")
    description: str = ""
    try:
        for anime in schedule[day_of_week]:
            description += (
                f"{anime['time']} - [{anime['title']}]"
                f"(https://subsplease.org/{anime['page']}) \n"
            )
        embed.description = description
    except KeyError:
        embed.description = "_No anime found for this day._"
    return embed

def gen_action_row(bot: alluka.Injected[hikari.GatewayBot]) -> hikari.api.ActionRowBuilder:
    """To generate a cached ActionRowBuilder to reuse for other commands"""

    action_row: hikari.api.ActionRowBuilder = bot.rest.build_action_row()
    select_menu: hikari.api.SelectMenuBuilder = (
        action_row.add_select_menu("schedule")
        .set_min_values(1)
        .set_placeholder("Select a day")
    )
    for day in days_of_week:
        select_menu.add_option(day, day).add_to_menu()
    select_menu.add_to_container()
    return action_row
