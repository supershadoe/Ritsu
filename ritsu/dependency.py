"""
The default dependency prototype from which other dependencies can inherit.

This is to ensure properly typed code.
"""

import abc
import typing

import alluka
from typing_extensions import Self

class DependencyProto(abc.ABC):
    """A dependency with a loader and unloader to be used with alluka"""

    dep_cls: typing.Type[typing.Any]
    __slots__: tuple[str] = ("dep_cls",)

    @classmethod
    @abc.abstractmethod
    async def loader(
        cls: typing.Type[Self], client: alluka.InjectedDescriptor
    ) -> None:
        """
        A helper function to initialize the dependency and set a type dependency
        in tanjun/alluka.
        """

    @classmethod
    @abc.abstractmethod
    async def unloader(
        cls: typing.Type[Self], client: alluka.InjectedDescriptor
    ) -> None:
        """
        A helper function to gracefully remove the dependency from tanjun/alluka
        """
