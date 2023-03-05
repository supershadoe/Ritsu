`use strict`;

import {
    ApplicationCommandOptionType, ApplicationCommandType
} from "discord-api-types/payloads/v10";
import {
    Locale, RESTPostAPIApplicationCommandsJSONBody
} from "discord-api-types/rest/v10";

/** List of commands to sync with Discord. */
const commands = [
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
    } satisfies RESTPostAPIApplicationCommandsJSONBody,
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
                    },
                    {
                        name: "language",
                        description: "Language to search in",
                        type: ApplicationCommandOptionType.String,
                        choices: Object.entries(Locale).map(
                            ([lang_name, lang_code]) => ({
                                name: lang_name,
                                value: lang_code.split("-")[0]
                            })
                        ).slice(0, 25),
                        required: false
                    }
                ]
            }
        ],
        dm_permission: false,
        type: ApplicationCommandType.ChatInput
    } satisfies RESTPostAPIApplicationCommandsJSONBody
];

export default commands;
