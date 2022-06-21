"""
The default dependency prototype from which other dependencies can inherit.

This is to ensure properly typed code.
"""

import abc
import typing

import alluka

class DependencyProto(abc.ABC):
    """A dependency with a loader and unloader to be used with alluka"""

    dep_cls: typing.Type[typing.Any]
    __slots__: tuple[str] = ("dep_cls",)

    @staticmethod
    @abc.abstractmethod
    async def loader(client: alluka.InjectedDescriptor) -> None:
        """
        A helper function to initialize the dependency and set a type dependency
        in tanjun/alluka.
        """

    @staticmethod
    @abc.abstractmethod
    async def unloader(client: alluka.InjectedDescriptor) -> None:
        """
        A helper function to gracefully remove the dependency from tanjun/alluka
        """
