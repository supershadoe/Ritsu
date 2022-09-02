`use strict`;

import {
    APIApplicationCommandInteractionDataStringOption,
    APIApplicationCommandInteractionDataSubcommandOption,
    APIChatInputApplicationCommandInteraction,
    APIEmbed, ComponentType,
    RESTPatchAPIWebhookWithTokenMessageJSONBody
} from "discord-api-types/v10";
import { Env } from "..";
import { DAYS_OF_WEEK, deferResponse, editInteractionResp, not_impl } from "../utils";

/** The basic URL of PubChem's site. */
const SUBSPLEASE_URL = "https://subsplease.org";

/** The URL of SubsPlease's API. */
const SUBSPLEASE_API = `${SUBSPLEASE_URL}/api`;

/** A model of the schedule data sent by SubsPlease. */
interface ScheduleData {
    tz: string;
    schedule: {
        [day: string]: {
            title: string;
            page: string;
            image_url: string;
            time: string;
        }[]
    }
}

/**
 * Embed generator for sending in response.
 *
 * @param schedule The schedule data returned by SubsPlease.
 * @param dayOfWeek The day of the week to generate embeds for.
 * @returns An array of embeds containing a single embed.
 */
function generateEmbeds(
    schedule: ScheduleData["schedule"], dayOfWeek: string
): [APIEmbed] {
    const embeds: [APIEmbed] = [{
        title: `Schedule for ${dayOfWeek}`,
        description: ""
    }]
    if (dayOfWeek in schedule)
        schedule[dayOfWeek].forEach(anime => {
            embeds[0].description +=
                `${anime.time} - [${anime.title}]`
                + `(${SUBSPLEASE_URL}/${anime.page})\n`
        });
    else
        embeds[0].description = "_No anime found for this day._";

    return embeds;
}

/**
 * The primary command handler for `subsplease schedule` command which fetches
 * results from the subsplease's API and responds to the interaction.
 *
 * @param day The day of week to show the schedule for.
 * @param appID The application ID of the bot.
 * @param ctx The execution context to use for caching.
 * @param interactionToken The token for the current interaction to edit the
 * deferred message.
 */
async function fetchScheduleAndRespond(
    day: string | undefined, appID: string, ctx: ExecutionContext,
    interactionToken: string
): Promise<Response> {
    const cache = caches.default;
    const requestURL = `${SUBSPLEASE_API}/?f=schedule&tz=UTC`;
    let response = await cache.match(requestURL);
    const interactionResponse: RESTPatchAPIWebhookWithTokenMessageJSONBody = {};

    let dayOfWeek = day;
    if (! dayOfWeek) dayOfWeek = DAYS_OF_WEEK[(new Date()).getDay()];

    if (! response) {
        response = await fetch(requestURL);
        if (! response.ok) {
            interactionResponse.content =
                "Error while fetching the schedule.\nAPI responded with"
                + `**${response.status}**: **${response.statusText}**.`;
            return await editInteractionResp(
                appID, interactionToken, interactionResponse
            );
        }
        ctx.waitUntil(cache.put(requestURL, response.clone()));
    }

    const schedule = (await response.json<ScheduleData>()).schedule;
    interactionResponse.content =
        "Here's the current release schedule of SubsPlease.";
    interactionResponse.embeds = generateEmbeds(schedule, dayOfWeek);
    interactionResponse.components = [{
        type: ComponentType.ActionRow,
        components: [{
            type: ComponentType.SelectMenu,
            custom_id: "subsplease-schedule-day",
            options: DAYS_OF_WEEK.map((value, index) => ({
                value: `subsplease-schedule-day${index}`,
                label: value
            })),
            placeholder: "Select a day"
        }]
    }];
    return await editInteractionResp(
        appID, interactionToken, interactionResponse
    );
}

/**
 * Interaction handler for `/subsplease` command.
 *
 * @param interaction The interaction object sent by Discord.
 * @param env The env at the time of execution.
 * @param ctx The execution context.
 * @returns A deferred response object to wait till data is fetched.
 */
export function subsplease(
    interaction: APIChatInputApplicationCommandInteraction,
    env: Env, ctx: ExecutionContext
): Response {
    const subcmd =
        <APIApplicationCommandInteractionDataSubcommandOption>
            interaction.data.options![0];
    switch(subcmd.name) {
        case "schedule":
            const dayOption =
                <APIApplicationCommandInteractionDataStringOption | undefined>
                    subcmd.options![0];
            const day = dayOption ? dayOption.value: undefined;
            ctx.waitUntil(fetchScheduleAndRespond(
                day, env.RITSU_APP_ID, ctx, interaction.token
            ));
            break;
        default:
            return not_impl();
    }
    return deferResponse();
    // TODO add callback to slash command options also so that we can avoid this clusterf
}
