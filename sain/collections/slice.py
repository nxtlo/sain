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

__all__ = ("Slice", "SliceMut", "SpecContains")

import sys
import typing
from collections import abc as collections

from sain.iter import TrustedIter
from sain.macros import rustc_diagnostic_item
from sain.option import Some

T = typing.TypeVar("T")


Pattern = T | collections.Iterable[T]

if typing.TYPE_CHECKING:
    from types import EllipsisType
    from typing import SupportsIndex

    from sain.option import Option

    if sys.version_info >= (3, 11, 0):
        from typing import Self
    else:
        from typing_extensions import Self


class SpecContains(typing.Generic[T]):
    """Provides a default `contains` method."""

    __slots__ = ()

    @typing.final
    def contains(self: collections.Container[T], pat: Pattern[T]) -> bool:
        """Check if `pat` is contained in `self`.

        `pat` here can be either an element of type `T` or an iterable of type `T`.

        If an iterable is passed, it will check if at least one of the elements is in `self`.

        Example
        -------
        ```py
        vec = Vec([1, 2, 3, 4])
        assert vec.contains(1) is True
        assert vec.contains([3, 4]) is True
        assert vec.contains(map(int, ['1', '2'])) is True
        ```

        The implementation is roughly this simple:
        ```py
        if isinstance(pat, Iterable):
            return any(_ in sequence for _ in pat)
        return pat in sequence
        ```
        """
        if isinstance(pat, collections.Iterable):
            return any(_ in self for _ in pat)  # pyright: ignore - bad type inference.

        return pat in self


# TODO: Lots of documentation.


@rustc_diagnostic_item("[T]")
class Slice(typing.Generic[T], collections.Sequence[T], SpecContains[T]):
    """An immutable view over some sequence of type `T`.

    Similar to `[T]`

    Parameters
    ----------
    ptr : `collections.Sequence[T]`
        The sequence to point to.
    """

    __slots__ = ("__buf",)

    def __init__(self, ptr: collections.Sequence[T]) -> None:
        self.__buf = ptr

    # impl [T]

    def iter(self) -> TrustedIter[T]:
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
        return TrustedIter(self.__buf)

    def len(self) -> int:
        return len(self.__buf)

    def is_empty(self) -> bool:
        return not self.__buf

    def first(self) -> Option[T]:
        return Some(self[0]) if self else Some(None)

    def split_first(self) -> Option[tuple[T, Self]]: ...

    def last(self) -> Option[T]:
        return Some(self[-1]) if self else Some(None)

    def split_last(self) -> Option[tuple[T, Self]]: ...

    def split_at(self, mid: int) -> tuple[Self, Self]:
        """Divide one slice into two at an index.

        The first will contain all indices from `[0 : mid]` excluding `mid` it self.
        and the second will contain [mid: len], excluding `len` itself.

        if `mid` > `len`, `IndexError` is raised, for non-error version,
        Check `split_at_checked`.

        Example
        -------
        ```py
        buffer = Bytes.from_bytes((1, 2, 3, 4))
        left, right = buffer.split_at(0)
        assert left == [] and right == [1, 2, 3, 4]

        left, right = buffer.split_at(2)
        assert left == [1, 2] and right == [2, 3]
        ```
        """
        if mid > len(self):
            raise IndexError from None

        return self[0:mid], self[mid:]

    def split_at_checked(self, mid: int) -> tuple[Self, Self]:
        """Divide one slice into two at an index.

        The first will contain all indices from `[0 : mid]` excluding `mid` it self.
        and the second will contain [mid: len], excluding `len` itself.

        if `mid` > `len`, Then all bytes will be moved to the left,
        returning an empty bytes in right.

        Example
        -------
        ```py
        buffer = Bytes.from_bytes((1, 2, 3, 4))
        left, right = buffer.split_at(0)
        assert left == [] and right == [1, 2, 3, 4]

        left, right = buffer.split_at(2)
        assert left == [1, 2] and right == [2, 3]
        ```
        """
        return self[0:mid], self[mid:]

    def get(self, index: SupportsIndex) -> Option[T]:
        opt: Option[T] = Some(None)
        try:
            opt.insert(self[index.__index__()])
        except IndexError:
            pass
        return opt

    def get_unchecked(self, index: SupportsIndex) -> T:
        return self[index.__index__()]

    # NOTE - Delegates `self` to whatever we're pointing to.

    # * impl Sequence[T] *

    @typing.overload
    def __getitem__(self, index: int) -> T: ...
    @typing.overload
    def __getitem__(self, index: slice) -> Self: ...
    @typing.overload
    def __getitem__(self, index: EllipsisType) -> Self: ...

    def __getitem__(self, index: int | slice | EllipsisType) -> Self | T:
        if index is ...:
            # Full slice self[...], creates another reference to __buf
            return self.__class__(self.__buf)

        if isinstance(index, slice):
            # Slicing like self[1:], self[:2], self[1:2]
            return self.__class__(self.__buf[index])

        else:
            # index get item. self[0]
            return self.__buf[index]

    def index(self, value: T, start: int = 0, stop: int = sys.maxsize) -> int:
        return self.__buf.index(value, start, stop)

    def count(self, value: T) -> int:
        return self.__buf.count(value)

    # * impl Iterable[T] *
    def __iter__(self) -> collections.Iterable[T]:
        return iter(self.__buf)

    # * impl Container[T] *
    def __contains__(self, item: T) -> bool:
        return item in self.__buf

    # * impl Sized *
    def __len__(self) -> int:
        return len(self.__buf)

    # * impl Reversible[T] *
    def __reversed__(self) -> collections.Iterator[T]:
        return reversed(self.__buf)

    def __bool__(self) -> bool:
        return bool(self.__buf)

    # * defaults

    def __repr__(self) -> str:
        return self.__buf.__repr__()

    __str__ = __repr__

    def __eq__(self, value: collections.Sequence[T], /) -> bool:
        return self.__buf == value

    def __ne__(self, value: collections.Sequence[T], /) -> bool:
        return not self.__eq__(value)


@rustc_diagnostic_item("[T]")
class SliceMut(Slice[T], collections.MutableSequence[T]):
    """A mutable view over some sequence of type `T`.

    Similar to `[T]` with a mutable `self`.

    Parameters
    ----------
    ptr : `collections.MutableSequence[T]`
        The mutable sequence to point to.
    """

    __slots__ = ("__buf",)

    if typing.TYPE_CHECKING:
        __buf: collections.MutableSequence[T]

    def __init__(self, ptr: collections.MutableSequence[T]) -> None:
        super().__init__(ptr)

    # impl mut [T]

    def swap(self, a: int, b: int):
        """Swap two elements in the slice.

        if `a` equals to `b` then it's guaranteed that elements won't change value.

        Example
        -------
        ```py
        ```

        Parameters
        ----------
        `a` : `int`
            The index of the first element
        `b` : `int`
            The index of the second element

        Raises
        ------
        IndexError
            If the positions of `a` or `b` are out of index.
        """
        if self[a] == self[b]:
            return

        self[a], self[b] = self[b], self[a]

    def swap_unchecked(self, a: int, b: int):
        """Swaps two elements in the slice. without checking if `a` == `b`.

        Example
        -------
        ```py
        ```

        Parameters
        ----------
        `a` : `int`
            The index of the first element
        `b` : `int`
            The index of the second element

        Raises
        ------
        IndexError
            If the positions of `a` or `b` are out of index.
        """
        self[a], self[b] = self[b], self[a]

    # TODO - add docs
    def reverse(self) -> None:
        self.__buf.reverse()

    def insert(self, index: int, value: T) -> None:
        self.__buf.insert(index, value)

    def __setitem__(self, index: int, item: T) -> None:
        self.__buf.__setitem__(index, item)

    def __delitem__(self, at: int) -> None:
        del self.__buf[at]
