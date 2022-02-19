"""Slash commands for chemistry related commands"""

__author__ = "supershadoe"
__license__ = "Apache v2.0"

import aiohttp
import hikari
import tanjun


@tanjun.with_str_slash_option("compound_name", "Try to use IUPAC Name for accurate results")
@tanjun.as_slash_command("structure", "Fetch the details of a compound from PubChem", always_defer=True)
async def cmd_structure(
    ctx: tanjun.abc.SlashContext,
    compound_name: str,
    bot: hikari.GatewayBot = tanjun.inject(type=hikari.GatewayBot),
    session: aiohttp.ClientSession = tanjun.inject(type=aiohttp.ClientSession)
) -> None:
    """To fetch details of a compound from PubChem"""

    def gen_struct_buttons(dimensions: int) -> hikari.api.ActionRowBuilder:
        if dimensions not in (2, 3):
            raise ValueError("Expected values (2) or (3): There are only 2d and 3d structures.")
        return (
            bot.rest.build_action_row()
            .add_button(
                hikari.ButtonStyle.PRIMARY,
                f"toggle-{dimensions}d"
            )
            .set_emoji("🧊" if dimensions == 3 else "⬜")
            .set_label(f"Show {dimensions}D Structure")
            .add_to_container()
        )

    pug_api_url: str = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    property_url: str = f"{pug_api_url}/compound/name/{compound_name}/property/"
    req_properties: str = "Title,IUPACName,MolecularFormula,MolecularWeight,Charge"
    property_req_url: str = f"{property_url}/{req_properties}/JSON"

    async with session.get(property_req_url) as details_req:
        if details_req.status == 200:
            details_resp = (await details_req.json())["PropertyTable"]["Properties"][0]
            image_url = f"{pug_api_url}/compound/cid/{details_resp['CID']}/PNG?record_type="
            embed = (
                hikari.Embed(title=details_resp["Title"], color=0xF6CEE7)
                .set_thumbnail(f"{image_url}3d&image_size=small")
                .add_field("IUPAC Name", details_resp["IUPACName"])
                .add_field("Molecular Formula", details_resp["MolecularFormula"])
                .add_field("Molecular Weight", details_resp["MolecularWeight"] + " g/mol", inline=True)
                .add_field("Charge", details_resp["Charge"], inline=True)
                .set_footer("Grabbed from PubChem")
                .set_image(f"{image_url}2d")
            )
            await ctx.edit_initial_response(embed=embed, component=gen_struct_buttons(3))
            with (
                bot.stream(hikari.InteractionCreateEvent, timeout=30)
                .filter(("interaction.type", hikari.InteractionType.MESSAGE_COMPONENT))
                .filter(("interaction.component_type", hikari.ComponentType.BUTTON))
                .filter(("interaction.message.id", (await ctx.fetch_initial_response()).id))
                .filter(("interaction.user", ctx.author))
            ) as stream:
                async for event in stream:
                    await event.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_UPDATE)
                    dimension = int(event.interaction.custom_id[-2])
                    embed.set_image(f"{image_url}{dimension}d")
                    await ctx.edit_initial_response(
                        embed=embed, component=gen_struct_buttons(2 if dimension == 3 else 3)
                    )
            await ctx.edit_initial_response(components=None)
        else:
            error: dict = (await details_req.json())["Fault"]
            await ctx.edit_initial_response(
                embed=(
                    hikari.Embed(title="Error", description=f"_{error['Details'][0]}._", color=0xF6CEE7)
                    .add_field("Code", f"**{error['Code']}**", inline=True)
                    .add_field("Message", error["Message"], inline=True)
                )
            )

component = tanjun.Component(name="chemistry").load_from_scope()
component.make_loader()
