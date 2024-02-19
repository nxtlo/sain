"""A contiguous growable alternative to builtin `list` with extra functionalities.

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

Equality is supported.

```py
vec = Vec((1,2,3))
vec == [1, 2, 3] and vec # True
```
"""
from __future__ import annotations

__all__ = ("Vec", "vec")

import typing
import itertools as itertools

from collections import abc as collections

from . import macros
from . import iter as _iter
from . import option as _option

T = typing.TypeVar("T")


# We are our own implementation, since MutableSequence have some conflicts with the return types.
@typing.final
class Vec(typing.Generic[T]):
    """A contiguous growable alternative to builtin `list` with extra functionalities.

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

    Equality is supported.

    ```py
    vec = Vec((1,2,3))
    vec == [1, 2, 3] and vec # True
    ```
    """

    __slots__ = ("_ptr", "_capacity")

    @typing.overload
    def __init__(self) -> None:
        ...

    @typing.overload
    def __init__(self, iterable: collections.Iterable[T]) -> None:
        ...

    def __init__(self, iterable: collections.Iterable[T] | None = None) -> None:
        """Initializes a new vec, This won't actually create the internal list until an element is appended into it.

        Example
        -------
        ```py
        names = Vec[str]()

        names.push('foo')
        names.push('bar')

        assert names.len() == 2

        # Initialize a vec from another iterable.
        from_iter = Vec((1,2,3))
        assert from_iter.len() == 3
        ```
        """

        # We won't allocate to build the list here.
        # Instead, On first push or fist indexed set
        # we allocate if it was None.
        self._ptr: list[T] | None = list(iterable) if iterable else None
        self._capacity = 0

    @classmethod
    @macros.unstable(reason="not unimplemented yet.")
    def with_capacity(cls, capacity: int) -> Vec[T]:
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
        v = Vec()
        v._capacity = capacity
        return v

    def into_inner(self) -> collections.Collection[T]:
        """Return an immutable collection over this vector elements.

        Example
        -------
        ```py
        vec = Vec((1,2,3))

        assert vec.into_inner() == (1,2,3)
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

    @macros.unstable(reason="not unimplemented yet.")
    def capacity(self) -> int:
        """Return the capacity of this vector.

        Example
        -------
        ```py
        TODO
        ```
        """
        return self._capacity

    def iter(self) -> _iter.Iter[T]:
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

        assert self._ptr is not None, "Can't access an empty sequence."
        if at > self.len():
            raise RuntimeError(
                f"Index `at` ({at}) should be <= than len of vector ({self.len()}) "
            ) from None

        # No reason to split at 0.
        if at == 0:
            return self

        split = self[at : self.len()]
        self._ptr = self._ptr[0:at]
        return split

    def split_first(self) -> _option.Option[tuple[T, collections.Sequence[T]]]:
        """Split the first and rest elements of the vector,
        if the rest is empty, `Some[None]` is returned.

        Example
        -------
        ```py
        vec = Vec((1, 2, 3))
        split = vec.split_first()
        assert split == Some((1, (2, 3)))

        vec = Vec((1))
        split = vec.split_first()
        assert split == Some(None)
        ```
        """
        assert self._ptr is not None, "Can't access an empty sequence."
        first, *rest = self._ptr
        if not rest:
            return _option.Some(None)

        return _option.Some((first, tuple(rest)))

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
        assert self._ptr is not None, "Can't access an empty sequence."

        if self.len() == 0:
            return

        self._ptr = self._ptr[:size]

    def retain(self, f: collections.Callable[[T], bool]):
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
        assert self._ptr is not None, "Can't access an empty sequence."

        if self.len() == 0:
            return

        self._ptr = [e for e in self._ptr if f(e)]

    ##########################
    # * Builtin Operations *
    ##########################

    def push(self, item: T) -> None:
        """Push an element at the end of the vector.

        Example
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
            return _option.Some(None)

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
        assert self._ptr is not None, "Can't access an empty sequence."
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
        assert self._ptr is not None, "Can't access an empty sequence."
        self._ptr.remove(item)

    def swap_remove(self, item: T) -> T:
        """Remove the first appearance of `item` from this vector and return it.

        This will raise a `ValueError` if `item` is not in this vector.

        Example
        -------
        ```py
        vec = Vector(('a', 'b', 'c'))
        vec.remove('a')
        assert vec == ['b', 'c']
        ```
        """
        assert self._ptr is not None, "Can't access an empty sequence."
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
        assert self._ptr is not None, "Can't access an empty sequence."
        self._ptr.extend(iterable)

    def copy(self) -> Vec[T]:
        """Create a vector that copies all of its elements and place it into the new one.

        Example
        -------
        ```py
        original = Vec((1,2,3))
        copy = original.copy()
        copy.push(4)

        print(original) # []
        ```
        """
        assert self._ptr is not None, "Can't access an empty sequence."
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
        assert self._ptr is not None, "Can't access an empty sequence."
        self._ptr.clear()

    def __len__(self) -> int:
        return len(self._ptr) if self._ptr else 0

    def __setitem__(self, index: int, value: T):
        if self._ptr is None:
            self._ptr = []

        self._ptr[index] = value

    @typing.overload
    def __getitem__(self, index: slice) -> Vec[T]:
        ...

    @typing.overload
    def __getitem__(self, index: int) -> T:
        ...

    def __getitem__(self, index: int | slice) -> T | Vec[T]:
        assert self._ptr is not None, "Can't access an empty sequence."
        if isinstance(index, slice):
            return self.__class__(self._ptr[index])

        return self._ptr[index]

    def __delitem__(self, index: int) -> None:
        assert self._ptr is not None, "Can't access an empty sequence."
        del self._ptr[index]

    def __contains__(self, element: T) -> bool:
        assert self._ptr is not None, "Can't access an empty sequence."
        return element in self._ptr

    def __iter__(self) -> collections.Iterator[T]:
        assert self._ptr is not None, "Can't access an empty sequence."
        return self._ptr.__iter__()

    def __repr__(self) -> str:
        return "[]" if not self._ptr else repr(self._ptr)

    def __eq__(self, other: object) -> bool:
        assert self._ptr is not None, "Can't access an empty sequence."
        if isinstance(other, Vec):
            return self._ptr == other._ptr
        if isinstance(other, (collections.Iterable, collections.MutableSequence)):
            return list(other) == self._ptr

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

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
