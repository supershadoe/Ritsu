"""Functions to initialize and close aiohttp session"""

import typing

import aiohttp
import alluka
import tanjun
from alluka.abc import UNDEFINED
from typing_extensions import Self

from ritsu.dependency import DependencyProto


class AiohttpDep(DependencyProto):
    """A class to represent aiohttp dependency"""

    dep_cls = aiohttp.ClientSession

    @classmethod
    async def loader(
        cls: typing.Type[Self], client: alluka.Injected[tanjun.Client]
    ) -> None:
        """To load the dependency"""
        http_s: aiohttp.ClientSession = aiohttp.ClientSession()
        client.set_type_dependency(cls.dep_cls, http_s)

    @classmethod
    async def unloader(
        cls: typing.Type[Self], client: alluka.Injected[tanjun.Client]
    ) -> None:
        """To unload the dependency"""
        dep_cls: typing.Type[cls.dep_cls] = cls.dep_cls
        if (http_s := client.get_type_dependency(dep_cls)) is not UNDEFINED:
            await http_s.close()
            client.remove_type_dependency(dep_cls)


__all__: tanjun.typing.Final[tuple[str]] = ("AiohttpDep",)
