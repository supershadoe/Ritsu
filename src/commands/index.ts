`use strict`;

import {
    ApplicationCommandOptionType,
    ApplicationCommandType,
    RESTPostAPIApplicationCommandsJSONBody
} from "discord-api-types/v10";

const commands: RESTPostAPIApplicationCommandsJSONBody[] = [
    {
        name: "pubchem",
        description: "Fetch the details of a compound from PubChem",
        options: [
            {
                name: "compound_name",
                description:
                    "The name of the compound "
                    + "/ Try to use the IUPAC name for accurate result",
                type: ApplicationCommandOptionType.String,
                required: true
            }
        ],
        dm_permission: false,
        type: ApplicationCommandType.ChatInput
    },
    {
        name: "wiki",
        description: "Commands to access various wiki pages",
        options: [
            {
                name: "fandom",
                description: "Search for any article from any fandom",
                type: ApplicationCommandOptionType.Subcommand,
                options: [
                    {
                        name: "search_term",
                        description: "Term to search for",
                        type: ApplicationCommandOptionType.String,
                        required: true
                    },
                    {
                        name: "fandom_name",
                        description: "Fandom site to search in",
                        type: ApplicationCommandOptionType.String,
                        required: true
                    }
                ]
            },
            {
                name: "wikipedia",
                description: "Search for any article from wikipedia",
                type: ApplicationCommandOptionType.Subcommand,
                options: [
                    {
                        name: "search_term",
                        description: "Term to search for",
                        type: ApplicationCommandOptionType.String,
                        required: true
                    }
                ]
            }
        ],
        dm_permission: false,
        type: ApplicationCommandType.ChatInput
    }
];

export default commands;
