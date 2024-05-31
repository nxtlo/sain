# BSD 3-Clause License
#
# Copyright (c) 2022-Present, nxtlo
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""Abstractions for threading / asynchronous programming."""

from __future__ import annotations

__all__ = ("spawn", "loop")

import asyncio
import enum
import typing

from . import result as _result

if typing.TYPE_CHECKING:
    import collections.abc as collections

    T_co = typing.TypeVar("T_co", covariant=True)
    T = typing.TypeVar("T", bound=collections.Callable[..., typing.Any])


class SpawnError(enum.Enum):
    EMPTY = 0
    """No awaitables were passed."""
    CANCELED = 1
    """The future gatherer were canceled."""
    TIMEOUT = 2
    """The future gatherer timed-out."""


async def spawn(
    *aws: collections.Awaitable[T_co],
    timeout: float | None = None,
) -> _result.Result[collections.Sequence[T_co], SpawnError]:
    """Spawn all given awaitables concurrently.

    Example
    -------
    ```py
    async def get(url: str) -> dict[str, Any]:
        return await http.get(url).json()

    async def main() -> None:
        tasks = await spawn(*(get("url.com") for _ in range(10)))
        match tasks:
            case Ok(tasks):
                assert len(tasks) <= 10
            case Err(why) if why.TIMEOUT:
                print("couldn't make it in time :<")
            case _:
                ...
    ```

    Parameters
    ----------
    *aws : `collections.Awaitable[T]`
        The awaitables to gather.
    timeout : `float | None`
        An optional timeout.

    Returns
    -------
    `sain.Result[T, SpawnError]`:
        The result of the gathered awaitables.
    """

    if not aws:
        return _result.Err(SpawnError.EMPTY)

    tasks: list[asyncio.Task[T_co]] = []

    tasks.extend(asyncio.ensure_future(coro) for coro in aws)
    gatherer = asyncio.gather(*tasks)
    try:
        return _result.Ok(await asyncio.wait_for(gatherer, timeout=timeout))

    except asyncio.CancelledError:
        return _result.Err(SpawnError.CANCELED)
    except asyncio.TimeoutError:
        return _result.Err(SpawnError.TIMEOUT)

    finally:
        for task in tasks:
            if not task.done() and not task.cancelled():
                task.cancel()
        gatherer.cancel()


# source: hikari-py/aio.py
def loop() -> asyncio.AbstractEventLoop:
    """Get the current usable event loop or create a new one.

    Returns
    -------
    `asyncio.AbstractEventLoop`
    """
    try:
        loop = asyncio.get_event_loop_policy().get_event_loop()

        if not loop.is_closed():
            return loop

    except RuntimeError:
        pass

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop
