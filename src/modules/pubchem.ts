`use strict`;

import {
    APIActionRowComponent, APIApplicationCommandInteractionDataStringOption,
    APIButtonComponentWithCustomId, APIChatInputApplicationCommandInteraction,
    APIChatInputApplicationCommandInteractionData, APIEmbed, APIInteraction,
    APIInteractionResponse, APIMessage, APIMessageButtonInteractionData,
    APIMessageComponentInteraction, APIMessageStringSelectInteractionData,
    APISelectMenuOption, APIStringSelectComponent, ApplicationCommandType,
    ButtonStyle, ComponentType, InteractionResponseType, InteractionType
} from "discord-api-types/payloads/v10";
import {
    RESTPatchAPIWebhookWithTokenMessageJSONBody
} from "discord-api-types/rest/v10";
import { deferResponse, editInteractionResp, jsonResponse, not_impl } from "../utils.js";

/** Type of embed sent in response. */
type ResponseEmbedT = Omit<APIEmbed, "image"> & Required<Pick<APIEmbed, "image">>

/** Structure of the data object sent in interaction object. */
interface CmdInterDataStructure extends
APIChatInputApplicationCommandInteractionData {
    options: [Omit<APIApplicationCommandInteractionDataStringOption, "name"> & {
        name: "compound_name"
    }]
}

/** Structure of the interaction object for this slash command. */
interface PubchemCommandInteraction extends
APIChatInputApplicationCommandInteraction {
    data: CmdInterDataStructure
}

/** Structure of interaction object for component interactions. */
interface PubchemComponentInteraction extends APIMessageComponentInteraction {
    data:
        Omit<APIMessageButtonInteractionData, "custom_id"> & {
            custom_id: "pubchem_toggleDim"
        } | Omit<APIMessageStringSelectInteractionData, "custom_id"> & {
            custom_id: "pubchem_searchResults"
        },
    message: Omit<APIMessage, "embeds" | "components"> & {
        embeds: [ResponseEmbedT],
        components: (APIActionRowComponent<APIStringSelectComponent> | APIActionRowComponent<APIButtonComponentWithCustomId>)[]
    }
}

/** A model of the each compound received for proper typing. */
interface CompoundProps {
        /** Compound ID for a particular compound */
        CID: number;
        /** Common name of that compound */
        Title: string;
        /** IUPAC Name of that compound (Field missing for stuff like phenyl) */
        IUPACName?: string;
        MolecularFormula: string;
        MolecularWeight: string;
        Charge: number;
}

/** A model of the error response sent by PubChem for proper typing. */
interface PubchemError {
    Fault: {
        Code: string;
        Message: string;
        Details: {[index: number]: string};
    }
}

/**
 * Type guard to guarantee that the given interaction is of a slash command.
 * 
 * @param interaction The interaction object.
 * @returns whether the given interaction is of a slash command.
 */
function isSlashCommandInt(interaction: APIInteraction): interaction is PubchemCommandInteraction {
    return (
        (interaction.type === InteractionType.ApplicationCommand) && (interaction.data.type === ApplicationCommandType.ChatInput)
    );
}

/**
 * Type guard to guarantee that the given interaction is of a message component.
 * 
 * @param interaction The interaction object.
 * @returns whether the given interaction is of a message component.
 */
function isComponentInt(interaction: APIInteraction): interaction is PubchemComponentInteraction {
    return (interaction.type === InteractionType.MessageComponent);
}

/** The basic URL of PubChem's site. */
const PUBCHEM_URL = "https://pubchem.ncbi.nlm.nih.gov";

/** The PUG REST API URL. */
const PUG_API_URL = `${PUBCHEM_URL}/rest/pug`;

/** The properties requested for a compound from PubChem. */
const REQUIRED_PROPERTIES = [
    "Title", "IUPACName", "MolecularFormula", "MolecularWeight", "Charge"
];

/**
 * Function to generate a toggle button based on required compound dimension.
 * 
 * @param dim_3d If toggle to change to 3D image should be shown.
 * @returns An action row object with a toggle button.
 */
const dimensionToggleButton = (dim_3d: "2d" | "3d") => ({
    type: ComponentType.ActionRow,
    components: [{
        type: ComponentType.Button,
        label: `Show ${dim_3d === "3d" ? '3' : '2'}D diagram`,
        style: ButtonStyle.Primary,
        custom_id: "pubchem_toggleDim"
    }]
}) satisfies APIActionRowComponent<APIButtonComponentWithCustomId>;

/**
 * Embed generator for sending in response.
 *
 * @param compound The compound to generate embed for.
 * @returns An array of embeds containing a single embed.
 */
function generateEmbed(compound: CompoundProps) {
    const imageURL = `${PUG_API_URL}/compound/cid/${compound.CID}/PNG`;
    const embed = {
        title: compound.Title,
        color: 0xF6CEE7,
        thumbnail: { url: `${imageURL}?record_type=3d&image_size=small` },
        fields: [
            {name: "Molecular Formula", value: compound.MolecularFormula},
            {name: "Molecular Weight", value: compound.MolecularWeight},
        ],
        footer: {
            text: "Fetched from PubChem", icon_url: `${PUBCHEM_URL}/favicon.ico`
        },
        image: { url: `${imageURL}?record_type=2d` },
        url: `${PUBCHEM_URL}/compound/${compound.CID}`
    } satisfies ResponseEmbedT;
    if (compound.IUPACName)
        embed.fields.push({
            name: "IUPAC Name", value: compound.IUPACName
        });
    if (compound.Charge)
        embed.fields.push({
            name: "Charge", value: compound.Charge.toString()
        });

    return [embed]
}

/**
 * Message component generator to attach components to the message thats sent.
 *
 * @param compounds Array of compounds to use for select menu generation.
 * @returns An array of either a button alone or a button and a select menu.
 */
function generateComponents(compounds: CompoundProps[]) {
    const components = [];

    if (compounds.length > 1) {
        const options: APISelectMenuOption[] = compounds.map(compound => ({
            value: compound.CID.toString(),
            label: compound.Title
        }));
        components.push({
            type: ComponentType.ActionRow,
            components: [{
                options,
                type: ComponentType.StringSelect,
                custom_id: "pubchem_switchLink",
                placeholder: "Select a compound"
            }]
        } satisfies APIActionRowComponent<APIStringSelectComponent>);
    }

    components.push(dimensionToggleButton("2d"));
    return components;
}

/**
 * Fetches results from the PubChem API and responds to the interaction.
 *
 * @param appID The application ID of the bot.
 * @param ctx The execution context to use for caching.
 * @param interactionToken The token for the current interaction to edit the
 * deferred message.
 * @param compoundName The name of the compound to search for.
 * @param cid The CID to fetch the details for.
 */
async function fetchDataAndRespond(
    appID: string, ctx: ExecutionContext, interactionToken: string,
    compoundName?: string, cid?: number
) {
    const cache = caches.default;
    const requestURL =
        `${PUG_API_URL}/compound/${cid ? "cid" : "name"}/${compoundName ?? cid}`
        + `/property/${REQUIRED_PROPERTIES.join()}/JSON`;
    let response = await cache.match(requestURL);
    const interactionResponse: RESTPatchAPIWebhookWithTokenMessageJSONBody = {};

    if (! response) {
        response = await fetch(requestURL);
        if (! response.ok) {
            const error = (await response.json<PubchemError>()).Fault;
            interactionResponse.content = 
                    "Error while fetching data from Pubchem.\nAPI "
                    + `responded with **${error.Code}** _«${error.Message}»_`
                    + ` - "**__${error.Details}__**".`
            ;
            return await editInteractionResp(
                appID, interactionToken, interactionResponse
            );
        }
        ctx.waitUntil(cache.put(requestURL, response.clone()));
    }

    type RespT = { PropertyTable: { Properties: CompoundProps[] } };
    const compounds = (await response.json<RespT>()).PropertyTable.Properties;

    interactionResponse.content =
        `Here's the data found for '${compoundName}'.`;
    interactionResponse.embeds = generateEmbed(compounds[0]);
    interactionResponse.components = generateComponents(compounds);

    await editInteractionResp(
        appID, interactionToken, interactionResponse
    );
}

/**
 * Interaction handler for `/pubchem` command.
 *
 * @param interaction The interaction object sent by Discord.
 * @param env The env at the time of execution.
 * @param ctx The execution context.
 * @returns A deferred response object to wait till data is fetched.
 */
export default function (
    interaction: APIInteraction, env: Env, ctx: ExecutionContext
): Response {
    if (isSlashCommandInt(interaction)) {
        ctx.waitUntil(fetchDataAndRespond(
            env.RITSU_APP_ID, ctx, interaction.token,
            interaction.data.options[0].value
        ));
        return deferResponse();
    } else if (isComponentInt(interaction)) {
        if (interaction.data.custom_id === "pubchem_toggleDim") {
            const embeds = interaction.message.embeds;
            const imageURL = new URL(embeds[0].image.url);
            const dim = imageURL.searchParams.get("record_type") as "2d" | "3d";
            imageURL.searchParams.set(
                "record_type", (dim === "2d") ? "3d" : "2d"
            );
            embeds[0].image.url = imageURL.toString();

            const components = interaction.message.components;
            components.pop();
            components.push(dimensionToggleButton(dim));
            return jsonResponse({
                type: InteractionResponseType.UpdateMessage,
                data: {embeds, components}
            } satisfies APIInteractionResponse);
        } else {
            // idk if this works cuz idr what input gives multiple results
            ctx.waitUntil(fetchDataAndRespond(
                env.RITSU_APP_ID, ctx, interaction.token, undefined,
                parseInt(interaction.data.values[0])
            ));
            return jsonResponse({
                type: InteractionResponseType.DeferredMessageUpdate
            });
        }
    }
    return not_impl();
}
