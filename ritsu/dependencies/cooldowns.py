"""
The default dependency prototype from which other dependencies can inherit.

This is to ensure properly typed code.
"""

import typing

import alluka
import tanjun
from typing_extensions import Self

from ritsu.dependency import DependencyProto

class CooldownsDep(DependencyProto):
    """A dependency with a loader and unloader to be used with alluka"""

    dep_cls: typing.Type[tanjun.InMemoryCooldownManager] = (
        tanjun.InMemoryCooldownManager
    )

    @classmethod
    async def loader(
        cls: typing.Type[Self], client: alluka.Injected[tanjun.Client]
    ) -> None:
        """To initialize the cooldown manager"""
        (
            cls.dep_cls()
            .set_bucket("comp_pubchem", tanjun.BucketResource.GLOBAL, 5, 1)
            .add_to_client(client)
        )

    @classmethod
    async def unloader(
        cls: typing.Type[Self], _: alluka.Injected[tanjun.Client]
    ) -> None:
        """
        Cooldowns get auto-unloaded by the client when it closes so no need to
        manually write code to unload it
        """
