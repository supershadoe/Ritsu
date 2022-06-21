"""Functions to open and close asyncpg connection"""

import logging
import os
import typing

import alluka
import asyncpg
import tanjun
from typing_extensions import Self

from ritsu.dependency import DependencyProto


class AsyncpgDep(DependencyProto):
    """A class to represent asyncpg dependency"""

    dep_cls: typing.Type[asyncpg.Connection] = asyncpg.Connection

    @classmethod
    async def loader(
        cls: typing.Type[Self], client: alluka.Injected[tanjun.Client]
    ) -> None:
        """To load the dependency using `self.loader_cm()`"""
        if db_pwd := os.getenv('SQL_DB_PASSWORD'):
            try:
                db_conn: asyncpg.Connection = await asyncpg.connect(
                    f"postgresql://ritsu:{db_pwd}@/ritsu"
                )
                client.set_type_dependency(cls.dep_cls, db_conn)
            except OSError as error:
                logging.getLogger("ritsu").error(
                    "Cannot connect to database for whatever reason. "
                    "Check if the database is online.\n"
                    "%s", error,
                    exc_info=1
                )
        else:
            raise ConnectionError(
                "Password for PostgreSQL user `ritsu` not found in runtime env."
            )

    @classmethod
    async def unloader(
        cls: typing.Type[Self], client: alluka.Injected[tanjun.Client]
    ) -> None:
        """To unload the dependency"""
        dep_cls: typing.Type[cls.dep_cls] = cls.dep_cls
        db_conn: asyncpg.Connection = client.get_type_dependency(dep_cls)
        await db_conn.close()
        client.remove_type_dependency(dep_cls)

__all__: typing.Final[tuple[str]] = ("AsyncpgDep",)
