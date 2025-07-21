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

__all__ = ("Vec",)

import sys as _sys
import typing
from collections import abc as collections

from sain import option as _option
from sain import result as _result
from sain.collections.slice import Slice
from sain.collections.slice import SliceMut
from sain.macros import rustc_diagnostic_item

if typing.TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

    from sain import Result

T = typing.TypeVar("T")


@rustc_diagnostic_item("Vec")
@typing.final
class Vec(SliceMut[T]):
    """A contiguous growable alternative to the builtin `list` with extra functionalities.

    The layout of `Vec<T>` is exactly the same as `list<T>`. Which means `list<T>`'s methods are inherited into `Vec<T>`.

    Also, `Vec<T>` is a `SliceMut<T>`, which means it can be treated as a mutable slice.

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
    * `Vec()`: Create an empty vec.
    * `Vec(other_list)`: Create a vec which points to `other_list`
    * `Vec([1, 2, 3])`: Create a vec with `[1, 2, 3]` pre-allocated.
    * `Vec(iterable)`: Create a vec from an `iterable`, This is `O(n)` where `n` is the number of elements,
    since it copies `iterable`'s elements into a new list.
    * `Vec.with_capacity(5)`: Create a vec that can hold up to 5 elements

    Iterating over `Vec`
    -------------------
    There're two ways to iterate over a `Vec`. The first is to normally use `for` loop.

    ```py
    for i in names:
        print(i)

    # foo
    # bar
    ```

    The second is to use `Vec.iter`, which creates a lazy, unique iterator that yields all items in this `Vec` from start to end.
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
    A `Vec` may be compared with another `Vec` or a `list`, any other type will return `False`

    ```py
    vec = Vec([1, 2, 3])
    assert vec == [1, 2, 3] # True
    assert vec != (1, 2, 3)
    ```

    Zero-Copy
    ---------
    A vec that gets initialized from a `list` will *point* to it and doesn't copy it.
    So any element that gets appended to the list will also get pushed into the vec
    that's pointing to it and vice-versa.

    ```py
    cells: list[str] = []
    vec = Vec(cells) # This DOES NOT copy the `cells`.

    cells.append("foo")
    vec[0] == "foo"  # True
    ```

    If you want an owned `Vec` that doesn't point to the original list,
    copy the list into a new `Vec`.

    ```py
    from sain import Vec

    # Copy `cells` into a vec.
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
        """Create an empty `Vec<T>`.

        Example
        ------
        ```py
        vec: Vec[float] = Vec()
        ```
        """

        if isinstance(iterable, list):
            # Calling `list()` on another list will copy it, So instead we just point to it.
            self._ptr = iterable
        elif isinstance(iterable, Vec):
            self._ptr = iterable._ptr
        # any other iterable that ain't a list needs to get copied into a new list.
        else:
            self._ptr: list[T] = list(iterable) if iterable else []

        self._capacity: int | None = None
        super().__init__(self._ptr)

    @classmethod
    def with_capacity(cls, capacity: int) -> Vec[T]:
        """Create a new `Vec` with at least the specified capacity.
        This vec will be able to hold `capacity` elements without pushing further.

        The capacity may dynamically grow if `Vec.reserve` is called at runtime.

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

    def as_slice(self) -> Slice[T]:
        """Return an immutable view over this vector elements.

        No copying occurs.

        Example
        -------
        ```py
        def send_bytes(v: Slice[int]) -> None:
            # access `vec` in a read-only mode.
            socket.write_all(v)

        buf = Vec([1, 2, 3])
        send_bytes(buf.as_slice())
        ```
        """
        # NOTE: Although, we could just return `self`, but,
        # we want to return an exclusive view.
        return Slice(self._ptr)

    def as_mut_slice(self) -> SliceMut[T]:
        """Return a mutable view over this vector elements.

        No copying occurs.

        Example
        -------
        ```py
        def read_bytes(buf: SliceMut[int]) -> None:
            # similar to how `Write::write_to_end` requires a `&mut [u8]`
            socket.read_to_end(buf)

        buf: Vec[int] = Vec()
        read_bytes(buf.as_mut_slice()) # or just `buf`
        assert buf.len() >= 1
        ```
        """
        # NOTE: Although, we could just return `self`, but,
        # we want to return an exclusive view.
        return SliceMut(self._ptr)

    def capacity(self) -> int:
        """Return the capacity of this vector if set, 0 if not .

        The number `0` here has two different Meanings:
        - The first means the `Vec` doesn't have a specific capacity set.
        - The second means the `Vec` literally initialized with `0` capacity.

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

    def leak(self) -> list[T]:
        """Consumes and leaks the Vec, returning a mutable reference to the contents.

        After calling this, this vec will no longer reference the underlying buffer,
        therefore, it becomes unusable.

        if `self` is uninitialized, an empty list is returned.

        This function is only useful when you want to detach from a `Vec<T>` and get a `list[T]` without
        any copies.

        Example
        -------
        ```py
        x = Vec([1, 2, 3])
        owned = x.leak()
        # x is now unusable.
        owned[0] += 1
        assert owned == [2, 2, 3]
        ```
        """
        # don't point to `_ptr` anymore.
        tmp = self._ptr
        del self._ptr
        return tmp

    def split_off(self, at: int) -> Vec[T]:
        """Split the vector off at the specified position.

        Returns a new vector at the range of `[at : len]`, leaving `self` at `[0: at]`.

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
        `IndexError`
            This method will raise if `at` > `len(self)`
        """
        len_ = self.len()
        if at > len_:
            raise IndexError(
                f"Index `at` ({at}) should be <= than len of vector ({len_}) "
            ) from None

        # Either the list is empty or uninit.
        if not self._ptr:
            return self

        split = self._ptr[at:len_]
        del self._ptr[at:len_]
        return Vec(split)

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
        del self._ptr[size:]

    def retain(self, f: collections.Callable[[T], bool]) -> None:
        """Retains only the elements specified by the predicate.

        This operation occurs in-place without copying the original list.

        Example
        -------
        ```py
        vec = Vec([1, 2, 3])
        vec.retain(lambda elem: elem > 1)

        assert vec == [2, 3]
        ```

        The impl for this method is very simple
        ```py
        for idx, e in enumerate(vec):
            if not f(e):
                del vec[idx]
        ```
        """
        idx = 0
        while idx < len(self._ptr):
            if not f(self._ptr[idx]):
                del self._ptr[idx]
            else:
                idx += 1

    def swap_remove(self, item: T) -> T:
        """Remove the first appearance of `item` from this vector and return it.

        Raises
        ------
        `ValueError`
            if `item` is not in this vector.

        Example
        -------
        ```py
        vec = Vec(('a', 'b', 'c'))
        element = vec.swap_remove('a')
        assert vec == ['b', 'c'] and element == 'a'
        ```
        """
        return self._ptr.pop(self.index(item))

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
                    print("Reached max cap :< can't push", elem)
        ```

        Or you can also just call `Vec.push` and it will push if there's is sufficient capacity.
        ```py
        vec: Vec[int] = Vec.with_capacity(3)

        vec.extend((1, 2, 3))
        vec.push(4)

        assert vec.len() == 3
        ```
        """
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

        for i in range(3):
            vec.push(i)

        match vec.push_within_capacity(4):
            case Ok(_):
                print("Pushed 4 successfully.")
            case Err(elem):
                vec.reserve(1)  # Reserve capacity for 1 more element.
                vec.push(4)  # Now we can push 4.
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

    def append(self, value: T) -> None:
        """Append an element at the end of the vector.

        An alias to `Vec.push`.
        """
        self._ptr.append(value)

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
        self[index] = value

    def pop(self, index: int = -1) -> _option.Option[T]:
        """Removes the last element from a vector and returns it, or `None` if it is empty.

        Example
        -------
        ```py
        vec = Vec((1, 2, 3))
        assert vec.pop() == Some(3)
        assert vec == [1, 2]
        ```
        """
        if not self._ptr:
            return _option.NOTHING

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
            return _option.NOTHING

        if pred(self[-1]):
            return self.pop()

        return _option.NOTHING

    def dedup(self) -> None:
        """Removes consecutive repeated elements in the vector according to their `__eq__`
        implementation.

        Example
        -------
        ```py
        vec = Vec([1, 2, 2, 3, 2])
        vec.dedup()
        assert vec == [1, 2, 3, 2]
        """
        self.dedup_by(lambda a, b: a == b)

    def dedup_by(self, same_bucket: collections.Callable[[T, T], bool]) -> None:
        """Removes all but the first of consecutive elements in the vector satisfying a given equality.

        Example
        -------
        ```py
        vec = Vec(["foo", "bar", "Bar", "baz", "bar"])
        vec.dedup_by(lambda a, b: a.lower() == b.lower())
        assert vec == ["foo", "bar", "baz", "bar"]
        ```

        Only remove consecutive duplicates.
        ```py
        vec = Vec([1, 2, 2, 3, 4, 1])
        vec.dedup_by(lambda a, b: a == b)
        # The final 1 is not adjacent to the first 1, so it is not removed.
        assert vec == [1, 2, 3, 4, 1]
        ```
        """

        if not self._ptr or (len_ := len(self._ptr)) <= 1:
            return

        idx = 1
        while idx < len_:
            if same_bucket(self._ptr[idx], self._ptr[idx - 1]):
                del self._ptr[idx]
                len_ -= 1
            else:
                idx += 1

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
        self._ptr.extend(iterable)

    def copy(self) -> Vec[T]:
        """Copy all elements of `self` into a new vector.

        Example
        -------
        ```py
        original = Vec((1,2,3))
        copy = original.copy()
        copy.push(4)

        print(original) # [1, 2, 3]
        ```
        """
        return Vec(self._ptr[:])

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
        return self._ptr.count(item)
