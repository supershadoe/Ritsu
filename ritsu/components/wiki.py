"""Slash commands for searching wikis"""

import functools
import typing
import tanjun

from ritsu.handlers.wiki import hooks
from ritsu.utils.wiki import send_initial_resp

partial_wiki_cmd = functools.partial(
    tanjun.SlashCommand, send_initial_resp, always_defer=True
)
cmd_wikipedia: tanjun.SlashCommand = (
    typing.cast(tanjun.SlashCommand, partial_wiki_cmd(
        "wikipedia", "Search for any article from wikipedia"
    ))
    .add_str_option("search_term", "Term to search for")
)
cmd_fandom: tanjun.SlashCommand = (
    typing.cast(tanjun.SlashCommand, partial_wiki_cmd(
        "fandom", "Search for any article from any fandom"
    ))
    .add_str_option("search_term", "Term to search for")
    .add_str_option("fandom_name", "Fandom site to search in")
)

hooks.add_to_command(cmd_wikipedia)
hooks.add_to_command(cmd_fandom)

loader_wiki: tanjun.abc.ClientLoader = (
    tanjun.Component(name="Wikis").load_from_scope().make_loader()
)
