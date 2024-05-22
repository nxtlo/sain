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
"""A contiguous growable alternative to builtin `list` with extra functionalities.

Example
-------
```py
names = Vec[str]()

names.push('foo')
names.push('bar')

print(names) # ['foo', 'bar']
assert names.len() == 2
```
"""

from __future__ import annotations

__all__ = ("Vec", "vec")

import sys as _sys
import typing
from collections import abc as collections

from . import iter as _iter
from . import macros
from . import option as _option

if typing.TYPE_CHECKING:
    from typing_extensions import Self

T = typing.TypeVar("T")

_LIST_REPR = _sys.intern("[]")


# We are our own implementation, since MutableSequence have some conflicts with the return types.
@typing.final
class Vec(typing.Generic[T]):
    """A contiguous growable alternative to builtin `list` with extra functionalities.

    The layout of `Vec` is basically the same as `list`.

    When initializing a vec, it will not build the underlying list until the first element gets pushed.
    Which saves a little bit of memory.

    Example
    -------
    ```py
    names = Vec()
    names.push('foo')
    names.push('bar')

    print(names) # ['foo', 'bar']
    assert names.len() == 2
    ```

    Iterating over `Vec`
    -------------------
    There're two ways to iterate over a `Vec`. The first is to normally use `for` loop.

    ```py
    for i in names:
        print(i)
    # foo
    # bar
    ```

    The second is to use `Vec.iter`, which yields all items in this `Vec` from start to end.
    Then the iterator gets exhausted as usual, See `sain.Iterator`.

    ```py
    iterator = names.iter()
    for name in iterator.map(str.upper):
        print(name)
    # FOO
    # BAR

    # No more items, The actual vec is left unchanged.
    assert iterator.next().is_none()
    ```

    Comparison operators
    --------------------
    Comparing different collections with `Vec` have a cost. Depending on what you're comparing it wit.

    Any iterable that is not a `list` or `Vec` that is used to compare with will get copied into a `list`,
    So be careful what you compare a `Vec` with.

    ```py
    vec = Vec((1,2,3))
    # zero-cost
    vec == [1, 2, 3]
    # Copies {1, 2, 3} -> [1, 2, 3] which can cost.
    vec == {1, 2, 3}
    ```

    Zero-Copy
    ---------
    A vec that gets initialized from a `list` will *point* to it and doesn't copy it.
    So any element that gets appended to the collection will also get pushed into the vec.

    ```py
    cells: list[str] = []
    vec = Vec(cells) # This DOES NOT copy the `cells`.

    cells.append("foo")
    vec[0] == "foo"  # True
    ```

    The opposite of the above is to initialize the vec from either
    an iterable or args, or copy the list.

    ```py
    # Creates a new list and extend it with the elements.
    from_args = Vec.from_args("foo", "bar")

    # inlined from another iterable.
    from_iter = Vec(["foo", "bar"])

    # Copy the list into a vec.
    vec = Vec(cells[:])
    cells.append("bar")

    vec[2] # IndexError: "bar" doesn't exist in vec.
    ```
    """

    __slots__ = ("_ptr", "_capacity")

    @typing.overload
    def __init__(self) -> None: ...

    @typing.overload
    def __init__(self, iterable: collections.Iterable[T]) -> None: ...

    def __init__(self, iterable: collections.Iterable[T] | None = None) -> None:
        # We won't allocate to build the list here.
        # Instead, On first push or fist indexed set
        # we allocate if it was None.
        if isinstance(iterable, list):
            # Calling `list()` on another list will copy it.
            self._ptr = iterable
        elif isinstance(iterable, Vec):
            self._ptr = iterable._ptr
        else:
            self._ptr: list[T] | None = list(iterable) if iterable else None

        self._capacity = 0

    @classmethod
    def from_args(cls, *args: T) -> Self:
        return cls(args)

    @classmethod
    @macros.unstable()
    def with_capacity(cls, capacity: int) -> Self:
        """Create a new `Vec` with at least the specified capacity.

        This vec will be able to hold `capacity` elements without pushing further if `len(vec) == capacity`.

        Example
        -------
        ```py
        vec = Vec.with_capacity(3)
        assert vec.len() == 0 and vec.capacity() >= 3

        vec.push(1)
        vec.push(2)
        vec.push(3)
        print(vec.len()) # 3

        # This won't push.
        vec.push(4)
        ```
        """
        return cls()

    def boxed(self) -> collections.Collection[T]:
        """Return an immutable view over this vector elements.

        Example
        -------
        ```py
        vec = Vec((1,2,3))

        assert vec.boxed() == (1,2,3)
        ```
        """
        return tuple(self)

    def len(self) -> int:
        """Return the number of elements in this vector.

        Example
        -------
        ```py
        vec = Vec((1,2,3))

        assert vec.len() == 3
        ```
        """
        return self.__len__()

    @macros.unstable(reason="`Vec` capacity is not unimplemented yet.")
    def capacity(self) -> int:
        """Return the capacity of this vector.

        Example
        -------
        ```py
        TODO
        ```
        """
        return self._capacity

    def iter(self) -> _iter.Iterator[T]:
        """Return an iterator over this vector elements.

        Example
        -------
        ```py
        vec = Vec((1,2,3))
        iterator = vec.iter()

        # Map each element to a str
        for element in iterator.map(str):
            print(element)
        ```
        """
        return _iter.Iter(self)

    def is_empty(self) -> bool:
        """Returns true if the vector contains no elements."""
        return self.len() == 0

    def split_off(self, at: int) -> Vec[T]:
        """Split the vector off at the specified position.

        Example
        -------
        ```py
        vec = Vec((1, 2, 3))
        split = vec.split_off(1)

        print(split, vec)  # [1], [2, 3]
        ```
        """
        if at > self.len():
            raise RuntimeError(
                f"Index `at` ({at}) should be <= than len of vector ({self.len()}) "
            ) from None

        # Either the list is empty or uninit.
        if not self._ptr:
            return self

        split = self[at : self.len()]
        self._ptr = self._ptr[0:at]
        return split

    def split_first(self) -> _option.Option[tuple[T, collections.Sequence[T]]]:
        """Split the first and rest elements of the vector, If empty, `Some[None]` is returned.

        Example
        -------
        ```py
        vec = vec(1, 2, 3)
        split = vec.split_first()
        assert split == Some((1, [2, 3]))

        vec: Vec[int] = vec()
        split = vec.split_first()
        assert split == Some(None)
        ```
        """
        if not self._ptr:
            return _option.nothing_unchecked()

        first, *rest = self._ptr
        return _option.Some((first, rest))

    def first(self) -> _option.Option[T]:
        """Get the first element in this vec, returning `Some[None]` if there's none.

        Example
        -------
        ```py
        vec = Vec((1,2,3))
        first = vec.first()
        assert ~first == 1
        ```
        """
        return self.get(0)

    def truncate(self, size: int) -> None:
        """Shortens the vec, keeping the first `size` elements and dropping the rest.

        Example
        -------
        ```py
        vec = vec(1,2,3)
        vec.truncate(1)
        assert vec == [1]
        ```
        """
        if not self._ptr:
            return

        self._ptr = self._ptr[:size]

    def retain(self, f: collections.Callable[[T], bool]) -> None:
        """Remove elements from this vec while `f()` returns `True`.

        In other words, filter this vector based on `f()`.

        Example
        -------
        ```py
        vec = vec(1, 2, 3)
        vec.retain(lambda elem: elem > 1)

        assert vec == [2, 3]
        ```
        """
        if not self._ptr:
            return

        self._ptr = [e for e in self._ptr if f(e)]

    ##########################
    # * Builtin Operations *
    ##########################

    def push(self, item: T) -> None:
        """Push an element at the end of the vector.

        Example
        -------
        ```py
        vec = Vec()
        vec.push(1)

        assert vec == [1]
        ```
        """
        if self._ptr is None:
            self._ptr = []

        self._ptr.append(item)

    # For people how are used to calling list.append
    append = push
    """An alias for `Vec.push` method."""

    def get(self, index: int) -> _option.Option[T]:
        """Get the item at the given index, or `Some[None]` if its out of bounds.

        Example
        -------
        ```py
        vec = Vec((1, 2, 3))
        vec.get(0) == Some(1)
        vec.get(3) == Some(None)
        ```
        """
        try:
            return _option.Some(self.__getitem__(index))
        except IndexError:
            return _option.nothing_unchecked()

    def insert(self, index: int, value: T) -> None:
        """Insert an element at the position `index`.

        Example
        --------
        ```py
        vec = Vec((2, 3))
        vec.insert(0, 1)
        assert vec == [1, 2, 3]
        ```
        """
        self.__setitem__(index, value)

    def pop(self, index: int = -1) -> _option.Option[T]:
        """Removes the last element from a vector and returns it, or `sain.Some(None)` if it is empty.

        Example
        -------
        ```py
        vec = Vec((1, 2, 3))
        assert vec.pop() == Some(3)
        assert vec == [1, 2]
        ```
        """
        if not self._ptr:
            return _option.nothing_unchecked()

        return _option.Some(self._ptr.pop(index))

    def remove(self, item: T) -> None:
        """Remove `item` from this vector.

        Example
        -------
        ```py
        vec = Vector(('a', 'b', 'c'))
        vec.remove('a')
        assert vec == ['b', 'c']
        ```
        """
        if not self._ptr:
            return

        self._ptr.remove(item)

    def swap_remove(self, item: T) -> T:
        """Remove the first appearance of `item` from this vector and return it.

        Raises
        ------
        * `ValueError`: if `item` is not in this vector.
        * `MemoryError`: if this vector hasn't allocated, Aka nothing has been pushed to it.

        Example
        -------
        ```py
        vec = Vector(('a', 'b', 'c'))
        element = vec.remove('a')
        assert vec == ['b', 'c'] and element == 'a'
        ```
        """
        if self._ptr is None:
            raise MemoryError("Vec is unallocated.") from None

        try:
            i = next(i for i in self._ptr if i == item)
        except StopIteration:
            raise ValueError(f"Item `{item}` not in list") from None

        self.remove(i)
        return i

    def extend(self, iterable: collections.Iterable[T]) -> None:
        """Extend this vector from another iterable.

        Example
        -------
        ```py
        vec = Vec((1, 2, 3))
        vec.extend((4, 5, 6))

        assert vec == [1, 2, 3, 4, 5, 6]
        ```
        """
        if self._ptr is None:
            self._ptr = []

        self._ptr.extend(iterable)

    def copy(self) -> Vec[T]:
        """Create a vector that copies all of its elements and place it into the new one.

        If the vector hasn't been allocated, `self` is returned.

        Example
        -------
        ```py
        original = Vec((1,2,3))
        copy = original.copy()
        copy.push(4)

        print(original) # [1, 2, 3]
        ```
        """
        return Vec(self._ptr[:]) if self._ptr is not None else self

    def clear(self) -> None:
        """Clear all elements of this vector.

        Example
        -------
        ```py
        vec = Vec((1,2,3))
        vec.clear()
        assert vec.len() == 0
        ```
        """
        if not self._ptr:
            return

        self._ptr.clear()

    def __len__(self) -> int:
        return len(self._ptr) if self._ptr else 0

    def __setitem__(self, index: int, value: T):
        if self._ptr is None:
            self._ptr = []

        self._ptr[index] = value

    @typing.overload
    def __getitem__(self, index: slice) -> Vec[T]: ...

    @typing.overload
    def __getitem__(self, index: int) -> T: ...

    def __getitem__(self, index: int | slice) -> T | Vec[T]:
        if not self._ptr:
            raise IndexError("Index out of range")

        if isinstance(index, slice):
            return self.__class__(self._ptr[index])

        return self._ptr[index]

    def __delitem__(self, index: int) -> None:
        if not self._ptr:
            return

        del self._ptr[index]

    def __contains__(self, element: T) -> bool:
        return element in self._ptr if self._ptr else False

    def __iter__(self) -> collections.Iterator[T]:
        if self._ptr is None:
            return iter(())

        return self._ptr.__iter__()

    def __repr__(self) -> str:
        return _LIST_REPR if not self._ptr else repr(self._ptr)

    def __eq__(self, other: object) -> bool:
        if not self._ptr:
            return False

        if isinstance(other, Vec):
            return self._ptr == other._ptr

        elif isinstance(other, list):
            return self._ptr == other

        elif isinstance(other, collections.Iterable):
            # We have to copy here.
            return self._ptr == list(other)

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __le__(self, other: list[T]) -> bool:
        if not self._ptr:
            return False

        return self._ptr <= other

    def __ge__(self, other: list[T]) -> bool:
        if not self._ptr:
            return False

        return self._ptr >= other

    def __lt__(self, other: list[T]) -> bool:
        if not self._ptr:
            return False

        return self._ptr < other

    def __gt__(self, other: list[T]) -> bool:
        if not self._ptr:
            return False

        return self._ptr > other

    def __bool__(self) -> bool:
        return bool(self._ptr)


def vec(*elements: T) -> Vec[T]:
    """Construct a vector containing `elements`.

    Example
    -------
    ```py
    items = vec('Apple', 'Orange', 'Lemon')
    items.push('Grape')
    ```
    """
    return Vec(elements)
