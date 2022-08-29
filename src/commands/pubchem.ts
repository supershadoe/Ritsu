import {
    APIActionRowComponent, APIButtonComponentWithCustomId, APIEmbed,
    APISelectMenuComponent, APISelectMenuOption,
    ButtonStyle, ComponentType, RESTPatchAPIWebhookWithTokenMessageJSONBody
} from "discord-api-types/v10";
import { editInteractionResp } from "../utils";

/** The basic URL of PubChem's site. */
const pubchemURL = "https://pubchem.ncbi.nlm.nih.gov";

/** The PUG REST API URL. */
const pugAPIURL = `${pubchemURL}/rest/pug`;

/** The properties requested for a compound from PubChem. */
const requiredProperties = [
    "Title", "IUPACName", "MolecularFormula", "MolecularWeight", "Charge"
];

/** A model of the property table for proper typing. */
interface PubchemCompoundPropertyTable {
    Properties: {[index: number]: {
        CID: number;
        Title: string;
        IUPACName: string;
        MolecularFormula: string;
        MolecularWeight: string;
        Charge: number;
    }};
}

/** A model of the response sent by PubChem for proper typing. */
interface PubchemCompoundPropTableResp {
    PropertyTable: PubchemCompoundPropertyTable
}

/** A model of the error response sent by PubChem for proper typing. */
interface PubchemError {
    Fault: {
        Code: string;
        Message: string;
        Details: {[index: number]: string};
    }
}

/** Type alias for the components that are sent by the bot. */
type pubchemComponents = (
    [APIActionRowComponent<APIButtonComponentWithCustomId>]
    | [
        APIActionRowComponent<APISelectMenuComponent>, APIActionRowComponent<APIButtonComponentWithCustomId>
    ]
);

/** Embed generator for sending in response
 * @param propTable The property table returned by PubChem.
 * @param compound A future-proof param to generate embeds for
 * different compounds from the same propTable (switching between results of
 * the compound search).
 * @returns An array of embeds containing a single embed.
 */
function generateEmbeds(
    propTable: PubchemCompoundPropertyTable, compound: number = 0
): APIEmbed[] {
    const firstCompound = propTable.Properties[compound];
    const imageURL = `${pugAPIURL}/compound/cid/${firstCompound.CID}/PNG`;
    const embed: APIEmbed = {
        title: firstCompound.Title,
        color: 0xF6CEE7,
        thumbnail: { url: `${imageURL}?record_type=3d&image_size=small` },
        fields: [
            {name: "IUPAC Name", value: firstCompound.IUPACName},
            {name: "Molecular Formula", value: firstCompound.MolecularFormula},
            {name: "Molecular Weight", value: firstCompound.MolecularWeight},
        ],
        footer: {
            text: "Fetched from PubChem", icon_url: `${pubchemURL}/favicon.ico`
        },
        image: { url: `${imageURL}?record_type=2d` }
    };
    if (firstCompound.Charge)
        embed.fields?.push({
            name: "Charge", value: firstCompound.Charge.toString()
        });

    return [embed]
}

/**
 * Message component generator to attach components to the message thats sent.
 * @param propTable The propTable to generate the select menu from (to switch
 * between search results).
 * @returns An array of either a button alone or a button and a select menu.
 */
function generateComponents(
    propTable: PubchemCompoundPropertyTable
): pubchemComponents {
    let components: pubchemComponents =[{
        type: ComponentType.ActionRow,
        components: [{
            type: ComponentType.Button,
            label: "Flatten Structure",
            style: ButtonStyle.Primary,
            custom_id: "pubchem-toggleDim"
        }]
    }];
    const results = Object.values(propTable.Properties)
    if (results.length > 2) {
        const results: APISelectMenuOption[] = Object.values(
            propTable.Properties).map((compound, index) => ({
                value: `pubchem-result-${index}`, 
                label: compound.Title
            }));
        const selMenu: APIActionRowComponent<APISelectMenuComponent> = {
            type: ComponentType.ActionRow,
            components: [{
                type: ComponentType.SelectMenu,
                custom_id: "pubchem-searchResults",
                options: results,
                placeholder: "Select a compound"
            }]
        };
        components = [selMenu, ...components];
    }
    return components;
}

/**
 * The primary command handler for `pubchem` command which fetches results from
 * the API and responds to the interaction.
 * @param compoundName The name of the compound to search for.
 * @param appID The application ID of the bot.
 * @param ctx The execution context to use for caching.
 * @param interactionToken The token for the current interaction to edit the
 * deferred message.
 */
export async function pubchem(
    compoundName: string, appID: string, ctx: ExecutionContext,
    interactionToken: string
): Promise<Response> {
    const cache = caches.default;
    const requestURL =
        `${pugAPIURL}/compound/name/${compoundName}/property`
        + `/${requiredProperties.join()}/JSON`;
    let response = await cache.match(requestURL);
    const interactionResponse: RESTPatchAPIWebhookWithTokenMessageJSONBody = {};

    if (! response) {
        response = await fetch(requestURL);
        if (! response.ok) {
            const error = (await response.json() as PubchemError).Fault;
            interactionResponse.content = 
                    "Error while fetching data from Pubchem.\nAPI "
                    + `responded with **${error.Code}** _«${error.Message}»_`
                    + ` - "**__${error.Details}__**".`
            ;
            return editInteractionResp(
                appID, interactionToken, interactionResponse
            );
        }
        ctx.waitUntil(cache.put(requestURL, response.clone()));
    }

    const propTable = (
        await response.json() as PubchemCompoundPropTableResp
    )["PropertyTable"];

    interactionResponse.content =
        `Here's the data found for '${compoundName}'.`;
    interactionResponse.embeds = generateEmbeds(propTable);
    interactionResponse.components = generateComponents(propTable);

    return await editInteractionResp(
        appID, interactionToken, interactionResponse
    );
}
