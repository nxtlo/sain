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
"""A lazy const that gets initialized at runtime."""

from __future__ import annotations

__all__ = ("Lazy", "LazyFuture")

import asyncio
import threading
import typing

from sain.macros import rustc_diagnostic_item

if typing.TYPE_CHECKING:
    from collections import abc as collections

T = typing.TypeVar("T")


@rustc_diagnostic_item("Lazy")
@typing.final
class Lazy(typing.Generic[T]):
    """A thread-safe value that gets lazily initialized at first access.

    This type is thread-safe and may be called from multiple threads since this value
    can be initialized from multiple threads, however, any calls to `Lazy.get` will block
    if another thread is initializing it.

    Example
    -------
    ```py
    # some expensive call that returns a `str`
    def expensive_string() -> str:
        return "hehehe"

    STRING: Lazy[str] = Lazy(expensive_string)
    print(STRING.get()) # The string is built, stored in the lazy lock and returned.
    print(STRING.get()) # The string is retrieved from the lazy lock.
    ```
    """

    __slots__ = ("__inner", "__lock")

    def __init__(self, f: collections.Callable[[], T]) -> None:
        self.__inner: T | collections.Callable[[], T] = f
        self.__lock: threading.Lock | None = None

    def get(self) -> T:
        """Get the value if it was initialized, otherwise initialize it and return it.

        Its guaranteed to not block if the value has been initialized.

        Example
        -------
        ```py
        # some expensive call that returns a `str`
        def expensive_string() -> str:
            return "hehehe"

        STRING: Lazy[str] = Lazy(expensive_string)
        print(STRING.get()) # The string is built, stored in the lazy lock and returned.
        print(STRING.get()) # The string is retrieved from the lazy lock.
        ```
        """
        if not callable(self.__inner):
            # value is already initialized, no need to make a call.
            return self.__inner

        if self.__lock is None:
            self.__lock = threading.Lock()

        with self.__lock:
            # TYPE SAFETY: We know we need to call this function.
            self.__inner = self.__inner()  # type: ignore
            return self.__inner  # type: ignore

    def __repr__(self) -> str:
        return f"Lazy(value: {self.__inner!r})"

    __str__ = __repr__

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Lazy):
            return self.__inner == other.get()

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


@typing.final
class LazyFuture(typing.Generic[T]):
    """A thread-safe value that gets lazily initialized asynchronously at first access.

    This type is thread-safe and may be called from multiple threads since this value
    can be initialized from multiple threads, however, any calls to `Lazy.get` will block
    if another thread is initializing it.

    Example
    -------
    ```py
    # some expensive call that returns a `str`
    async def fetch_expensive_string(filtered: bool) -> str:
        return "hehehe" if filtered else "whahaha"

    STRING: LazyFuture[str] = LazyFuture(lambda: expensive_string(True))
    print(await STRING.get()) # The string is built, stored in the lazy lock and returned.
    print(await STRING.get()) # The string is retrieved from the lazy lock.
    ```
    """

    __slots__ = ("__inner", "__lock")

    def __init__(
        self,
        f: collections.Callable[[], collections.Coroutine[typing.Any, typing.Any, T]],
    ) -> None:
        self.__inner: (
            T
            | collections.Callable[[], collections.Coroutine[typing.Any, typing.Any, T]]
        ) = f
        self.__lock: asyncio.Lock | None = asyncio.Lock()

    async def get(self) -> T:
        """Get the value if it was initialized, otherwise initialize it and return it.

        Example
        -------
        ```py
        # some expensive call that returns a `str`
        async def fetch_expensive_string(filtered: bool) -> str:
            return "hehehe" if filtered else "whahaha"

        STRING: LazyFuture[str] = LazyFuture(lambda: expensive_string(True))
        print(await STRING.get()) # The string is built, stored in the lazy lock and returned.
        print(await STRING.get()) # The string is retrieved from the lazy lock.
        ```
        """
        if not callable(self.__inner):
            # value is already initialized, no need to make a call.
            return self.__inner

        if self.__lock is None:
            self.__lock = asyncio.Lock()

        async with self.__lock:
            # calling self.__inner will make self.__inner type T
            v = await self.__inner()  # pyright: ignore
            self.__inner = v
            return v

    def __repr__(self) -> str:
        return f"LazyFuture(value: {self.__inner!r})"

    __str__ = __repr__

    def __eq__(self, other: object) -> bool:
        if not callable(self.__inner):
            return False

        if isinstance(other, Lazy):
            return self._inner == other._inner  # pyright: ignore

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
