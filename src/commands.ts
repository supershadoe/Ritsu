`use strict`;

import { ApplicationCommandOptionType, ApplicationCommandType } from "discord-api-types/v10";
import { DAYS_OF_WEEK } from "./consts";

const GuildOnlySlashCommand = {
    dm_permission: false,
    type: ApplicationCommandType.ChatInput
}

export const PUBCHEM = {
    ...GuildOnlySlashCommand,
    id: "985455808697466900",
    name: "pubchem",
    description: "Fetch the details of a compound from PubChem",
    options: [
        {
            name: "Compound Name",
            description:
              "The name of the compound " +
              "/ Try to use IUPAC Name for accurate result",
            type: ApplicationCommandOptionType.String,
            required: true
        }
    ]
}

export const FANDOM = {
    ...GuildOnlySlashCommand,
    id: "996816322556071976",
    name: "fandom",
    description: "Search for any article from any fandom",
    options: [
        {
            name: "Search Term",
            description: "Term to search for",
            type: ApplicationCommandOptionType.String,
            required: true
        },
        {
            name: "Fandom Name",
            description: "Fandom site to search in",
            type: ApplicationCommandOptionType.String,
            required: true
        }
    ]
};

export const WIKIPEDIA = {
    ...GuildOnlySlashCommand,
    id: "996805455798087720",
    name: "wikipedia",
    description: "Search for any article from wikipedia",
    options: [
        {
            name: "Search Term",
            description: "Term to search for",
            type: ApplicationCommandOptionType.String,
            required: true
        }
    ]
}

export const SUBSPLEASE = {
    ...GuildOnlySlashCommand,
    id: "985089699599241254",
    name: "subsplease",
    description: "Commands to access Subsplease API",
    options: [
        {
            name: "schedule",
            description: "Shows release schedule of Subsplease",
            type: ApplicationCommandOptionType.Subcommand,
            options: [
                {
                    name: "Day of week",
                    description: "Day of week to fetch schedule for",
                    choices: DAYS_OF_WEEK,
                    default: DAYS_OF_WEEK[(new Date()).getDay()],
                    required: false
                }
            ]
        }
    ]
}
