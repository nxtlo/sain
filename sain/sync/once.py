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

from sain import macros
from sain import option as _option
from sain import result as _result

if typing.TYPE_CHECKING:
    import collections.abc as collections

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

    UUID: Once[UUID] = Once()

    def start() -> None:
        assert UUID.get().is_none()

        # First initialization.
        UUID.get_or(uuid4()) # some-uuid

        # Won't set, returns the same uuid that got initialized first.
        UUID.get_or(uuid4()) # some-uuid
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
        """Gets the stored value, returning `None` if not initialized.

        This method will never block.
        """
        return _option.Some(self._inner) if self.is_set else _option.nothing_unchecked()

    @macros.unsafe
    def get_unchecked(self) -> T:
        """Get the contained value without checking if it was initialized.

        Example
        -------
        ```py
        cell = Once[float]()
        inner = cell.get_unchecked() # Undefined Behavior!!

        # Initialize it first.
        cell.get_or(math.sqrt(2.0))

        # At this point of the program,
        # it is guaranteed that the value is initialized.
        inner = cell.get_unchecked()
        ```
        """
        # SAFETY: The caller guarantees that the value is initialized.
        return self.get().unwrap_unchecked()

    def set(self, v: T) -> _result.Result[None, T]:
        """Set the const value if its not set. returning `T` if its already set.

        This method may block if another thread is trying to initialize the value.
        The value is guaranteed to be set, just not necessarily the one provided.

        Example
        --------
        ```py
        flag = Once[bool]()
        # flag is empty.
        assert flag.get_or(True) is True.

        # flag is not empty, so it returns the value we set first.
        assert flag.set(False) == Err(True)
        ```

        Returns
        -------
        `sain.Result[None, T]`
            This cell returns `Ok(None)` if it was empty. otherwise `Err(T)` if it was full.
        """
        if self._inner is not None:
            return _result.Err(self._inner)

        self._inner = self.get_or(v)
        self._lock = None
        return _result.Ok(None)

    def clear(self) -> None:
        """Clear the inner value, Setting it to `None`."""
        self._lock = None
        self._inner = None

    def get_or(self, init: T) -> T:
        """Get the value if it was not initialized, Otherwise set `init` value and returning it.

        Many threads may call `get_or` concurrently with different
        initializing functions, but it is guaranteed that only one function
        will be executed.

        Example
        -------
        ```py
        UUID: Once[UUID] = Once()

        def main() -> None:
            assert UUID.get().is_none()

            # First initialization.
            UUID.get_or(uuid4()) # some-uuid

            # Won't set, returns the same uuid that got initialized first.
            UUID.get_or(uuid4()) # some-uuid
            ```
        """

        # If the value is not empty we return it immediately.
        if self._inner is not None:
            return self._inner

        if self._lock is None:
            self._lock = threading.Lock()

        with self._lock:
            self._inner = init
            return init

    def get_or_with(self, f: collections.Callable[..., T]) -> T:
        """Gets the contents of the cell, initializing it with `f` if the cell
        was empty.

        Many threads may call `get_or_with` concurrently with different
        initializing functions, but it is guaranteed that only one function
        will be executed.

        Examples
        --------
        ```py
        cell = Once[int]()
        value = cell.get_or_with(lambda: 92)
        assert value == 92

        value = cell.get_or_with(lambda: 0)
        assert value == 92
        ```
        """
        # If the value is not empty we return it immediately.
        if self._inner is not None:
            return self._inner

        if self._lock is None:
            self._lock = threading.Lock()

        with self._lock:
            v = f()
            self._inner = v
            return v

    def into_inner(self) -> T | None:
        return self.get().into_inner()

    def __repr__(self) -> str:
        if not self.is_set:
            return "<uninit>"

        return f"Once(inner: {self._inner!r})"

    __str__ = __repr__

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Once):
            return self._inner == __value._inner  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]

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

    # A global uuid
    UUID: AsyncOnce[UUID] = AsyncOnce()

    async def start() -> None:
        assert UUID.get().is_none()
        # First initialization.
        await UUID.get_or(uuid4()) # some-uuid
        # Won't set, returns the same uuid that got initialized first.
        await UUID.get_or(uuid4()) # some-uuid
    ```
    """

    __slots__ = ("_inner", "_lock")

    def __init__(self) -> None:
        self._lock: asyncio.Lock | None = None
        self._inner: T | None = None

    @property
    def is_set(self) -> bool:
        """Whether this inner value has ben initialized or not."""
        return self._inner is not None

    def get(self) -> Option[T]:
        """Gets the stored value. `Some(None)` is returned if nothing is stored.

        This method will never block.
        """
        return _option.Some(self._inner)

    @macros.unsafe
    def get_unchecked(self) -> T:
        """Get the contained value without checking if it was initialized.

        Example
        -------
        ```py
        cell = AsyncOnce[float]()
        inner = cell.get_unchecked() # Undefined Behavior!!

        # Initialize it first.
        cell.get_or(math.sqrt(2.0))

        # At this point of the program,
        # it is guaranteed that the value is initialized.
        inner = cell.get_unchecked()
        ```
        """
        # SAFETY: The caller guarantees that the value is initialized.
        return self.get().unwrap_unchecked()

    async def set(self, v: T) -> _result.Result[None, T]:
        """Set the const value if its not set. returning `T` if its already set.

        if another thread is trying to initialize the value, The value is guaranteed to be set,
        just not necessarily the one provided.

        Example
        --------
        ```py
        flag = AsyncOnce[bool]()
        # flag is empty.
        assert await flag.get_or(True) is True.
        # flag is not empty, so it returns the value we set first.
        assert await flag.set(False) == Err(True)
        ```

        Returns
        -------
        `sain.Result[None, T]`
            This cell returns `Ok(None)` if it was empty. otherwise `Err(T)` if it was full.
        """
        if self._inner is not None:
            return _result.Err(self._inner)

        self._inner = await self.get_or(v)
        self._lock = None
        return _result.Ok(None)

    def clear(self) -> None:
        """Clear the inner value, Setting it to `None`."""
        self._lock = None
        self._inner = None

    async def get_or(self, init: T) -> T:
        """Gets the contents of the cell, initializing it with `init` if the cell
        was empty.

        Many threads may call `get_or` concurrently with different
        initializing functions, but it is guaranteed that only one function
        will be executed.

        Examples
        --------
        ```py
        from sain.sync import AsyncOnce

        cell = AsyncOnce[int]()
        value = await cell.get_or(92)
        assert value == 92

        value = await cell.get_or(0)
        assert value == 92
        ```
        """
        # If the value is not empty we return it immediately.
        if self._inner is not None:
            return self._inner

        if self._lock is None:
            self._lock = asyncio.Lock()

        async with self._lock:
            self._inner = init
            return init

    async def get_or_with(self, f: collections.Callable[..., T]) -> T:
        """Gets the contents of the cell, initializing it with `f` if the cell
        was empty.

        Many threads may call `get_or_with` concurrently with different
        initializing functions, but it is guaranteed that only one function
        will be executed.

        Examples
        --------
        ```py
        from sain.sync import AsyncOnce

        cell = AsyncOnce[int]()
        value = await cell.get_or_with(lambda: 92)
        assert value == 92

        value = await cell.get_or_init(lambda: 0)
        assert value == 92
        ```
        """
        # If the value is not empty we return it immediately.
        if self._inner is not None:
            return self._inner

        if self._lock is None:
            self._lock = asyncio.Lock()

        async with self._lock:
            v = f()
            self._inner = v
            return v

    def __repr__(self) -> str:
        if self._inner is not None:
            return f"AsyncOnce(value: {self._inner})"
        return "<async_uninit>"

    __str__ = __repr__

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, AsyncOnce):
            return self._inner == __value._inner  # pyright: ignore

        return NotImplemented

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)

    def __bool__(self) -> bool:
        return self.is_set
