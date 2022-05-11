"""Slash commands for chemistry related commands"""

import aiohttp
import alluka
import hikari
import tanjun
import yarl

from bs4 import BeautifulSoup


@tanjun.with_str_slash_option("compound_name", "Try to use IUPAC Name for accurate results")
@tanjun.as_slash_command("structure", "Fetch the details of a compound from PubChem", always_defer=True)
async def cmd_structure(
    ctx: tanjun.abc.SlashContext,
    compound_name: str,
    bot: alluka.Injected[hikari.GatewayBot],
    session: alluka.Injected[aiohttp.ClientSession]
) -> None:
    """To fetch details of a compound from PubChem"""

    def gen_struct_buttons(dimensions: int) -> hikari.api.ActionRowBuilder:
        """To generate an action row for the message depending on the structure shown"""

        return (
            bot.rest.build_action_row()
            .add_button(hikari.ButtonStyle.PRIMARY, f"toggle-{dimensions}d")
            .set_emoji("🧊" if dimensions == 3 else "⬜")
            .set_label(f"Show {dimensions}D Structure")
            .add_to_container()
        )

    pubchem_url: yarl.URL = yarl.URL("https://pubchem.ncbi.nlm.nih.gov")
    pug_api_url: yarl.URL = pubchem_url / "rest/pug"
    req_properties: tuple[str, ...] = ("Title", "IUPACName", "MolecularFormula", "MolecularWeight", "Charge")
    request_url: yarl.URL = \
        pug_api_url / "compound/name" / compound_name / "property" / ','.join(req_properties) / "JSON"

    async with session.get(request_url) as details_req:
        if details_req.status == 200:
            details_resp: dict = (await details_req.json())["PropertyTable"]["Properties"][0]
            image_url: yarl.URL = pug_api_url / "compound/cid" / str(details_resp['CID']) / "PNG"
            embed: hikari.Embed = (
                hikari.Embed(title=details_resp["Title"], color=0xF6CEE7)
                .set_thumbnail(str(image_url.with_query(record_type="3d", image_size="small")))
                .add_field(name="IUPACName", value=details_resp["IUPACName"])
                .add_field(name="MolecularFormula", value=details_resp["MolecularFormula"])
                .add_field(name="MolecularWeight", value=details_resp["MolecularWeight"] + " g/mol", inline=True)
                .set_footer(text="Fetched from PubChem", icon=str(pubchem_url / "favicon.ico"))
                .set_image(str(image_url.with_query(record_type="2d")))
            )
            if charge := details_resp["Charge"]:
                embed.add_field(name="Charge", value=charge, inline=True)

            og_msg = await ctx.edit_initial_response(
                content="Here's the data requested.", embed=embed, component=gen_struct_buttons(3)
            )
            with (
                bot.stream(hikari.InteractionCreateEvent, timeout=30).filter(
                    ("interaction.type", hikari.InteractionType.MESSAGE_COMPONENT),
                    ("interaction.component_type", hikari.ComponentType.BUTTON),
                    ("interaction.message.id", og_msg.id),
                    ("interaction.user", ctx.author)
                )
            ) as stream:
                async for event in stream:
                    dimension: int = int(event.interaction.custom_id[-2])
                    embed.set_image(str(image_url.update_query(record_type=f"{dimension}d")))
                    await event.interaction.create_initial_response(
                        response_type=hikari.ResponseType.MESSAGE_UPDATE,
                        embed=embed,
                        component=gen_struct_buttons(2 if dimension == 3 else 3)
                    )
            try:
                await ctx.edit_initial_response(components=None)
            except hikari.NotFoundError:
                pass
        else:
            try:
                # If PubChem returns a proper error JSON
                error: dict = (await details_req.json())["Fault"]
                embed: hikari.Embed = (
                    hikari.Embed(title="Error", description=f"_{error['Details'][0]}._", color=0xFF0000)
                    .add_field("Code", f"**{error['Code']}**", inline=True)
                    .add_field("Message", error["Message"], inline=True)
                )
            except aiohttp.ContentTypeError:
                # If it doesn't
                bs_text: BeautifulSoup = BeautifulSoup(await details_req.text(), "html.parser")
                embed: hikari.Embed = hikari.Embed(
                    title="Error", description=f"**{bs_text.title.get_text()}**", color=0xFF0000
                )
            await ctx.edit_initial_response(
                embed=embed,
                content="Oh no! An error has occurred while trying to fetch the required data!"
            )

comp_chemistry: tanjun.Component = tanjun.Component(name="comp_chemistry").load_from_scope()
comp_chemistry.make_loader()

__all__: tanjun.typing.Final[list[str]] = ['comp_chemistry']
