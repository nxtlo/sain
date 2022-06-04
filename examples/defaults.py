"""Objects with default values example."""

import asyncio
import dataclasses
import typing

import sain


@dataclasses.dataclass
class Loop(sain.Default[asyncio.AbstractEventLoop]):
    """A default event loop."""

    # Initialize a default loop with value None.
    loop: sain.Option[asyncio.AbstractEventLoop] = sain.Some(None)

    @staticmethod
    def default() -> asyncio.AbstractEventLoop:
        """The default event loop."""
        return asyncio.get_event_loop()

    def run(self, func: typing.Coroutine[None, None, None]) -> None:
        # Get the event loop either from the provided value or from the default.
        self.loop.unwrap_or(self.default()).run_until_complete(func)


async def woof() -> None:
    print("Woof!")


loop = Loop()
loop.run(woof())
