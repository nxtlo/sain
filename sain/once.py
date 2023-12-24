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

from __future__ import annotations

__all__ = ("Once",)

import _thread
import typing

from . import option as _option

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

    # Not initialized yet
    GLOBAL_UUID: Once[UUID] = Once()

    def run_application():
        # This will init the uuid if its not set or return it if it already is.
        uuid = GLOBAL_UUID.get_or_init(uuid4())
        app = Application(token=uuid)
        # Attempting to write to the initialized uuid will raise runtime error.
        GLOBAL_UUID.set(uuid4())  # Value is already set. Can't reset it.
    ```
    """

    __slots__ = ("_inner", "_lock", "_blocking")

    def __init__(self, *, blocking: bool = True) -> None:
        self._blocking = blocking
        self._lock: _thread.LockType | None = None
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

        self._inner = origin = self.get_or_init(v)
        self._lock = None
        return origin

    def clear(self) -> None:
        self._lock = None
        self._inner = None

    def get_or_init(self, f: T) -> T:
        """Get the value if its not `None`, Otherwise call `f()` setting the value and returning it."""

        # If the value is not empty we return it immediately.
        if self._inner is not None:
            return self._inner

        if self._lock is None:
            self._lock = _thread.allocate_lock()

        try:
            self._lock.acquire(blocking=self._blocking)
            self._inner = f
            return self._inner
        finally:
            self._lock.release()

    def __repr__(self) -> str:
        return f"Once(value: {self._inner})"

    def __str__(self) -> str:
        return str(self._inner)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Once):
            return NotImplemented

        return self._inner == __value._inner

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)

    def __bool__(self) -> bool:
        return self.is_set
