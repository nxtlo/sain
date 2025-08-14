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

"""A dynamically-sized view into a contiguous sequence of elements.

The most fundamental types already implement `Slice` and `SliceMut` which are `Vec`, `Bytes` and `BytesMut` respectively.

Slices are views into any sequence object, represented as a pointer to the data.

# Overview

```py
from sain import Vec

v = Vec([1, 2, 3, 4])
# slicing a vec.
int_slice = v[...] # or v.as_slice()
```

Slices are either mutable (`SliceMut`) or immutable (`Slice`), depending on the type of the sequence they're storing.

```py
from sain.collections.slice import SliceMut, Slice

some_data = ['a', 'b', 'c']
x = SliceMut(some_data) # point to `some_data`.
x[0] = 'z' # change the first element to 'z'.
assert some_data == ['z', 'b', 'c'] # the original data is changed.

# But, we cannot create a mutable slice from an immutable data structure.
y = SliceMut((1, 2, 3, 4)) # This is an actual runtime error. you can't mutate a tuple.
```

## Layout

A `Slice` or a `SliceMut` keeps a pointer to the shared state containing the full data of the sequence.

`Slice`'s special methods coerces to pointed-to magic methods,

For an example. If `x` is a slice of `list`, then `x == list` is valid, and `hash(x)` is the same as `hash(list)`.

This is a list of the delegated methods:

* `__getitem__`, slicing returns a `Slice|Mut`, not the pointed-to type.
* `__len__`
* `__repr__`
* `__str__`
* `__eq__`
* `__ne__`
* `__lt__`
* `__gt__`
* `__le__`
* `__ge__`
* `__bool__`
* `__hash__`

...and the rest of `Sequence` provided methods, such as `__iter__`, `__contains__`, etc.

However, `__copy__` simply just returns a new slice pointing to the same data. You can override this behavior.

## Iteration

Just like any other sequence, slices implement the `Iterator` protocol,
allowing you to iterate over them with a `for` loop.

Slices also provide a `Slice.iter` method which is an explicit method to return a `sain.Iterator`.

```py
numbers = Slice([1, 2, 3, 4])
for number in numbers:
    print(number)

# ...or
total = numbers.iter().fold(0, lambda acc, x: acc + x)
assert total == 10
```

## Zero-copy Guarantees

Slices use the pointed-to type's `__getitem__` implementation, some data structures provide zero-copy slicing operations,
such as `memoryview`, `array` and `Bytes`.

If you have a slice of `memoryview` or `Bytes`, you get free zero-copy slicing.

```py
from sain import Slice

some_bytes = b"hello, world!"
s = Slice(memoryview(some_bytes))

# Split the bytes into two parts.
# * the first part is the first byte: b"h"
# * the second part is the rest of the bytes: b"ello, world!"
# This is a doesn't cost anything.

header, trailer = s.split_first().unwrap()
assert header == ord('h')  # the first byte is 'h'
# trailer points to the same data. starting from `some_bytes[1:]`
assert id(trailer.as_ptr().obj) == id(some_bytes)
```

However, types such as `list`, `tuple` and `set` do not provide zero-copy slicing,
they copy their elements's references into a new object.

```py
from sain import Slice

some_list = [1, 2, 3]
s = Slice(some_list)

last, elements = s.split_last().unwrap()
# `elements` and `some_list` are two different lists, but they point to the same element references.
```
"""

from __future__ import annotations

__all__ = ("Slice", "SliceMut", "SpecContains", "Chunks")

import copy
import typing
from collections import abc as collections

from sain.iter import ExactSizeIterator
from sain.iter import TrustedIter
from sain.macros import rustc_diagnostic_item
from sain.option import Some

T = typing.TypeVar("T")
T_cov = typing.TypeVar("T_cov", covariant=True)

Pattern = T | collections.Iterable[T]

if typing.TYPE_CHECKING:
    from types import EllipsisType
    from typing import SupportsIndex

    from _typeshed import SupportsAllComparisons as SliceOrd

    from sain.collections.vec import Vec
    from sain.option import Option

    class CoerceSized(typing.Protocol[T_cov]):
        """Trait that indicates that an object is indexable, while also having a length."""

        def __getitem__(self, index: SupportsIndex, /) -> T_cov: ...
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


@typing.final
class Chunks(ExactSizeIterator["Slice[T]"]):
    """An iterator over a slice in (non-overlapping) chunks (chunk_size elements at a time), starting at the beginning of the slice.

    When the slice len is not evenly divided by the chunk size, the last slice of the iteration will be the remainder.

    This iterator is created by the `Slice.chunks` method on slices.

    Example
    -------
    ```py
    slice = Slice(['l', 'o', 'r', 'e', 'm'])
    iter = slice.chunks(2)
    assert iter.next() == Some(['l', 'o'])
    assert iter.next() == Some(['r', 'e'])
    assert iter.next() == Some(['m'])
    assert iter.next() == None
    ```
    """

    __slots__ = ("_v", "_chunk_size")

    def __init__(self, s: Slice[T], chunk_size: int, /) -> None:
        if chunk_size == 0:
            raise ValueError("chunk size must be non-zero")

        self._v = s
        self._chunk_size = chunk_size

    def __next__(self) -> Slice[T]:
        if not self._v:
            raise StopIteration

        chunksz = min(len(self._v), self._chunk_size)
        fst, snd = self._v.split_at(chunksz)
        self._v = snd
        return fst

    def __len__(self) -> int:
        if not self._v:
            return 0

        n = len(self._v) / self._chunk_size
        rem = len(self._v) % self._chunk_size
        return int(n + 1 if rem > 0 else n)


@typing.final
class ChunkBy(ExactSizeIterator["Slice[T]"]):
    """An iterator over slice in (non-overlapping) chunks separated by a predicate.

    This struct is created by the `Slice.chunk_by` method on slices.
    """

    __slots__ = ("_v", "_predicate")

    def __init__(
        self, s: Slice[T], predicate: collections.Callable[[T, T], bool], /
    ) -> None:
        self._v = s
        self._predicate = predicate

    def __next__(self) -> Slice[T]:
        if not self._v:
            raise StopIteration

        len_ = 1
        it = self._v.windows(2)
        while True:
            left, right = next(it)
            if self._predicate(left, right):
                len_ += 1
            else:
                break

        head, tail = self._v.split_at(len_)
        self._v = tail
        return head

    def __len__(self) -> int:
        return len(self._v)


@typing.final
class ChunksExact(ExactSizeIterator["Slice[T]"]):
    """An iterator over a slice in (non-overlapping) chunks (`chunk_size` elements at a time), starting at the beginning of the slice.

    When the slice len is not evenly divided by the chunk size,
    the last up to `chunk_size-1` elements will be omitted but can be retrieved from the `remainder` function from the iterator.

    This iterator is created by the `Slice.chunks_exact` method on slices.
    """

    __slots__ = ("_v", "_rem", "_chunk_size")

    def __init__(self, s: Slice[T], chunk_size: int, /) -> None:
        rem = len(s) % chunk_size
        len_ = len(s) - rem
        fst, snd = s.split_at_checked(len_)
        self._v = fst
        self._rem = snd
        self._chunk_size = chunk_size

    def __next__(self) -> Slice[T]:
        if len(self._v) < self._chunk_size:
            raise StopIteration

        fst, snd = self._v.split_at(self._chunk_size)
        self._v = snd
        return fst

    def remainder(self) -> Slice[T]:
        return self._rem

    def __len__(self) -> int:
        return int(len(self._v) / self._chunk_size)


@typing.final
class Windows(ExactSizeIterator["Slice[T]"]):
    """An iterator over overlapping subslices of length `size`.

    This iterator is created by the `Slice.windows` method on slices.

    Example
    -------
    ```py
    slice = Slice(['r', 'u', 's', 't'])
    iter = slice.windows(2)
    assert iter.next() == Some(['r', 'u'])
    assert iter.next() == Some(['u', 's'])
    assert iter.next() == Some(['s', 't'])
    assert iter.next() == None
    ```
    """

    __slots__ = ("_v", "_size")

    def __init__(self, s: Slice[T], size: int, /) -> None:
        if size == 0:
            raise ValueError("window size must be non-zero")

        self._v = s
        self._size = size

    def __next__(self) -> Slice[T]:
        if self._size > len(self._v):
            raise StopIteration

        ret = self._v[: self._size]
        self._v = self._v[1:]
        return ret

    def __len__(self) -> int:
        if self._size > len(self._v):
            return 0

        return len(self._v) - self._size + 1


@rustc_diagnostic_item("[T]")
class Slice(typing.Generic[T], collections.Sequence[T], SpecContains[T]):
    """An immutable view over some sequence of type `T`.

    See the [top-level][] documentation for more information.

    [top-level]: #overview

    Parameters
    ----------
    ptr : `collections.Sequence[T]`
        The sequence to point to.
    """

    __slots__ = ("_buf",)

    def __init__(self, ptr: collections.Sequence[T] = ()) -> None:
        self._buf = ptr

    # impl [T]

    def as_ptr(self) -> collections.Sequence[T]:
        """Returns an immutable reference to the data this slice is pointing to.

        Example
        -------
        ```py
        data = (1, 2, 3, 4)
        s = Slice(data)
        assert id(s.as_ptr()) == id(data)
        ```
        """
        return self._buf

    def iter(self) -> TrustedIter[T]:
        """Returns an iterator over the slice.

        The iterator yields all items from start to end.

        Example
        -------
        ```py
        x: Slice[int] = Slice([1, 2, 3])
        iterator = x.iter()

        assert iterator.next() == Some(1)
        assert iterator.next() == Some(2)
        assert iterator.next() == Some(3)
        assert iterator.next().is_none()
        ```
        """
        return TrustedIter(self._buf)

    def chunks(self, chunk_size: int, /) -> Chunks[T]:
        """Returns an iterator over `chunk_size` elements at a time, starting at the beginning of the slice.

        When the slice len is not evenly divided by the chunk size, the last slice of the iteration will be the remainder.

        The chunks are slices and do not overlap. If `chunk_size` does not divide the length of the slice, then the last chunk will not have length `chunk_size`.

        See `chunks_exact` for a variant of this iterator that returns chunks of always exactly chunk_size elements.

        Example
        -------
        ```py
        slice = Slice(['l', 'o', 'r', 'e', 'm'])
        iter = slice.chunks(2)
        assert iter.next() == Some(['l', 'o'])
        assert iter.next() == Some(['r', 'e'])
        assert iter.next() == Some(['m'])
        assert iter.next() == None
        ```
        """
        return Chunks(self, chunk_size)

    def windows(self, size: int, /) -> Windows[T]:
        """Creates an iterator over overlapping subslices of length `size`.

        Raises
        ------
        `ValueError`
            If `size` is zero.

        Example
        -------
        ```py
        slice = Slice(['r', 'u', 's', 't'])
        iter = slice.windows(2)
        assert iter.next() == Some(['r', 'u'])
        assert iter.next() == Some(['u', 's'])
        assert iter.next() == Some(['s', 't'])
        assert iter.next() == None
        ```
        """
        return Windows(self, size)

    def chunk_by(self, predicate: collections.Callable[[T, T], bool], /) -> ChunkBy[T]:
        """Returns an iterator over the slice producing non-overlapping runs of elements using the predicate to separate them.

        The predicate is called for every pair of consecutive elements,
        meaning that it is called on `slice[0]` and `slice[1]`, followed by `slice[1]` and `slice[2]`, and so on.

        Example
        -------
        ```py
        slice = Slice([1, 1, 1, 3, 3, 2, 2, 2])

        iter = slice.chunk_by(lambda a, b: a == b)

        assert_eq!(iter.next(), Some([1, 1, 1])
        assert_eq!(iter.next(), Some([3, 3])
        assert iter.next() == Some([2, 2, 2])
        assert iter.next() == None
        ```
        """
        return ChunkBy(self, predicate)

    def chunks_exact(self, chunk_size: int, /) -> ChunksExact[T]:
        """Returns an iterator over `chunk_size` elements of the slice at a time, starting at the beginning of the slice.

        The chunks are slices and do not overlap. If `chunk_size` does not divide the length of the slice,
        then the last up to `chunk_size-1` elements will be omitted and can be retrieved from the `ChunksExact.remainder` function of the iterator.

        Raises
        ------
        `ValueError`
            if `chunk_size` is zero.

        Examples
        --------
        ```py
        slice = Slice(['l', 'o', 'r', 'e', 'm'])
        iter = slice.chunks_exact(2)
        assert iter.next().unwrap() == ['l', 'o']
        assert iter.next().unwrap() == ['r', 'e']
        assert iter.next().is_none()
        assert iter.remainder() == ['m']
        ```
        """
        return ChunksExact(self, chunk_size)

    def len(self) -> int:
        """Returns the number of elements in the slice.

        Example
        -------
        ```py
        a = Slice([1, 2, 3])
        assert a.len() == 3
        ```
        """
        return len(self._buf)

    def is_empty(self) -> bool:
        """Returns `True` if the slice has a length of 0.

        Example
        -------
        ```py
        a: Slice[int] = Slice()
        assert a.is_empty()

        a = Slice([1, 2, 3, 4])
        assert not a.is_empty()
        ```
        """
        return not self._buf

    def first(self) -> Option[T]:
        """Returns the first element of the slice, or None if it is empty.

        Example
        --------
        ```py
        v = Slice([10, 40, 30])
        assert v.first().unwrap() == 10

        y: Slice[int] = Slice()
        assert y.first().is_none()
        ```
        """
        return Some(self[0]) if self else Some(None)

    def last(self) -> Option[T]:
        """Returns the last element of the slice, or None if it is empty.

        Example
        --------
        ```py
        v = Slice([10, 40, 30])
        assert v.last().unwrap() == 30

        y: Slice[int] = Slice([])
        assert y.last().is_none()
        ```
        """
        return Some(self[-1]) if self else Some(None)

    def split_first(self) -> Option[tuple[T, Slice[T]]]:
        """Returns the first and rest of the slice elements, returns `None` if the slice's length is 0.

        If empty, `None` is returned.

        Example
        -------
        ```py
        s = Slice([1, 2, 3])

        first, elements = s.split_first().unwrap()
        assert first == 1
        assert elements == [2, 3]
        ```
        """
        if len(self) == 0:
            return Some(None)

        return Some((self[0], self[1:]))

    def split_last(self) -> Option[tuple[T, Slice[T]]]:
        """Returns the last and rest of the slice elements, returns `None` if the slice's length is 0.

        If empty, `None` is returned.

        Example
        -------
        ```py
        s = Slice([1, 2, 3])

        last, elements = s.split_last().unwrap()
        assert last == 3
        assert elements == [1, 2]
        ```
        """
        if len(self) == 0:
            return Some(None)

        return Some((self[-1], self[:-1]))

    def split_once(
        self, pred: collections.Callable[[T], bool]
    ) -> Option[tuple[Slice[T], Slice[T]]]:
        """Splits the slice on the first elements that matches the specified predicate.

        If the predicates matches any elements in the slice, returns the prefix
        before the match and suffix after. The matching element itself will not be included.

        If no elements matches, returns `None`.

        Example
        -------
        ```py
        slice = Slice([1, 2, 3, 2, 4])
        assert slice.split_once(lambda x: x == 2) == Some(([1], [3, 2, 4]))
        ```
        """
        # TODO: Need to bench this.
        if (index := self.iter().position(pred).transpose()) is not None:
            return Some((self[:index], self[index + 1 :]))

        return Some(None)

    def split_at(self, mid: int) -> tuple[Slice[T], Slice[T]]:
        """Divide one slice into two at an index.

        The first will contain all indices from `[0 : mid]` excluding `mid` it self.
        and the second will contain [mid: len], excluding `len` itself.

        if `mid` > `len`, `IndexError` is raised, for non-error version,
        Check `split_at_checked`.

        Example
        -------
        ```py
        s = Slice(['a', 'b', 'c'])

        left, right = s.split_at(0)
        assert left == [] and right == ['a', 'b', 'c']

        left, right = s.split_at(2)
        assert left == ['a', 'b'] and right == ['c']

        # If mid > len, this errors.
        left, right = s.split_at(10) # IndexError(...)
        ```
        """
        if mid > len(self):
            raise IndexError from None

        return self[0:mid], self[mid:]

    def split_at_checked(self, mid: int) -> tuple[Slice[T], Slice[T]]:
        """Divide one slice into two at an index.

        The first will contain all indices from `[0 : mid]` excluding `mid` it self.
        and the second will contain [mid: len], excluding `len` itself.

        if `mid` > `len`, Then all indices will be moved to the left,
        returning an empty indices in right.

        Example
        -------
        ```py
        s = Slice(['a', 'b', 'c'])

        left, right = s.split_at_checked(0)
        assert left == [] and right == ['a', 'b', 'c']

        left, right = s.split_at_checked(2)
        assert left == ['a', 'b'] and right == ['c']

        # If mid > len, it fills the left with all elements, and returns right empty.
        left, right = s.split_at_checked(10)
        assert left == ['a', 'b', 'c'] and right == []
        ```
        """
        return self[0:mid], self[mid:]

    def get(self, index: SupportsIndex) -> Option[T]:
        """Returns a reference to an element at an `index`.

        Return `None` if `index` is out of bounds.

        Example
        -------
        ```py
        s = Slice([1, 2, 3, 4])
        s.get(0).unwrap() == 1
        assert s.get(10).is_none()
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
        xs = Slice([1, 2, 3, 4])
        assert 1 == xs.get_unchecked(0)
        ```
        """
        return self[index.__index__()]

    def starts_with(self, needle: collections.Sequence[T]) -> bool:
        """Returns true if needle is a prefix of the slice or equal to the slice.

        Always returns true if needle is an empty slice.

        Example
        ------
        ```py
        v = Slice([10, 40, 30])
        assert v.starts_with([10])
        assert v.starts_with([10, 40])
        assert v.starts_with([10, 40, 30])
        assert not v.starts_with([50])
        ```
        """
        if not needle:
            return True

        n = len(needle)
        return len(self) >= n and needle == self[:n]

    def ends_with(self, needle: collections.Sequence[T]) -> bool:
        """Returns true if needle is a prefix of the slice or equal to the slice.

        Always returns true if needle is an empty slice.

        Example
        ------
        ```py
        v = Slice([10, 40, 30])
        assert v.ends_with([30])
        assert v.ends_with([40, 40])
        assert v.ends_with([10, 40, 30])
        assert not v.starts_with([10])
        ```
        """
        if not needle:
            return True

        m, n = len(self), len(needle)
        return m >= n and needle == self[m - n :]

    def to_vec(self) -> Vec[T]:
        """Copies `self` into a new `Vec`.

        Example
        -------
        ```py
        s = Slice([1, 2, 3])
        xs = s.to_vec()
        # Here, s and xs can be modified independently.
        ```
        """
        from .vec import Vec

        return Vec(self[:])

    def to_vec_in(self, v: Vec[T], /) -> Vec[T]:
        """Copies `self` into `v` by extending `v`, Then returns `v`.

        Example
        -------
        ```py
        dst = Vec([1, 2, 3])
        s = Slice([4, 5, 6])

        xs = s.to_vec_in(dst)
        assert dst == [1, 2, 3, 4, 5, 6] and dst == xs
        ```
        """
        v.extend(self)
        return v

    def repeat(self, n: int, /) -> Vec[T]:
        """Creates a vector by copying a slice n times.

        Example
        -------
        ```py
        assert Slice([1, 2]).repeat(3) == [1, 2, 1, 2, 1, 2]
        ```
        """
        from .vec import Vec

        if n == 0:
            return Vec()

        return Vec(list(self) * n)

    # * magic

    @typing.overload
    def __getitem__(self, index: int) -> T: ...
    @typing.overload
    def __getitem__(self, index: slice) -> Slice[T]: ...
    @typing.overload
    def __getitem__(self, index: EllipsisType) -> Slice[T]: ...

    def __getitem__(self, index: int | slice | EllipsisType) -> Slice[T] | T:
        if index is ...:
            # Full slice self[...], creates another reference to _buf
            return Slice(self._buf)

        if isinstance(index, slice):
            # Slicing like self[1:], self[:2], self[1:2]
            return Slice(self._buf[index])

        else:
            # index get item, i.e. self[0]
            return self._buf[index]

    def __len__(self) -> int:
        return len(self._buf)

    def __repr__(self) -> str:
        return self._buf.__repr__()

    def __str__(self) -> str:
        return self._buf.__str__()

    def __eq__(self, value: collections.Sequence[T], /) -> bool:
        return self._buf == value

    def __ne__(self, value: collections.Sequence[T], /) -> bool:
        return not self.__eq__(value)

    def __lt__(self, rhs: SliceOrd) -> bool:
        return self._buf < rhs

    def __gt__(self, rhs: SliceOrd) -> bool:
        return self._buf > rhs

    def __le__(self, rhs: SliceOrd) -> bool:
        return self._buf <= rhs

    def __ge__(self, rhs: SliceOrd) -> bool:
        return self._buf >= rhs

    def __bool__(self) -> bool:
        return bool(self._buf)

    def __hash__(self) -> int:
        return hash(self._buf)

    def __copy__(self) -> Slice[T]:
        # Create another reference to `_buf`
        return self[...]


@rustc_diagnostic_item("[T]")
class SliceMut(
    Slice[T],
    # ! we are a mutable *view*, not a mutable sequence.
    # ! we let the concrete impls handle this, like Vec.
):
    """A mutable view over some sequence of type `T`.

    See the [top-level][] documentation for more information.

    [top-level]: #overview

    Parameters
    ----------
    ptr : `collections.MutableSequence[T]`
        The mutable sequence to point to.
    """

    __slots__ = ("_buf",)

    if typing.TYPE_CHECKING:
        _buf: collections.MutableSequence[T]

    def __init__(self, ptr: collections.MutableSequence[T]) -> None:
        # dirty runtime check here just to make sure that people don't
        # call methods on immutable collections. This line doesn't
        # exist if the program is level 1 optimized. `-O`.
        assert isinstance(ptr, collections.MutableSequence), (
            f"expected a mutable sequence, got {type(ptr).__name__}."
        )
        self._buf = ptr

    # impl mut [T]

    def as_mut_ptr(self) -> collections.MutableSequence[T]:
        """Returns a mutable reference to the data this slice is pointing to.

        Example
        -------
        ```py
        data = [1, 2, 3, 4]
        s = SliceMut(data)
        assert s.as_mut_ptr().pop() == 4
        assert data == [1, 2, 3]
        ```
        """
        return self._buf

    def reverse(self) -> None:
        """Reverse this slice, in-place.

        Example
        -------
        ```py
        ss = SliceMut([1, 2, 3])
        ss.reverse()
        assert ss == [3, 2, 1]
        ```
        """
        self._buf.reverse()

    def fill(self, value: T, /) -> None:
        """Fills `self` with elements by copying references of `value`.

        Example
        -------
        ```py
        s = SliceMut([1, 2, 3, 4])
        # Copy `0` references 4 times.
        ss.fill(0)
        assert s == [0, 0, 0, 0]
        ```

        `fill` copy `value` references, not the value itself.

        ```py
        DEFAULT_ARRAY = [1, 2, 3]
        # pre-allocate the slice with 3d lists.
        s = SliceMut([[], [], []])
        # then fill it with the default array.
        s.fill(DEFAULT_ARRAY)
        # the slice is filled with references to `DEFAULT_ARRAY`, which means
        # any modifications to `DEFAULT_ARRAY` also affects the arrays in the slice.
        assert all(id(arr) == id(DEFAULT_ARRAY) for arr in s)
        ```
        """

        if not self._buf:
            return

        self[:] = [value] * len(self)

    def fill_with(self, f: collections.Callable[[], T], /) -> None:
        """Fills `self` with elements by copying the value's reference returned by `f`.

        This method uses closures to create new value, If you'd rather `copy` a given value, use `fill` instead.

        Example
        -------
        ```py
        def default() -> int:
            return 1

        s = SliceMut([0] * 5)
        s.fill_with(default)
        assert s == [1, 1, 1, 1, 1]
        ```
        """
        if not self._buf:
            return

        self[:] = [f()] * len(self)

    def __copy_from_slice_slow(
        self, src: CoerceSized[T], copier: collections.Callable[[T], T], count: int, /
    ) -> None:
        start = 0
        while start < count:
            self[start] = copier(src[start])
            start += 1

    def copy_from_slice(self, src: CoerceSized[T], /) -> None:
        """Shallow copies the elements from `src` into `self`.

        If you need a deep-copy of `src`'s elements, use `clone_from_slice` instead.

        The length of `src` must be the same as `self`.

        Raises
        ------
        `IndexError`
            If the two slices have different lengths.

        Example
        -------
        ```py
        dst = SliceMut([0, 0])
        src = [1, 2, 3, 4]

        # we must slice src here because dst has to be the same length.
        dst.copy_from_slice(src[2:])
        assert src == [3, 4]
        ```
        """

        if (src_len := len(src)) != (self_len := len(self)):
            raise IndexError(
                f"copy_from_slice: source slice length ({src_len}) does not match destination slice length({self_len})"
            ) from None

        self.__copy_from_slice_slow(src, copy.copy, self_len)

    def clone_from_slice(self, src: CoerceSized[T], /) -> None:
        """Deep-copies the elements from `src` into `self`.

        If you only need a shallow-copy of `src`'s elements, use `copy_from_slice` instead.

        The length of `src` must be the same as `self`.

        Raises
        ------
        `IndexError`
            If the two slices have different lengths.

        Example
        -------
        ```py
        dst = SliceMut([0, 0])
        src = [1, 2, 3, 4]

        # we must slice src here because dst has to be the same length.
        dst.clone_from_slice(src[2:])
        assert src == [3, 4]
        ```
        """
        if (src_len := len(src)) != (self_len := len(self)):
            raise IndexError(
                f"clone_from_slice: source slice length ({src_len}) does not match destination slice length({self_len})"
            ) from None

        self.__copy_from_slice_slow(src, copy.deepcopy, self_len)

    def swap(self, a: int, b: int):
        """Swap two elements in the slice.

        if `a` equals to `b` then it's guaranteed that elements won't change value.

        Example
        -------
        ```py
        s = SliceMut([1, 2])
        s.swap(0, 1)
        assert s == [2, 1]
        ```

        if `a == b`, nothing happens.

        ```py
        s = SliceMut([1, 1])
        s.swap(1, 0) # NOP
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
        s = SliceMut([1, 2])
        s.swap_unchecked(0, 1)
        assert s == [2, 1]
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

    def swap_with_slice(self, other: collections.MutableSequence[T]) -> None:
        """Swaps all elements in `self` with those in `other`.

        The length of `other` must be the same as `self`.

        Raises
        ------
        `IndexError`
            If `other`'s length is not the same as `self`.

        Example
        -------
        ```py
        slice1 = SliceMut([1, 2, 3])
        slice2 = SliceMut([4, 5, 6])

        slice1.swap_with_slice(slice2)

        assert slice1 == [4, 5, 6] and slice2 == [1, 2, 3]
        ```
        """
        if len(other) != (count := len(self)):
            raise IndexError(
                "destination and source slices have different lengths"
            ) from None

        start = 0
        while start < count:
            self[start], other[start] = other[start], self[start]
            start += 1

    def split_first_mut(self) -> Option[tuple[T, SliceMut[T]]]:
        """Returns the first and rest of the slice elements, returns `None` if the slice's length is 0.

        If empty, `None` is returned.

        Example
        -------
        ```py
        s = SliceMut([1, 2, 3])

        first, elements = s.split_first_mut().unwrap()
        assert first == 1
        assert elements == [2, 3]
        ```
        """
        if len(self) == 0:
            return Some(None)

        return Some((self[0], self[1:]))

    def split_last_mut(self) -> Option[tuple[T, SliceMut[T]]]:
        """Returns the last and rest of the slice elements, returns `None` if the slice's length is 0.

        If empty, `None` is returned.

        Example
        -------
        ```py
        s = SliceMut([1, 2, 3])

        last, elements = s.split_last_mut().unwrap()
        assert last == 3
        assert elements == [1, 2]
        ```
        """
        if len(self) == 0:
            return Some(None)

        return Some((self[-1], self[:-1]))

    def split_off_first(self) -> Option[T]:
        """Removes the first element of the slice and returns a reference to it.

        Returns None if the slice is empty.

        Example
        -------
        ```py
        s = = SliceMut([1, 2, 3, 4])
        first = s.split_of_first().unwrap()

        assert first == 1
        assert s == [2, 3, 4]
        ```
        """
        if len(self) == 0:
            return Some(None)

        first = self[0]
        del self._buf[0]
        return Some(first)

    def split_off_last(self) -> Option[T]:
        """Removes the last element of the slice and returns a reference to it.

        Returns None if the slice is empty.

        Example
        -------
        ```py
        s = = SliceMut([1, 2, 3, 4])
        last = s.split_off_last().unwrap()

        assert last == 4
        assert s == [1, 2, 3]
        ```
        """
        if len(self) == 0:
            return Some(None)

        last = self[-1]
        del self._buf[-1]
        return Some(last)

    def split_at_mut(self, mid: int) -> tuple[SliceMut[T], SliceMut[T]]:
        """Divide one slice into two at an index.

        The first will contain all indices from `[0 : mid]` excluding `mid` it self.
        and the second will contain [mid: len], excluding `len` itself.

        if `mid` > `len`, `IndexError` is raised, for non-error version,
        Check `split_at_mut_checked`.

        Example
        -------
        ```py
        s = SliceMut(['a', 'b', 'c'])

        left, right = s.split_at_mut(0)
        assert left == [] and right == ['a', 'b', 'c']

        left, right = s.split_at_mut(2)
        assert left == ['a', 'b'] and right == ['c']

        # If mid > len, this errors.
        left, right = s.split_at_mut(10) # IndexError(...)
        ```
        """
        if mid > len(self):
            raise IndexError from None

        return self[0:mid], self[mid:]

    def split_at_mut_checked(self, mid: int) -> Option[tuple[SliceMut[T], SliceMut[T]]]:
        """Divide one slice into two at an index.

        The first will contain all indices from `[0 : mid]` excluding `mid` it self.
        and the second will contain [mid: len], excluding `len` itself.

        if `mid` > `len`, `IndexError` is raised, for non-error version,
        Check `split_at_checked`.

        Example
        -------
        ```py
        s = SliceMut(['a', 'b', 'c'])

        left, right = s.split_at_mut_checked(0)
        assert left == [] and right == ['a', 'b', 'c']

        left, right = s.split_at_mut_checked(2)
        assert left == ['a', 'b'] and right == ['c']

        # If mid > len, it fills the left with all elements, and returns right empty.
        left, right = s.split_at_mut_checked(10)
        assert left == ['a', 'b', 'c'] and right == []
        ```
        """
        if mid > len(self):
            return Some(None)

        return Some((self[0:mid], self[mid:]))

    @typing.overload
    def __getitem__(self, index: int) -> T: ...
    @typing.overload
    def __getitem__(self, index: slice) -> SliceMut[T]: ...
    @typing.overload
    def __getitem__(self, index: EllipsisType) -> SliceMut[T]: ...

    def __getitem__(self, index: int | slice | EllipsisType) -> SliceMut[T] | T:
        if index is ...:
            # Full slice self[...], creates another reference to _buf
            return SliceMut(self._buf)

        if isinstance(index, slice):
            # Slicing like self[1:], self[:2], self[1:2]
            return SliceMut(self._buf[index])

        else:
            # index get item, i.e. self[0]
            return self._buf[index]

    @typing.overload
    def __setitem__(self, index: int, item: T) -> None: ...
    @typing.overload
    def __setitem__(self, index: slice, item: collections.Sequence[T]) -> None: ...

    def __setitem__(
        self, index: int | slice, item: T | collections.Sequence[T]
    ) -> None:
        self._buf[index] = item  # pyright: ignore - this is exactly how its defined in MutableSequence.

    def __delitem__(self, idx: int) -> None:
        del self._buf[idx]

    def __copy__(self) -> SliceMut[T]:
        # Create another reference to `_buf`
        return self[...]
