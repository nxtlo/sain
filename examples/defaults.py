"""Objects with default values example."""

from __future__ import annotations

import asyncio
import dataclasses
import typing

import sain

# Is is optional to type hint values with `Option` and Some can be used instead.
if typing.TYPE_CHECKING:
    from sain import Option
    from collections.abc import Awaitable


@dataclasses.dataclass
class Loop(sain.Default[asyncio.AbstractEventLoop]):
    """A default event loop."""

    # Initialize a default loop with value None.
    loop: Option[asyncio.AbstractEventLoop] = sain.Some(None)

    # This method must be implemented which returns a default value.
    @staticmethod
    def default() -> asyncio.AbstractEventLoop:
        """The default event loop."""
        return sain.futures.loop()

    def run(self, func: Awaitable[None]) -> None:
        # Get the event loop either from the provided value or from the default.
        self.loop.unwrap_or(self.default()).run_until_complete(func)


async def woof() -> None:
    print("Woof!")


loop = Loop()
loop.run(woof())
