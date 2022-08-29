`use strict`;

import {
    APIChatInputApplicationCommandInteraction,
    ApplicationCommandOptionType, ApplicationCommandType,
    RESTPostAPIChatInputApplicationCommandsJSONBody
} from "discord-api-types/v10";
import { Env } from "..";
import { DAYS_OF_WEEK, not_impl } from "../utils";
import { pubchem } from "./pubchem";

const GuildOnlySlashCommand: Pick<
    RESTPostAPIChatInputApplicationCommandsJSONBody,
    "dm_permission" | "type"
> = {
    dm_permission: false,
    type: ApplicationCommandType.ChatInput,
};

export type RitsuSlashCommand = RESTPostAPIChatInputApplicationCommandsJSONBody & {
    callback: (
        interaction: APIChatInputApplicationCommandInteraction,
        env: Env, ctx: ExecutionContext
    ) => Response
};

export const PUBCHEM: RitsuSlashCommand = {
    ...GuildOnlySlashCommand,
    name: "pubchem",
    description: "Fetch the details of a compound from PubChem",
    options: [
        {
            name: "compound_name",
            description:
              "The name of the compound " +
              "/ Try to use IUPAC Name for accurate result",
            type: ApplicationCommandOptionType.String,
            required: true
        }
    ],
    callback: pubchem
};

export const FANDOM: RitsuSlashCommand = {
    ...GuildOnlySlashCommand,
    name: "fandom",
    description: "Search for any article from any fandom",
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
    ],
    callback: not_impl
};

export const WIKIPEDIA: RitsuSlashCommand = {
    ...GuildOnlySlashCommand,
    name: "wikipedia",
    description: "Search for any article from wikipedia",
    options: [
        {
            name: "search_term",
            description: "Term to search for",
            type: ApplicationCommandOptionType.String,
            required: true
        }
    ],
    callback: not_impl
};

export const SUBSPLEASE: RitsuSlashCommand = {
    ...GuildOnlySlashCommand,
    name: "subsplease",
    description: "Commands to access Subsplease API",
    options: [
        {
            name: "schedule",
            description: "Shows release schedule of Subsplease",
            type: ApplicationCommandOptionType.Subcommand,
            options: [
                {
                    name: "day_of_week",
                    description: "Day of week to fetch schedule for",
                    type: ApplicationCommandOptionType.String,
                    choices: DAYS_OF_WEEK.map((d) => ({ name: d, value: d })),
                    required: false
                }
            ]
        }
    ],
    callback: not_impl
};
// TODO default: DAYS_OF_WEEK[(new Date()).getDay()],
// TODO create a KV Namespace with all command ids for both testing and stable bot.
