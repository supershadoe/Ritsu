CREATE TABLE IF NOT EXISTS schema_info(
    schema_version INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS anime_subs(
    anime TEXT PRIMARY KEY,
    subscribers BIGINT[]
);

CREATE TABLE IF NOT EXISTS clan_info(
    guild_id BIGINT PRIMARY KEY,
    clan_tag TEXT,
    clan_name TEXT,
    roles BIGINT[]
);
