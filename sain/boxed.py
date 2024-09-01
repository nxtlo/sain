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


"""a `Box` is a wrapper around a value that expires after the given amount of time."""

from __future__ import annotations

__all__ = ("Box",)

import asyncio
import datetime
import math
import time
import typing

from . import futures
from . import option

if typing.TYPE_CHECKING:
    from collections import abc as collections

    from typing_extensions import Self

    from . import Option

T = typing.TypeVar("T", covariant=True)


@typing.final
class Box(typing.Generic[T]):
    """The box object for expiring data. not thread-safe.

    A box is an object that contains a value of type `T` which expires it after the given amount of time,
    The box won't start expiring the data until its first access with `Box.get` method.

    Example
    -------
    ```py
    # Initializing a box doesn't mean it started expiring. instead,
    # getting the value the first time will start the process.
    cache: dict[str, Box[int]] = {"sora": Box(999, timedelta(seconds=5)}

    # first start expiring here.
    cache["sora"].get().unwrap()
    time.sleep(6)
    assert cache["sora"].has_expired()
    ```
    """

    __slots__ = ("_inner", "_expire_in", "_on_expire", "_mono")

    def __init__(self, value: T, expire_in: int | float | datetime.timedelta) -> None:
        if isinstance(expire_in, datetime.timedelta):
            expire_in = expire_in.total_seconds()
        else:
            expire_in = float(expire_in)

        if expire_in <= 0:
            raise ValueError("expire_in must be more than 0 seconds.")

        # We set the last call on the first access to the value.
        self._mono: float | None = None
        self._inner: Option[T] = option.Some(value)
        self._on_expire: collections.Callable[[T], typing.Any] | None = None
        self._expire_in = expire_in

    @property
    def has_expired(self) -> bool:
        """Returns True if the value has expired."""
        # return self._mono is not None and not self._expire_in <= (
        # time.monotonic() - self._mono
        # )
        return self._mono is not None and (
            not self._mono or self._expire_in <= (time.monotonic() - self._mono)
        )

    def on_expire(self, callback: collections.Callable[[T], typing.Any]) -> Self:
        """Set a callback that will be invoked when this value gets expired.

        Both async and sync callbacks are supported.

        Example
        -------
        ```py
        async def sink(message: str) -> None:
            await client.create_message(message)
            print("Sinked", message)

        box = Box("bluh", 5).on_expire(sink)

        while box.get().is_some():
            time.sleep(5)
        ```
        First `.get` call on an expired box, the `sink` callback will be invoked,
        also the inner value will be set to `Some(None)`.

        After 5 seconds.
        ```py
        assert box.get() == Some("bluh") # This last call invokes the callback.
        # Sinked bluh
        assert box.get().is_none()
        ```
        """
        self._on_expire = callback
        return self

    def remaining(self) -> float:
        """Returns when this box will expire in seconds.

        Example
        --------
        ```py
        jogo = Box("jogo", 3)
        assert jogo.get().unwrap() == "jogo"

        time.sleep(1)
        assert jogo.remaining() == 2
        ```
        """
        if not self._mono:
            return 0.0

        return math.floor(
            (self._expire_in - (time.monotonic() - self._mono) + 1) * 0.99
        )

    def get(self) -> Option[T]:
        """Get the contained value if it was not expired, otherwise `Some(None)` is returned.

        Example
        -------
        ```py
        pizza = Box("pizza", timedelta(days=1))

        while not pizza.get().is_none():
            # Do stuff with the value while its not expired.

        # After 1 day.
        assert pizza.get().is_none()
        ```
        """
        if self.has_expired:
            if self._on_expire is not None:
                try:
                    if asyncio.iscoroutinefunction(self._on_expire):
                        futures.loop().run_until_complete(
                            self._on_expire(self._inner.unwrap_unchecked())
                        )
                    else:
                        self._on_expire(self._inner.unwrap_unchecked())
                finally:
                    self._on_expire = None

            self._inner.take()
            self._mono = None
            # SAFETY: The value is expired, therefore we always return None.
            return option.NOTHING  # pyright: ignore

        if self._mono is None:
            self._mono = time.monotonic()

        return self._inner

    def __repr__(self) -> str:
        return f"Box(value: {self._inner}, expired: {self.has_expired})"

    __str__ = __repr__

    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, Box):
            return NotImplemented

        return (
            self._inner == value._inner
            and not self.has_expired
            and not value.has_expired
        )

    def __ne__(self, value: object, /) -> bool:
        return not self.__eq__(value)

    def __hash__(self) -> int:
        return hash(self._inner)

    def __bool__(self) -> bool:
        return not self.has_expired
