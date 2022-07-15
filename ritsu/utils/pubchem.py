"""Helper functions for pubchem component"""

from typing import Any

import aiohttp
import alluka
import hikari
import yarl

from bs4 import BeautifulSoup

pubchem_url: yarl.URL = yarl.URL("https://pubchem.ncbi.nlm.nih.gov")
pug_api_url: yarl.URL = pubchem_url / "rest/pug"
req_properties: tuple[str, ...] = (
    "Title", "IUPACName", "MolecularFormula", "MolecularWeight", "Charge"
)


async def fetch_compound(
    compound_name: str, session: alluka.Injected[aiohttp.ClientSession]
) -> dict[str, Any]:
    """To fetch the details of a compound from PubChem API"""

    request_url: yarl.URL = (
        pug_api_url / "compound/name" / compound_name / "property"
        / ','.join(req_properties) / "JSON"
    )
    async with session.get(request_url) as req:
        if req.status == 200:
            return (await req.json())["PropertyTable"]["Properties"][0]
        try:
            # If PubChem returns a proper JSON indicating error
            error: dict = (await req.json())["Fault"]
            return {"ritsu_error": (req.status, error)}
        except aiohttp.ContentTypeError:
            # If it doesn't
            bs_text: BeautifulSoup = BeautifulSoup(
                await req.text(), "html.parser"
            )
            return {"ritsu_error": (req.status, bs_text.title.get_text())}


def gen_compound_embed(details: dict[str, str | int]) -> hikari.Embed:
    """To generate embed for showing details of a compound"""

    image_url: yarl.URL = (
        pug_api_url / "compound/cid" / str(details['CID']) / "PNG"
    )
    embed: hikari.Embed = (
        hikari.Embed(title=details["Title"], color=0xF6CEE7)
        .set_thumbnail(str(image_url.with_query(record_type="3d", image_size="small")))
        .add_field(name="IUPACName", value=details["IUPACName"])
        .add_field(name="MolecularFormula", value=details["MolecularFormula"])
        .add_field(name="MolecularWeight", value=details["MolecularWeight"] + " g/mol", inline=True)
        .set_footer(text="Fetched from PubChem", icon=str(pubchem_url / "favicon.ico"))
        .set_image(str(image_url.with_query(record_type="2d")))
    )

    if charge := details["Charge"]:
        embed.add_field(name="Charge", value=charge, inline=True)

    return embed


def gen_action_row(
    bot: alluka.Injected[hikari.RESTBot]
) -> hikari.api.ActionRowBuilder:
    """To generate a tuple of action rows to be cached for later use"""

    action_row: hikari.api.ActionRowBuilder = bot.rest.build_action_row()
    buttons: tuple[str, str] = ("⬜", "🧊")
    for index, button in enumerate(buttons):
        action_row: hikari.api.ActionRowBuilder = (
            action_row
            .add_button(hikari.ButtonStyle.PRIMARY, f"chem-struct-{index}")
            .set_emoji(button)
            .set_label(f"Show {index + 2}D Structure")
            .add_to_container()
        )
    action_row.components[0].set_is_disabled(True)
    return action_row
