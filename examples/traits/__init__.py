from __future__ import annotations

import asyncio
import dataclasses
import typing

from sain import Some
from sain import Default
from sain import futures
from sain.convert import From, Into

# Is is optional to type hint values with `Option` and Some can be used instead.
if typing.TYPE_CHECKING:
    from sain import Option
    from collections.abc import Awaitable, Callable


@dataclasses.dataclass
class Loop(
    # This class has a default loop.
    Default[asyncio.AbstractEventLoop],
    # This class can be constructed from a a callable that returns an event loop.
    From[Callable[[], asyncio.AbstractEventLoop]],
    # This class can extract its event loop.
    Into[asyncio.AbstractEventLoop],
):
    """A default event loop."""

    # Initialize a default loop with value None.
    loop: Option[asyncio.AbstractEventLoop] = Some(None)

    # Impl `From`
    @classmethod
    def from_value(cls, value: Callable[[], asyncio.AbstractEventLoop]) -> Loop:
        return cls(loop=Some(value()))

    # Impl `Into`
    def into(self) -> asyncio.AbstractEventLoop:
        return self.loop.unwrap_or_else(self.default)

    # This method must be implemented which returns a default value.
    @staticmethod
    def default() -> asyncio.AbstractEventLoop:
        """The default event loop."""
        return futures.loop()

    def run(self, func: Awaitable[None]) -> None:
        # Get the event loop either from the provided value or from the default.
        self.loop.unwrap_or_else(self.default).run_until_complete(func)


async def woof() -> None:
    print("Woof!")


loop = Loop()
loop.run(woof())


# Default is `@runtime_checkable` protocol.
def run_at(future: float, loop: Default[asyncio.AbstractEventLoop]) -> None:
    default_loop = loop.default()
    default_loop.call_at(future, woof)


# this block won't run.
if False:
    # you can use a custom event loop, uvloop for an example.
    uvloop_loop = Loop.from_value(uvloop.new_event_loop)  # noqa
    run_at(1.0, uvloop_loop)

# extract the loop from the Loop instance
extracted_loop = loop.into()
assert isinstance(extracted_loop, asyncio.AbstractEventLoop)
