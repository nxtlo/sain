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
import copy
from collections import abc as collections

from sain.iter import TrustedIter
from sain.macros import rustc_diagnostic_item
from sain.option import Some

T = typing.TypeVar("T")
T_cov = typing.TypeVar("T_cov", covariant=True)

Pattern = T | collections.Iterable[T]

if typing.TYPE_CHECKING:
    from types import EllipsisType
    from typing import SupportsIndex

    from sain.option import Option

    if sys.version_info >= (3, 11, 0):
        from typing import Self
    else:
        from typing_extensions import Self

    class CoerceSized(typing.Protocol[T_cov]):
        """Trait that indicates that an object that is iterable, while also having a constant length."""

        def __iter__(self) -> collections.Iterator[T_cov]: ...
        def __next__(self) -> T_cov: ...
        def __len__(self) -> int: ...


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

# FIXME[slice-deref]: Should we return `Self` or always `Slice[T]` ?
# ? In Rust, Vec<T> deref to [T], and calling `Vec::split_first`
# ? does not return Option<(&T, Vec<&T>)>, it returns Option<(&T, &[T])>
# ? should we do the same? if yes then we need to create a new Slice(buf)
# ? where buf is a whatever we just sliced out of __buf. This is obviously
# ? a cost for anything other than memoryview's.


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
        x = ...
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

    def last(self) -> Option[T]:
        return Some(self[-1]) if self else Some(None)

    # ? def split(self, pred: F) -> Split[T, F] where F: Callable[[T], bool]: ...
    def split_first(self) -> Option[tuple[T, Self]]:
        if len(self) == 0:
            return Some(None)

        return Some((self.__buf[0], self[1:]))

    def split_last(self) -> Option[tuple[T, Self]]:
        if len(self) == 0:
            return Some(None)

        return Some((self.__buf[-1], self[:-1]))

    def split_off(self, at: int) -> Option[Self]: ...
    def split_once(self) -> Option[tuple[Self, Self]]: ...
    def split_at(self, mid: int) -> tuple[Self, Self]:
        """Divide one slice into two at an index.

        The first will contain all indices from `[0 : mid]` excluding `mid` it self.
        and the second will contain [mid: len], excluding `len` itself.

        if `mid` > `len`, `IndexError` is raised, for non-error version,
        Check `split_at_checked`.

        Example
        -------
        ```py
        ```
        """
        if mid > len(self):
            raise IndexError from None

        return self[0:mid], self[mid:]

    def split_at_checked(self, mid: int) -> tuple[Self, Self]:
        """Divide one slice into two at an index.

        The first will contain all indices from `[0 : mid]` excluding `mid` it self.
        and the second will contain [mid: len], excluding `len` itself.

        if `mid` > `len`, Then all indices will be moved to the left,
        returning an empty indices in right.

        Example
        -------
        ```py
        ```
        """
        return self[0:mid], self[mid:]

    def get(self, index: SupportsIndex) -> Option[T]:
        """Returns a reference to an element at an `index`.

        Return `None` if `index` is out of bounds.

        Example
        -------
        ```py
        ```
        """
        try:
            return Some(self[index.__index__()])
        except IndexError:
            return Some(None)

    def get_unchecked(self, index: SupportsIndex) -> T:
        """Returns a reference to an element at an `index`.

        Raises `KeyError` if `index` is out of bounds.

        Example
        -------
        ```py
        ```
        """
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

    def __len__(self) -> int:
        return len(self.__buf)

    # * defaults

    def __repr__(self) -> str:
        return self.__buf.__repr__()

    def __str__(self) -> str:
        return self.__buf.__str__()

    def __eq__(self, value: collections.Sequence[T], /) -> bool:
        return self.__buf == value

    def __ne__(self, value: collections.Sequence[T], /) -> bool:
        return not self.__eq__(value)

    def __bool__(self) -> bool:
        return bool(self.__buf)


@rustc_diagnostic_item("[T]")
class SliceMut(
    Slice[T],
    # ! we are a mutable *view*, not a mutable sequence.
    # ! we let the concrete impls handle this, like Vec.
    # collections.MutableSequence[T],
):
    """A mutable view over some sequence of type `T`.

    Similar to `[T]` with a mutable `self`.

    Parameters
    ----------
    ptr : `collections.MutableSequence[T]`
        The mutable sequence to point to.
    """

    if typing.TYPE_CHECKING:
        __buf: collections.MutableSequence[T]

    def __init__(self, ptr: collections.MutableSequence[T]) -> None:
        super().__init__(ptr)

    # impl mut [T]

    def fill(self, value: T) -> None:
        """Fills `self` with elements by copying `value`.

        Example
        -------
        ```py
        ```
        """

        if not self.__buf:
            return

        self.__buf[:] = [value] * len(self)

    def fill_with(self, f: collections.Callable[[], T]) -> None:
        """Fills `self` with elements by copying the value returned by `f`.

        This method uses closures to create new value, If you'd rather `copy` a given value, use `fill` instead.

        Example
        -------
        ```py
        ```
        """

        if not self.__buf:
            return

        self.__buf[:] = [f()] * len(self)

    # ? shallow-copies
    def copy_from_slice(self, src: CoerceSized[T]) -> None:
        """Shallow copies he elements from `src` into `self`.

        If you need a deep-copy of `src`'s elements, use `clone_from_slice` instead.

        The length of `src` must be the same as `self`.

        Raises
        ------
        `IndexError`
            If the two slices have different lengths.

        Example
        -------
        ```py
        ```
        """

        if (src_len := len(src)) != (self_len := len(self)):
            raise IndexError(
                f"copy_from_slice: source slice length ({src_len}) does not match destination slice length({self_len})"
            ) from None

        # TODO: Test this vs for i in range(src_len): ...
        self.__buf[:] = [copy.copy(_) for _ in src]

    # ? deep-copies
    def clone_from_slice(self, src: CoerceSized[T]) -> None:
        """Deep copies he elements from `src` into `self`.

        If you only need a shallow-copy of `src`'s elements, use `copy_from_slice` instead.

        The length of `src` must be the same as `self`.

        Raises
        ------
        `IndexError`
            If the two slices have different lengths.

        Example
        -------
        ```py
        ```
        """
        if (src_len := len(src)) != (self_len := len(self)):
            raise IndexError(
                f"copy_from_slice: source slice length ({src_len}) does not match destination slice length({self_len})"
            ) from None

        # TODO: Test this vs for i in range(src_len): ...
        self.__buf[:] = [copy.deepcopy(_) for _ in src]

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

    # ? def split_mut(self, pred: F) -> SplitMut[T, F] where F: Callable[[T], bool]: ...
    def split_first_mut(self) -> Option[tuple[T, Self]]:
        if len(self) == 0:
            return Some(None)

        return Some((self.__buf[0], self[1:]))

    def split_last_mut(self) -> Option[tuple[T, Self]]:
        if len(self) == 0:
            return Some(None)

        return Some((self.__buf[-1], self[:-1]))

    def split_off_mut(self, at: int) -> Option[Self]: ...
    def split_at_mut(self, mid: int) -> tuple[Self, Self]:
        """Divide one slice into two at an index.

        The first will contain all indices from `[0 : mid]` excluding `mid` it self.
        and the second will contain [mid: len], excluding `len` itself.

        if `mid` > `len`, `IndexError` is raised, for non-error version,
        Check `split_at_mut_checked`.

        Example
        -------
        ```py
        ```
        """
        if mid > len(self):
            raise IndexError from None

        return self[0:mid], self[mid:]

    def split_at_mut_checked(self, mid: int) -> Option[tuple[Self, Self]]:
        """Divide one slice into two at an index.

        The first will contain all indices from `[0 : mid]` excluding `mid` it self.
        and the second will contain [mid: len], excluding `len` itself.

        if `mid` > `len`, `IndexError` is raised, for non-error version,
        Check `split_at_checked`.

        Example
        -------
        ```py
        ```
        """
        if mid > len(self):
            return Some(None)

        return Some((self[0:mid], self[mid:]))

    def insert(self, index: int, value: T) -> None:
        self.__buf.insert(index, value)

    def __setitem__(self, index: int, item: T) -> None:
        self.__buf.__setitem__(index, item)

    def __delitem__(self, at: int) -> None:
        del self.__buf[at]
