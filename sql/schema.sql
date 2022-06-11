CREATE TABLE IF NOT EXISTS schema_info(
    schema_version INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS anime_subs(
    anime TEXT PRIMARY KEY,
    subscribers BIGINT[]
);
