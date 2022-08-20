/** Days of week for using in some commands. */
export const DAYS_OF_WEEK = [
    "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
]

/** Content-Type header for response with JSON body. */
export const jsonHeaders = {
    "Content-Type": "application/json;charset=UTF-8"
}

/**
 * Creates a Response object from JSON objects.
 *
 * Made just for convenience.
 *
 * @param responseBody The response object to stringify.
 * @param options Custom settings like headers/status code.
 * @returns A new response object generated with the required defaults.
 */
export const jsonResponse = (
    responseBody: object, options: object = { headers: jsonHeaders }
): Response => new Response(JSON.stringify(responseBody), options);
