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
"""Composable async iteration.

This module is an async version of `sain.iter`.

### `AsyncIterator`

The heart and soul of this module is the `AsyncIterator` interface, its core looks like this:

```py
class AsyncIterator[Item]:
    async def __anext__(self) -> Item: ...
```

An async iterator has two core methods, `AsyncIterator.poll_next` and `AsyncIterator.__anext__`.
`AsyncIterator.poll_next` returns an `Option[Item]` as long as there are elements,
and once they've all been exhausted, it returns `None` to indicate that the iteration is done.
`AsyncIterator.__anext__` is the same as `AsyncIterator.poll_next`, but it raises `StopAsyncIteration` when there are no more elements.

Async iterators are also composable, and it's common to chain them together to do more complex forms of processing.

### `Stream`

`Stream`, like `sain.Iter`, is out of the box a general-purpose type of async iterator that implements `AsyncIterator` which allows any iterable to be converted into an async iterator.

### `into_stream`

This simply just wraps the passed iterable into a `Stream`.

### Implementing `AsyncIterator`

Creating an async iterator of your own involved two steps: creating a class that holds the iterator's state, and then implement `AsyncIterator`.

Let's make a `Counter` async iterator that counts from 0 to 10:

```py
from __future__ import annotations

from sain.async_iter import AsyncIterator

class Counter(AsyncIterator[int]):
    def __init__(self, /) -> None:
        # The state of the iterator is stored in the instance.
        self.count = 0

    # `__anext__` is the only required method.
    async def __anext__(self) -> int:
        self.count += 1

        if self.count < 6:
            return self.count

        raise StopAsyncIteration
```

And then we can use it like this:

```py
counter = Counter()

# The idiomatic way to use an async iterator is to use it in an `async for` loop.
async for value in counter:
    print(value)
```
"""

from __future__ import annotations

__all__ = ("AsyncIterator", "Stream", "into_stream")

import abc
import typing
from collections import abc as collections

from sain.macros import override
from sain.macros import rustc_diagnostic_item
from sain.macros import unstable
from sain.option import NOTHING
from sain.option import Some

T = typing.TypeVar("T", covariant=True)
Item = typing.TypeVar("Item")

if typing.TYPE_CHECKING:
    from typing_extensions import Self

    from sain.option import Option

    Poller: typing.TypeAlias = collections.AsyncIterable[T] | collections.Iterable[T]


@rustc_diagnostic_item("AsyncIterator")
@unstable(feature="async_iter", issue="257")
class AsyncIterator(typing.Generic[Item], abc.ABC):
    """An interface for dealing with async iterators.

    It is the async version of `sain.Iterator`. See the top module documentation for more details.
    """

    __slots__ = ()

    # Required methods

    @abc.abstractmethod
    async def __anext__(self) -> Item: ...

    # Provided methods

    async def poll_next(self) -> Option[Item]:
        try:
            fut = await self.__anext__()
        except (StopAsyncIteration, StopIteration):
            return NOTHING

        return Some(fut)

    def __aiter__(self) -> Self:
        return self

    async def __await__(self) -> collections.MutableSequence[Item]:
        return [item async for item in self]


# special methods require this public annotation for pdoc to show it.
# TODO: do the same for other methods?
AsyncIterator.__anext__.__doc__ = """@public"""  # pyright: ignore


@typing.final
@unstable(feature="async_iter", issue="257")
class Stream(AsyncIterator[Item]):
    """A stream of values produced asynchronously.

    This is a general-purpose type of async iterator that implements `AsyncIterator`
    which allows any iterable to be converted into an async iterator.
    """

    __slots__ = ("_poller",)

    def __init__(self, iterable: Poller[Item], /) -> None:
        self._poller = (
            iterable.__aiter__()
            if isinstance(iterable, collections.AsyncIterable)
            else iterable.__iter__()
        )

    @override
    async def __anext__(self) -> Item:
        if isinstance(self._poller, collections.AsyncIterable):
            return await anext(self._poller)
        else:
            try:
                return next(self._poller)
            except StopIteration:
                raise StopAsyncIteration


@unstable(feature="async_iter", issue="257")
def into_stream(iterable: Poller[Item], /) -> Stream[Item]:
    """Converts an iterable into a stream.

    Example
    -------
    ```py
    from sain.async_iter import into_stream

    async def gen():
        for i in range(10):
            if i % 2 == 0:
                yield i

    ranges = into_stream(gen())
    async for value in ranges:
        print(value)
    ```
    """
    return Stream(iterable)
