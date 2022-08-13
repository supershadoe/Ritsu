/**
 * Days of week for using in some commands.
 */
export const DAYS_OF_WEEK = [
    "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
]

/**
 * Creates a Response object from JSON objects.
 *
 * Made just for convenience.
 *
 * @param responseBody The response object to stringify.
 * @param options Custom settings like headers/status code.
 * @returns A new response object generated with the required defaults.
 */
export function jsonResponse(
    responseBody: object,
    options: object = {
        headers: {
            "Content-Type": "application/json;charset=UTF-8"
        }
    },
    jsonType: boolean = true //TODO
): Response {
    return new Response(JSON.stringify(responseBody), options);
}
