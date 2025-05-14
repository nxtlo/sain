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

__all__ = ("Slice", "SliceMut")

import typing
from collections import abc as collections

from sain import iter as _iter

T = typing.TypeVar("T")


@typing.final
class Slice(typing.Generic[T], collections.Sequence[T]):
    """An immutable view over some sequence of type `T`.

    Similar to `&[T]`

    Parameters
    ----------
    ptr : `collections.Sequence[T]`
        The sequence to point to.
    """

    __slots__ = ("__buf",)

    def __init__(self, ptr: collections.Sequence[T]) -> None:
        self.__buf = ptr

    def into_inner(self) -> collections.Sequence[T]:
        """Consume this `Slice`, returning the sequence that's being pointed to.

        `self` will no longer reference the sequence.

        Example
        -------
        ```py
        def from_parts(slice: Slice[int], len: int) -> list[int]:
            uninit: list[int] = []
            uninit.extend(slice.into_inner()[:len])
            return uninit

        vec = Vec([1, 2, 3, 4])
        new = from_parts(vec.as_ref(), 2)
        assert new == [1, 2]
        ```
        """
        ptr = self.__buf
        del self.__buf
        return ptr

    def iter(self) -> _iter.TrustedIter[T]:
        """Returns an iterator over the slice.

        The iterator yields all items from start to end.

        Example
        -------
        ```py
        x = Vec([1, 2, 3])
        iterator = x.iter()

        assert iterator.next() == Some(1)
        assert iterator.next() == Some(2)
        assert iterator.next() == Some(3)
        assert iterator.next().is_none()
        ```
        """
        return _iter.TrustedIter(self.__buf)

    def __len__(self) -> int:
        return len(self.__buf)

    def __iter__(self) -> collections.Iterator[T]:
        return iter(self.__buf)

    def __repr__(self) -> str:
        return repr(self.__buf)

    @typing.overload
    def __getitem__(self, index: slice) -> Slice[T]: ...

    @typing.overload
    def __getitem__(self, index: int) -> T: ...

    def __getitem__(self, index: int | slice) -> T | Slice[T]:
        if isinstance(index, slice):
            return Slice(self.__buf[index])

        return self.__buf[index]

    def __eq__(self, other: object, /) -> bool:
        return self.__buf == other

    def __ne__(self, other: object, /) -> bool:
        return self.__buf != other


@typing.final
class SliceMut(typing.Generic[T], collections.MutableSequence[T]):
    """A mutable view over some sequence of type `T`.

    Similar to `&mut [T]`

    Parameters
    ----------
    ptr : `collections.MutableSequence[T]`
        The mutable sequence to point to.
    """

    __slots__ = ("__buf",)

    def __init__(self, ptr: collections.MutableSequence[T]) -> None:
        self.__buf = ptr

    def into_inner(self) -> collections.MutableSequence[T]:
        """Consume this `SliceMut`, returning the sequence that's being pointed to.

        `self` will no longer reference the sequence.

        Example
        -------
        ```py
        x = Vec(["x", "y", "z"])

        # mutable reference to `x`
        mut_ref = x.as_mut()
        # make all elements in `x` uppercase, then detach from `mut_ref`.
        mut_ref.into_inner()[:] = [s.upper() for s in mut_ref]

        assert x == ["X", "Y", "Z"]
        ```
        """
        ptr = self.__buf
        del self.__buf
        return ptr

    def iter(self) -> _iter.TrustedIter[T]:
        """Returns an iterator over the slice.

        The iterator yields all items from start to end.

        Example
        -------
        ```py
        x = Vec([1, 2, 3])
        iterator = x.iter()

        assert iterator.next() == Some(1)
        assert iterator.next() == Some(2)
        assert iterator.next() == Some(3)
        assert iterator.next().is_none()
        ```
        """
        return _iter.TrustedIter(self.__buf)

    def insert(self, index: int, value: T) -> None:
        self.__buf.insert(index, value)

    def __len__(self) -> int:
        return len(self.__buf)

    def __iter__(self) -> collections.Iterator[T]:
        return iter(self.__buf)

    def __repr__(self) -> str:
        return repr(self.__buf)

    def __setitem__(self, index: int, item: T) -> None:
        self.__buf.__setitem__(index, item)

    def __delitem__(self, at: int) -> None:
        del self.__buf[at]

    @typing.overload
    def __getitem__(self, index: slice) -> Slice[T]: ...

    @typing.overload
    def __getitem__(self, index: int) -> T: ...

    def __getitem__(self, index: int | slice) -> T | Slice[T]:
        if isinstance(index, slice):
            return Slice(self.__buf[index])

        return self.__buf[index]

    def __eq__(self, other: object, /) -> bool:
        return self.__buf == other

    def __ne__(self, other: object, /) -> bool:
        return self.__buf != other
