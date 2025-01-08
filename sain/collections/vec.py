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

__all__ = ("Vec", "from_args")

import sys as _sys
import typing
from collections import abc as collections

from sain import iter as _iter
from sain import option as _option
from sain import result as _result
from sain.macros import rustc_diagnostic_item

if typing.TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

    from sain import Result

T = typing.TypeVar("T")

_LIST_REPR = _sys.intern("[]")


# We are our own implementation, since MutableSequence have some conflicts with the return types.
@typing.final
class Vec(typing.Generic[T]):
    """A contiguous growable alternative to builtin `list` with extra functionalities.

    The layout of `Vec` is almost the same as `list`.

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

    Constructing
    ------------
    * `Vec()`: Create an unallocated vec, Which means the underlying list will be `None` until you start pushing into it
    * `Vec(other_list)`: Create a vec which points to `other_list`
    * `Vec((1, 2, 3))`: Create a vec with `[1, 2, 3]` pre-allocated
    * `Vec.with_capacity(5)`: Create a vec that can hold up to 5 elements
    * `from_args(1, 2, 3)`: Create a vec from arguments. This is not a classmethod

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

    ## Comparison operators
    A `Vec` may be compared with another `Vec` or a `list`, which is what this type is built on-top of.
    any other type will return `False`

    ```py
    vec = Vec([1, 2, 3])
    assert vec == [1, 2, 3] # True
    assert not vec == (1, 2, 3)
    ```

    Zero-Copy
    ---------
    A vec that gets initialized from a `list` will *point* to it and doesn't copy it.
    So any element that gets appended to the list will also get pushed into the vec
    thats pointing to it.

    ```py
    cells: list[str] = []
    vec = Vec(cells) # This DOES NOT copy the `cells`.

    cells.append("foo")
    vec[0] == "foo"  # True
    ```

    The opposite of the above is to initialize the vec from either
    an iterable or args, or copy the list.

    ```py
    from sain.collections import vec, Vec

    # Creates a new vec and extend it with the elements.
    from_args = vec.from_args("foo", "bar")

    # inlined from another iterable.
    from_iter = Vec(["foo", "bar"])

    # Copy the list into a vec.
    vec = Vec(cells[:])
    cells.append("bar")

    vec[1] # IndexError: "bar" doesn't exist in vec.
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
            # Calling `list()` on another list will copy it, So instead we just point to it.
            self._ptr = iterable
        elif isinstance(iterable, Vec):
            self._ptr = iterable._ptr
        # any other iterable that ain't a list needs to get copied into a new list.
        else:
            self._ptr: list[T] | None = list(iterable) if iterable else None

        self._capacity: int | None = None

    @classmethod
    def with_capacity(cls, capacity: int) -> Vec[T]:
        """Create a new `Vec` with at least the specified capacity.
        This vec will be able to hold `capacity` elements without pushing further.

        Check out `Vec.push_within_capacity` as well.

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
        v = cls()
        v._capacity = capacity
        return v

    def as_ref(self) -> collections.Collection[T]:
        """Return an immutable view over this vector elements.

        This will *copy* `self` elements into a new tuple.

        Example
        -------
        ```py
        vec = Vec((1,2,3))
        assert vec.as_ref() == (1, 2, 3)
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

    def capacity(self) -> int:
        """Return the capacity of this vector if set. 0 if not .

        Example
        -------
        ```py
        vec_with_cap = Vec.with_capacity(3)
        assert vec_with_cap.capacity().unwrap() == 3

        vec = Vec([1, 2, 3])
        assert vec.capacity() == 0
        ```
        """
        return 0 if self._capacity is None else self._capacity

    def iter(self) -> _iter.Iterator[T]:
        """Return an iterator over this vector elements.

        Example
        -------
        ```py
        vec = Vec([1 ,2, 3])
        for element in vec.iter().map(str):
            print(element)
        ```
        """
        return _iter.Iter(self)

    def is_empty(self) -> bool:
        """Returns true if the vector contains no elements."""
        return not self._ptr

    def split_off(self, at: int) -> Vec[T]:
        """Split the vector off at the specified position, returning a new
        vec at the range of `[at : len]`, leaving `self` at `[at : vec_len]`.

        if this vec is empty, `self` is returned unchanged.

        Example
        -------
        ```py
        origin = Vec((1, 2, 3, 4))
        split = vec.split_off(2)

        print(origin, split)  # [1, 2], [3, 4]
        ```

        Raises
        ------
        `RuntimeError`
            This method will raise if `at` > `len(self)`
        """
        len_ = self.len()
        if at > len_:
            raise RuntimeError(
                f"Index `at` ({at}) should be <= than len of vector ({len_}) "
            ) from None

        # Either the list is empty or uninit.
        if not self._ptr:
            return self

        split = self[at:len_]  # split the items into a new vec.
        del self._ptr[at:len_]  # remove the items from the original list.
        return split

    def split_first(self) -> _option.Option[tuple[T, collections.Sequence[T]]]:
        """Split the first and rest elements of the vector, If empty, `None` is returned.

        Example
        -------
        ```py
        vec = Vec([1, 2, 3])
        split = vec.split_first()
        assert split == Some((1, [2, 3]))

        vec: Vec[int] = Vec()
        split = vec.split_first()
        assert split.is_none()
        ```
        """
        if not self._ptr:
            return _option.NOTHING  # pyright: ignore

        # optimized to only one element in the vector.
        if self.len() == 1:
            return _option.Some((self[0], ()))

        first, *rest = self._ptr
        return _option.Some((first, rest))

    def split_last(self) -> _option.Option[tuple[T, collections.Sequence[T]]]:
        """Split the last and rest elements of the vector, If empty, `None` is returned.

        Example
        -------
        ```py
        vec = Vec([1, 2, 3])
        last, rest = vec.split_last().unwrap()
        assert (last, rest) == [3, [1, 2]]
        ```
        """
        if not self._ptr:
            return _option.NOTHING  # pyright: ignore

        # optimized to only one element in the vector.
        if self.len() == 1:
            return _option.Some((self[0], ()))

        last = self[-1]
        return _option.Some((last, [*self[:-1]]))

    def split_at(self, mid: int) -> tuple[Vec[T], Vec[T]]:
        """Divide `self` into two at an index.

        The first will contain all elements from `[0:mid]` excluding `mid` it self.
        and the second will contain the remaninig elements.

        if `mid` > `self.len()`, Then all elements will be moved to the left,
        returning an empty vec in right.

        Example
        -------
        ```py
        buffer = Vec((1, 2, 3, 4))
        left, right = buffer.split_at(0)
        assert left == [] and right == [1, 2, 3, 4]

        left, right = buffer.split_at(2)
        assert left == [1, 2] and right == [2, 3]
        ```

        The is roughly the implementation
        ```py
        self[0:mid], self[mid:]
        ```
        """
        return self[0:mid], self[mid:]

    def swap(self, a: int, b: int):
        """Swap two elements in the vec.

        if `a` equals to `b` then it's guaranteed that elements won't change value.

        Example
        -------
        ```py
        buf = Vec([1, 2, 3, 4])
        buf.swap(0, 3)
        assert buf == [4, 2, 3, 1]
        ```

        Raises
        ------
        IndexError
            If the positions of `a` or `b` are out of index.
        """
        if self[a] == self[b]:
            return

        self[a], self[b] = self[b], self[a]

    def swap_unchecked(self, a: int, b: int):
        """Swap two elements in the vec. without checking if `a` == `b`.

        If you care about `a` and `b` equality, see `Vec.swap`.

        Example
        -------
        ```py
        buf = Vec([1, 2, 3, 1])
        buf.swap_unchecked(0, 3)
        assert buf == [1, 2, 3, 1]
        ```

        Raises
        ------
        IndexError
            If the positions of `a` or `b` are out of index.
        """
        self[a], self[b] = self[b], self[a]

    def first(self) -> _option.Option[T]:
        """Get the first element in this vec, returning `None` if there's none.

        Example
        -------
        ```py
        vec = Vec((1,2,3))
        first = vec.first()
        assert ~first == 1
        ```
        """
        return self.get(0)

    def last(self) -> _option.Option[T]:
        """Get the last element in this vec, returning `None` if there's none.

        Example
        -------
        ```py
        vec = Vec([1, 2, 3, 4])
        first = vec.last()
        assert ~first == 4
        ```
        """
        return self.get(-1)

    def truncate(self, size: int) -> None:
        """Shortens the vec, keeping the first `size` elements and dropping the rest.

        Example
        -------
        ```py
        vec = Vec([1,2,3])
        vec.truncate(1)
        assert vec == [1]
        ```
        """
        if not self._ptr:
            return

        del self._ptr[size:]

    def retain(self, f: collections.Callable[[T], bool]) -> None:
        """Remove elements from this vec in-place while `f()` returns `True`.

        In other words, filter this vector based on `f()`.

        Example
        -------
        ```py
        vec = Vec([1, 2, 3])
        vec.retain(lambda elem: elem > 1)

        assert vec == [2, 3]
        ```
        """
        if not self._ptr:
            return

        for idx, e in enumerate(self._ptr):
            if f(e):
                del self._ptr[idx]

    def swap_remove(self, item: T) -> T:
        """Remove the first appearance of `item` from this vector and return it.

        Raises
        ------
        * `ValueError`: if `item` is not in this vector.
        * `MemoryError`: if this vector hasn't allocated, Aka nothing has been pushed to it.

        Example
        -------
        ```py
        vec = Vec(('a', 'b', 'c'))
        element = vec.remove('a')
        assert vec == ['b', 'c'] and element == 'a'
        ```
        """
        if self._ptr is None:
            raise MemoryError("Vec is unallocated.") from None

        return self._ptr.pop(self.index(item))

    def fill(self, value: T) -> None:
        """Fill `self` with the given `value`.

        Nothing happens if the vec is empty or unallocated.

        Example
        ```py
        a = Vec([0, 1, 2, 3])
        a.fill(0)
        assert a == [0, 0, 0, 0]
        ```
        """
        if not self._ptr:
            return

        for n, _ in enumerate(self):
            self[n] = value

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
        if self._capacity is not None:
            self.push_within_capacity(item)
            return

        if self._ptr is None:
            self._ptr = []

        self._ptr.append(item)

    def push_within_capacity(self, x: T) -> Result[None, T]:
        """Appends an element if there is sufficient spare capacity, otherwise an error is returned with the element.

        Example
        -------
        ```py
        vec: Vec[int] = Vec.with_capacity(3)
        for i in range(3):
            match vec.push_within_capacity(i):
                case Ok(_):
                    print("All good.")
                case Err(elem):
                    print("Reached max cap :< cant push", elem)
        ```

        Or you can also just call `Vec.push` and it will push if theres is sufficient capacity.
        ```py
        vec: Vec[int] = Vec.with_capacity(3)

        vec.extend((1, 2, 3))
        vec.push(4)

        assert vec.len() == 3
        ```
        """
        if self._ptr is None:
            self._ptr = []

        if self.len() == self._capacity:
            return _result.Err(x)

        self._ptr.append(x)
        return _result.Ok(None)

    def reserve(self, additional: int) -> None:
        """Reserves capacity for at least additional more elements to be inserted in the given Vec<T>.

        Example
        -------
        ```py
        vec = Vec.with_capacity(3)
        is_vip = random.choice((True, False))

        for i in range(4):
            match vec.push_within_capacity(i):
                case Ok(_):
                    print("All good")
                case Err(person):
                    # If the person is a VIP, then reserve for one more.
                    if is_vip:
                        vec.reserve(1)
                        continue

                    # is_vip was false.
                    print("Can't reserve for non-VIP members...", person)
                    break
        ```
        """
        if self._capacity is not None:
            self._capacity += additional

    def shrink_to_fit(self) -> None:
        """Shrink the capacity of this `Vec` to match its length.

        If `self` is initialized with no capacity, This is a `NOP`.

        Example
        -------
        ```py
        s = Vec([1, 2, 3, 4])

        s.reserve(100)
        s.shrink_to_fit()
        assert s.capacity() == 4
        ```
        """
        if self._capacity is None:
            return

        # The capacity is never less than the length.
        self._capacity = min(self.__len__(), self._capacity)

    def shrink_to(self, min_capacity: int) -> None:
        """Shrink the capacity of this `Vec` to a minimum specified capacity.

        If `self` is initialized with no capacity or the current capacity is less than the lower limit,
        This is a `NOP`.

        Example
        -------
        ```py
        vec = Vec.with_capacity(10)
        vec.extend([1, 2, 3])
        assert vec.capacity() >= 10
        vec.shrink_to(4)
        assert vec.capacity() >= 4
        vec.shrink_to(0)
        ```
        """
        if self._capacity is None or self._capacity <= min_capacity:
            return

        # Ensure the capacity is not reduced below the current length of the vector.
        self._capacity = max(self.__len__(), min_capacity)

    ##########################
    # * Builtin Operations *
    ##########################

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
            return _option.Some(self[index])
        except IndexError:
            return _option.NOTHING  # pyright: ignore

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
            return _option.NOTHING  # pyright: ignore

        return _option.Some(self._ptr.pop(index))

    def pop_if(self, pred: collections.Callable[[T], bool]) -> _option.Option[T]:
        """Removes the last element from a vector and returns it if `f` returns `True`,
        or `None` if it is empty.

        Example
        -------
        ```py
        vec = Vec((1, 2, 3))
        assert vec.pop_if(lambda num: num * 2 == 6) == Some(3)
        assert vec == [1, 2]
        ```
        """
        if not self._ptr:
            return _option.NOTHING  # pyright: ignore

        if pred(self[-1]):
            return self.pop()

        return _option.NOTHING  # pyright: ignore

    def dedup(self) -> None:
        """Removes duplicate elements from `self` in-place.

        Example
        -------
        ```py
        vec = Vec([1, 2, 3, 3, 4, 1])
        vec.dedup()
        assert vec == [1, 2, 3, 4]
        """

        if not self._ptr:
            return

        seen: set[T] = set()
        write_idx = 0

        for read_idx, _ in enumerate(self._ptr):
            if self._ptr[read_idx] not in seen:
                seen.add(self._ptr[read_idx])
                self._ptr[write_idx] = self._ptr[read_idx]
                write_idx += 1

        del self._ptr[write_idx:]

    def remove(self, item: T) -> None:
        """Remove the first appearance of `item` from this vector.

        Example
        -------
        ```py
        vec = Vec(('a', 'b', 'c'))
        vec.remove('a')
        assert vec == ['b', 'c']
        ```
        """
        if not self._ptr:
            return

        self._ptr.remove(item)

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

        Example
        -------
        ```py
        original = Vec((1,2,3))
        copy = original.copy()
        copy.push(4)

        print(original) # [1, 2, 3]
        ```
        """
        return Vec(self._ptr[:]) if self._ptr else Vec()

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

    def sort(
        self,
        *,
        key: collections.Callable[[T], SupportsRichComparison] | None = None,
        reverse: bool = False,
    ) -> None:
        """This method sorts the list in place, using only < comparisons between items.

        Example
        -------
        ```py
        vec = Vec((2, 1, 3))
        vec.sort()
        assert vec == [1, 2, 3]
        ```
        """
        if not self._ptr:
            return

        # key can be `None` here just fine, idk why pyright is complaining.
        self._ptr.sort(key=key, reverse=reverse)  # pyright: ignore

    def index(
        self, item: T, start: typing.SupportsIndex = 0, end: int = _sys.maxsize
    ) -> int:
        # << Official documentation >>
        """Return zero-based index in the vec of the first item whose value is equal to `item`.
        Raises a ValueError if there is no such item.

        Example
        -------
        ```py
        vec = Vec((1, 2, 3))
        assert vec.index(2) == 1
        ```
        """
        if self._ptr is None:
            raise ValueError from None

        return self._ptr.index(item, start, end)

    def count(self, item: T) -> int:
        """Return the number of occurrences of `item` in the vec.

        `0` is returned if the vector is empty or hasn't been initialized, as well if them item not found.

        Example
        --------
        ```py
        vec = Vec((1, 2, 3, 3))
        assert vec.count(3) == 2
        ```
        """
        if self._ptr is None:
            return 0

        return self._ptr.count(item)

    def __len__(self) -> int:
        return len(self._ptr) if self._ptr else 0

    def __setitem__(self, index: int, value: T):
        if not self._ptr:
            raise IndexError from None

        self._ptr[index] = value

    @typing.overload
    def __getitem__(self, index: slice) -> Vec[T]: ...

    @typing.overload
    def __getitem__(self, index: int) -> T: ...

    def __getitem__(self, index: int | slice) -> T | Vec[T]:
        if not self._ptr:
            raise IndexError("Index out of range")

        if isinstance(index, slice):
            return Vec(self._ptr[index])

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
        if isinstance(other, Vec):
            return self._ptr == other._ptr

        elif isinstance(other, list):
            return self._ptr == other

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


@rustc_diagnostic_item("vec!")
def from_args(*elements: T) -> Vec[T]:
    """Creates a `Vec` containing `elements`.

    Example
    -------
    ```py
    import sain.vec as vec

    items = vec.from_args('Apple', 'Orange', 'Lemon')
    items.push('Grape')
    ```
    """
    return Vec(elements)
