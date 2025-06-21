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
"""A wrapper type to construct uninitialized instances of T."""

from __future__ import annotations

import typing

from . import macros
from .macros import rustc_diagnostic_item

if typing.TYPE_CHECKING:
    import collections.abc as collections

    from typing_extensions import Self

T = typing.TypeVar("T")


@rustc_diagnostic_item("MaybeUninit")
@typing.final
class MaybeUninit(typing.Generic[T]):
    """A wrapper type to construct uninitialized instances of `T`.

    This is kinda equivalent to Rust's `MaybeUninit<T>` wrapper.

    The difference is what's happening under the hood is when initializing an instance of this object,
    nothing really is being initialized, until you call `.write()` to initialize the inner value.

    What??
    -----
    Ok, so `MaybeUninit<T>` is in a sense the unsafe equivalent of `Option<T>`, it either contains a value of type `T`,
    or it contains uninitialized memory (`the attribute doesn't exist`).

    However, `MaybeUninit` is unable to tell you whether the value it contains is `Some(T)` or `None`, So you
    as a programmer is responsible for initializing it.

    And by default, `Option<T>` always contain a default value, which is `None`.

    Examples
    --------
    ```py
    # Let's write a simple wrapper around `MaybeUninit<T>` to create a dynamic array.
    class SizedArray[T]:
        def __init__(self, size: int) -> None:
            # Creates count `size` of `MaybeUninit<T>` in an uninitialized state.
            self.buf = MaybeUninit[T].uninit_array(size)
            # Track how many initialized elements are in the array.
            self.len = 0

        def push(self, value: T) -> None:
            # if the length of the array is equal to the size of the array,
            # then we've reached the max size of the array.
            if self.len == len(self.buf):
                raise RuntimeError("max size reached")

            # get the next uninitialized element and write into it.
            self.buf[self.len].write(value)
            self.len += 1

        def copy_from(self, other: Sequence[T]) -> None:
            # get the remaining space in the array.
            spared = self.buf[self.len:]
            other_len = len(other)
            # Check if there's enough capacity to copy the other list into the array.
            if len(spared) < other_len:
                raise RuntimeError("not enough space")

            # Copy the other list into the array.
            index = 0
            while index < other_len:
                self.buf[self.len + index].write(other[index])
                index += 1

            self.len += other_len

        def read(self) -> Sequence[T]:
            return MaybeUninit.array_assume_init(self.buf[:self.len])

    array = SizedArray[int](3)
    array.push(1)
    array.copy_from([2, 3])
    assert array.read() == (1, 2, 3)
    ```
    """

    __slots__ = ("__value",)

    @typing.overload
    def __init__(self) -> None: ...

    @typing.overload
    def __init__(self, value: T) -> None:
        """Creates a new MaybeUninit<T> initialized with the given value.
        It is safe to call assume_init on the return value of this function.

        Example
        -------
        ```py
        v = MaybeUninit(1)
        assert v.assume_init() == 1
        ```
        """

    def __init__(self, value: T | None = None) -> None:
        if value is None:
            return None
        else:
            # we simply pre-initialize the value if it was passed
            # when constructing the instance.
            self.__value = value

    @classmethod
    def uninit(cls) -> Self:
        """Creates a new `MaybeUninit<T>` in an uninitialized state.

        Example
        -------
        ```py
        v: MaybeUninit[str] = MaybeUninit.uninit() # or just MaybeUninit()
        ```
        """
        return cls()

    @classmethod
    def uninit_array(cls, n: int) -> collections.Sequence[Self]:
        """Creates an immutable sequence of `MaybeUninit<T>` in an uninitialized state.

        Example
        -------
        ```py
        v = MaybeUninit[str].uninit_array(3)
        assert len(v) == 3
        for uninit in v:
            uninit.write('content')

            initialized = uninit.assume_init()
        ```
        """
        return tuple(cls() for _ in range(n))

    @macros.unsafe
    def assume_init(self) -> T:
        """Get the inner value, assuming that it was initialized by the caller.

        It is unsafe and undefined behavior to call this method on an uninitialized state,

        Example
        -------
        ```py
        uninit: MaybeUninit[int] = MaybeUninit.uninit()
        val = uninit.assume_init() # This is UNSAFE ⚠️

        # Initialize it first.
        uninit.write(0)
        val = uninit.assume_init() # This is safe to access.
        ```
        """
        # SAFETY: the caller must guarantee that `self` is initialized.
        return self.__value

    @staticmethod
    @macros.unsafe
    def array_assume_init(
        array: collections.Sequence[MaybeUninit[T]],
    ) -> collections.Sequence[T]:
        """Extracts a sequence of `MaybeUninit[T]` containers.

        You must guarantee that all elements in the array are initialized.

        Example
        -------
        ```py
        array: list[MaybeUninit[int]] = [MaybeUninit(), MaybeUninit(), MaybeUninit()]
        array[0].write(0)
        array[1].write(1)
        array[2].write(2)
        # transposed into a tuple.
        assert MaybeUninit.array_assume_init(array) == (0, 1, 2)
        ```
        """
        # SAFETY: The caller guarantees that all elements of the array are initialized
        return tuple(uninit.assume_init() for uninit in array)

    @staticmethod
    @macros.unsafe
    def array_assume_init_mut(
        array: collections.Sequence[MaybeUninit[T]],
    ) -> collections.MutableSequence[T]:
        """Extracts a sequence of `MaybeUninit[T]` to a list of `T`s.

        You must guarantee that all elements in the array are initialized.

        Example
        -------
        ```py
        array: list[MaybeUninit[int]] = [MaybeUninit(), MaybeUninit(), MaybeUninit()]
        array[0].write(0)
        array[1].write(1)
        array[2].write(2)
        # transposed into a list.
        assert MaybeUninit.array_assume_init_mut(array) == [0, 1, 2]
        ```
        """
        # SAFETY: The caller guarantees that all elements of the array are initialized
        return [uninit.assume_init() for uninit in array]

    def write(self, value: T) -> T:
        """Sets the value of the `MaybeUninit[T]`, Then return a reference to it.

        This will overwrite any previous values, if was initialized.

        Example
        -------
        ```py
        buffer: MaybeUninit[bytes] = MaybeUninit()
        buffer.write(b"Hello, World!")
        print(buffer.assume_init())
        ```
        """
        self.__value = value
        # SAFETY: we just initialized the value, so it's safe to access.
        return self.__value

    def __repr__(self) -> str:
        if self:
            return f"MaybeUninit(value: {self.__value!r})"
        return "<uninit>"

    __str__ = __repr__

    def __bool__(self) -> bool:
        """Perform a boolean check on whether the value is initialized or not.

        Example
        -------
        ```py
        v = MaybeUninit[bool]()
        assert not v
        ```
        """
        return hasattr(self, "_MaybeUninit__value")

    def __hash__(self) -> int:
        return self.__value.__hash__()
