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

from sain import macros
from sain import option

if typing.TYPE_CHECKING:
    from sain import Option

T = typing.TypeVar("T")


@typing.final
class Lazy(typing.Generic[T]):
    """A thread-safe value that gets lazily initialized at runtime.

    This isn't some sort of magic, the inner value is set to `None` when first initialized,
    Then this `None` gets replaced at runtime when calling `Lazy.set` method.

    This is a well-known approach used in Python to lazily initialize expensive objects
    that needs to be `None` until it gets initialized with a function call at runtime.

    Example
    -------
    ```py
    @dataclass
    class Config:
        token: Lazy[str] = Lazy()

    @dataclass
    class Application:
        config: Config

    # application entry point.
    def run(app: Application) -> None:
        token = app.config.token.set('token')
        app.run(token=token)
    ```
    """

    __slots__ = ("_inner", "_lock")

    def __init__(self) -> None:
        self._inner: T | None = None
        self._lock: threading.Lock | None = None

    @property
    def is_initialized(self) -> bool:
        """Whether the contained value is initialized or not."""
        return self._inner is not None

    def get(self) -> Option[T]:
        """Hold ownership of the contained value and return it.

        This ensures that the value is only generated once and kept
        acquired until its set again with `Lazy.set`.
        """
        if self._inner is not None:
            return option.Some(self._inner)

        if not self._lock:
            self._lock = threading.Lock()

        with self._lock:
            if self._inner is not None:
                # inner here is never none.
                return option.Some(self._inner)

        return option.nothing_unchecked()

    def set(self, value: T, /) -> T:
        """Set the contained value to `value`.

        This will clear any ownership of the value until the next `get` call.

        Example
        -------
        ```py
        lazy = Lazy[str]()
        print(lazy.set("foo"))
        ```
        """
        self._inner = value
        self._lock = None
        return value

    def __repr__(self) -> str:
        if self._inner is None:
            return "<uninit>"
        return f"Lazy(value: {self._inner!r})"

    __str__ = __repr__

    def __bool__(self) -> bool:
        return self.is_initialized

    def __eq__(self, other: object) -> bool:
        if not self.is_initialized:
            return False

        if isinstance(other, Lazy):
            return self._inner == other._inner

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


@typing.final
class LazyFuture(typing.Generic[T]):
    """A thread-safe value that gets lazily initialized at runtime asynchronously.

    This isn't some sort of magic, the inner value is set to `None` when first initialized,
    Then this `None` gets replaced at runtime when calling `LazyFuture.set` method.

    This is a well-known approach used in Python to lazily initialize expensive objects
    that needs to be `None` until it gets initialized with a function call at runtime.

    Example
    -------
    ```py
    @dataclass
    class Config:
        token: Lazy[str] = Lazy()

    @dataclass
    class Application:
        config: Config

    # application entry point.
    def run(app: Application) -> None:
        token = app.config.token.set('token')
        app.run(token=token)
    ```
    """

    __slots__ = ("_inner", "_lock")

    def __init__(self) -> None:
        self._inner: T | None = None
        self._lock: asyncio.Lock | None = None

    @property
    def is_initialized(self) -> bool:
        """Whether the contained value is initialized or not."""
        return self._inner is not None

    @macros.unsafe
    async def get(self) -> Option[T]:
        """Hold ownership of the contained value and return it.

        This ensures that the value is only generated once and kept acquired.
        """
        if self._inner is not None:
            return option.Some(self._inner)

        if not self._lock:
            self._lock = asyncio.Lock()

        async with self._lock:
            if self._inner is not None:
                # inner here is never none.
                return option.Some(self._inner)

        return option.nothing_unchecked()

    def set(self, value: T, /) -> T:
        """Set the contained value to `value`.

        This will clear any ownership of the value until the next `get` call.

        Example
        -------
        ```py
        lazy = LazyFuture()
        print(lazy.set("foo"))
        ```
        """
        self._inner = value
        self._lock = None
        return value

    def __repr__(self) -> str:
        if self._inner is None:
            return "uninit"
        return f"LazyFuture(value: {self._inner!r})"

    __str__ = __repr__

    def __bool__(self) -> bool:
        return self.is_initialized

    def __eq__(self, other: object) -> bool:
        if not self.is_initialized:
            return False

        if isinstance(other, Lazy):
            return self._inner == other._inner  # pyright: ignore

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
