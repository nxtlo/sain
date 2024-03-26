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

"""A synchronization primitive which can be written to only once."""

from __future__ import annotations

__all__ = ("Once", "AsyncOnce")

import asyncio
import threading
import typing

from sain import option as _option

if typing.TYPE_CHECKING:
    from sain import Option

T = typing.TypeVar("T")


@typing.final
class Once(typing.Generic[T]):
    """A synchronization primitive which can be written to only once.

    Example
    -------
    ```py
    from sain.once import Once
    from uuid import uuid4, UUID

    class Application:
        # Not initialized yet
        uuid: Once[UUID] = Once()

        def send(self, id: UUID) -> None:
            ...

    def spawn(app: Application) -> None:
        app.uuid.get().is_none() # True
        uid = app.uuid.get_or(uuid4())
        app.send(uid)

    def run_application():
        # This will init the uuid if its not set or return it if it already is.
        app = Application()
        thread = threading.Thread(target=spawn, args=(app,))
        thread.start()

        app.uuid.get().is_some()  # True
    ```
    """

    __slots__ = ("_inner", "_lock")

    def __init__(self) -> None:
        self._lock: threading.Lock | None = None
        self._inner: T | None = None

    @property
    def is_set(self) -> bool:
        return self._inner is not None

    def get(self) -> Option[T]:
        """Gets the stored value.

        `Option(None)` is returned if nothing is stored. This method will never block.
        """
        return _option.Some(self._inner)

    def set(self, v: T) -> T:
        """Set the const value if its not set.

        This method may block if another thread is trying to access it.

        Raises
        ------
        `RuntimeError`
            If the value is already set. This will get raised.
        """
        if self._inner is not None:
            raise ValueError("Value is already set.")

        self._inner = origin = self.get_or(v)
        self._lock = None
        return origin

    def clear(self) -> None:
        """Clear the inner value, Setting it to `None`."""
        self._lock = None
        self._inner = None

    def get_or(self, f: T) -> T:
        """Get the value if its not `None`, Otherwise set `f` value and returning it."""

        # If the value is not empty we return it immediately.
        if self._inner is not None:
            return self._inner

        if self._lock is None:
            self._lock = threading.Lock()

        with self._lock:
            self._inner = f
            return self._inner

    def __repr__(self) -> str:
        return f"Once(value: {self._inner})"

    def __str__(self) -> str:
        return str(self._inner)

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Once):
            return self._inner == __value._inner  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]

        if isinstance(self._inner, type(__value)):
            return __value == self._inner

        return NotImplemented

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)

    def __bool__(self) -> bool:
        return self.is_set


@typing.final
class AsyncOnce(typing.Generic[T]):
    """A synchronization primitive which can be written to only once.

    This is an `async` version of `Once`.

    Example
    -------
    ```py
    from sain.once import Once
    from uuid import uuid4, UUID

    class Application:
        # Not initialized yet
        uuid: Once[UUID] = Once()

        async def send(self, id: UUID) -> None:
            ...

    async def spawn(app: Application) -> None:
        app.uuid.get().is_none() # True
        uid = await app.uuid.get_or(uuid4())
        await app.send(uid)

    def run_application():
        # This will init the uuid if its not set or return it if it already is.
        app = Application()
        tasks = (asyncio.create_task(spawn(app)) for _ in range(2))
        await asyncio.gather(*tasks)

        app.uuid.get().is_some()  # True
    ```
    """

    __slots__ = ("_inner", "_lock")

    def __init__(self) -> None:
        self._lock: asyncio.Lock | None = None
        self._inner: T | None = None

    @property
    def is_set(self) -> bool:
        return self._inner is not None

    def get(self) -> Option[T]:
        """Gets the stored value.

        `Option(None)` is returned if nothing is stored. This method will never block.
        """
        return _option.Some(self._inner)

    async def set(self, v: T) -> T:
        """Set the const value if its not set.

        Raises
        ------
        `RuntimeError`
            If the value is already set. This will get raised.
        """
        if self._inner is not None:
            raise ValueError("Value is already set.")

        self._inner = origin = await self.get_or(v)
        self._lock = None
        return origin

    def clear(self) -> None:
        self._lock = None
        self._inner = None

    async def get_or(self, f: T) -> T:
        """Get the value if its not `None`, Otherwise set `f` value and returning it."""

        # If the value is not empty we return it immediately.
        if self._inner is not None:
            return self._inner

        if self._lock is None:
            self._lock = asyncio.Lock()

        async with self._lock:
            self._inner = f
            return self._inner

    def __repr__(self) -> str:
        return f"Once(value: {self._inner})"

    def __str__(self) -> str:
        return str(self._inner)

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Once):
            return self._inner == __value._inner  # pyright: ignore

        if isinstance(self._inner, type(__value)):
            return __value == self._inner

        return NotImplemented

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)

    def __bool__(self) -> bool:
        return self.is_set
