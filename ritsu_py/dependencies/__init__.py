"""Module to store code to initialize dependencies to use with alluka"""

import typing as _typing

from .aiohttp import *
from .asyncpg import *
from .cooldowns import *

__all__: _typing.Final[list[str]] = [
    name for name in dir() if name.endswith("Dep")
]

del _typing
