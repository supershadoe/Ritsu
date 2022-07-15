"""Handlers for component interactions"""

from typing import Awaitable

import alluka
import hikari
import tanjun

from hikari.impl.special_endpoints import InteractionMessageBuilder


class ComponentInteractionHandler:
    def __init__(self):
        pass

    async def pubchem_handler(self):
        """To handle interactions for messages from Pubchem component"""

    async def __call__(
        self, inter: hikari.ComponentInteraction,
        bot: alluka.Injected[hikari.RESTAware]
    ) -> Awaitable[hikari.api.special_endpoints.InteractionResponseBuilder]:
        """To be used when interaction handler is called"""
        return bot.rest.create_interaction_response()
