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
"""Composable external iteration. See `Iter` for more details."""

from __future__ import annotations

__all__ = ("Iter", "into_iter", "empty", "once")

import collections.abc as collections
import copy
import itertools
import typing

from . import default as _default
from . import futures
from . import option as _option
from . import result as _result
from .vec import Vec

Item = typing.TypeVar("Item")
"""A type hint for the item type of the iterator."""

if typing.TYPE_CHECKING:
    import _typeshed
    import typing_extensions as ty_ext

    from .option import Option

    OtherItem = typing.TypeVar("OtherItem")
    _B = typing.TypeVar("_B", bound=collections.Callable[..., typing.Any])


class Iter(
    collections.Iterator[Item],
    collections.Iterable[Item],
    _default.Default["Iter[ty_ext.Never]"],
):
    """a lazy, in-memory functional iterator.

    This is similar to Rust `Iterator` trait which iterables can build
    from this via `.iter()` method.

    Example
    -------
    ```py
    iterator = Iter([1, 2, 3])
    # Limit the results to 2.
    for item in iterator.take(2):
        print(item)
    # 1
    # 2

    # Filter the results.
    for item in iterator.filter(lambda item: item > 1):
        print(item)
        print(iterator.count())
    # 2
    # 3
    # 3

    # Indexing is supported.
    print(iterator[0])
    # 1
    ```

    Parameters
    ----------
    items: `Iterable[Item]`
        The items to iterate over. This must be an iterable.
    """

    __slots__ = ("_items",)

    def __init__(self, items: collections.Iterable[Item]) -> None:
        self._items = iter(items)

    @staticmethod
    @typing.final
    def default() -> Iter[ty_ext.Never]:
        """Return the default iterator for this type. It returns an empty iterator.

        Example
        -------
        ```py
        it = Iter.default()
        assert t.next().is_none()
        ```
        """
        return empty()

    @typing.overload
    @typing.final
    def collect(self) -> collections.Sequence[Item]: ...

    @typing.overload
    @typing.final
    def collect(self, *, cast: _B) -> collections.Sequence[_B]: ...

    @typing.final
    def collect(
        self, *, cast: _B | None = None
    ) -> collections.Sequence[Item] | collections.Sequence[_B]:
        """Collects all items in the iterator into an immutable sequence.

        Example
        -------
        ```py
        iterator = Iter(range(3))
        iterator.collect()
        # (0, 1, 2, 3)
        iterator.collect(cast=str) # Map each element and collect it.
        # ('0', '1', '2', '3')
        ```

        Parameters
        ----------
        cast: `T | None`
            An optional type to cast the items into.
            If not provided the items will be returned as it's original type.
        """
        if cast is not None:
            return tuple(map(cast, self._items))

        return tuple(self._items)

    @typing.final
    def to_vec(self) -> Vec[Item]:
        """Convert this iterator into `Vec[T]`.

        Example
        -------
        ```py
        it = sain.iter.once(0)
        vc = it.to_vec()

        assert to_vec == [0]
        ```
        """
        return Vec(self._items)

    @typing.final
    def copied(self) -> Iter[Item]:
        """Creates an iterator which copies all of its elements by value.

        .. note::
            If you only need a copy of the item reference, Use `by_ref` instead.

        Example
        -------
        ```py
        it = Iter([None, None, None])
        copied = it.copied()
        assert it.collect() == copied.collect()
        ```
        """
        return Iter(copy.deepcopy(self._items))

    @typing.final
    def by_ref(self) -> Iter[Item]:
        """Creates an iterator which shallow copies its elements by reference.

        Example
        -------
        ```py
        it = Iter([None, None, None])
        for ref in it.by_ref():
            ...

        # Original not consumed.
        assert it.count() == 3
        ```
        """
        return Iter(copy.copy(self._items))

    def next(self) -> Option[Item]:
        """Returns the next item in the iterator, `Some(None)` if all items yielded.

        Example
        -------
        ```py
        iterator = Iter[str](["1", "2"])
        assert iterator.next() == Some("1")
        assert iterator.next() == Some("2")
        assert iterator.next().is_none()
        ```
        """
        try:
            item = self.__next__()
        except StopIteration:
            # SAFETY: no items left.
            return _option.nothing_unchecked()
        return _option.Some(item)

    def map(
        self, predicate: collections.Callable[[Item], OtherItem]
    ) -> Iter[OtherItem]:
        """Maps each item in the iterator to its predicated value.

        Example
        -------
        ```py
        iterator = Iter(["1", "2", "3"]).map(lambda value: int(value))

        # <Iter([1, 2, 3])>
        for item in iterator:
            assert isinstance(item, int)
        ```

        Parameters
        ----------
        predicate: `collections.Callable[[Item], Item]`
            The function to map each item in the iterator to its predicated value.
        """
        return Iter(predicate(item) for item in self._items)

    def take(self, n: int) -> Iter[Item]:
        """Take the first number of items until the number of items are yielded or
        the end of the iterator is reached.

        Example
        -------
        ```py
        iterator = Iter(['c', 'x', 'y'])
        for mode in iterator.take(2):
            assert mode in ['c', 'x']
        # <Iter(['c', 'x'])>
        ```

        Parameters
        ----------
        n: `int`
            The number of items to take.
        """
        return Iter(itertools.islice(self._items, n))

    def take_while(self, predicate: collections.Callable[[Item], bool]) -> Iter[Item]:
        """Yields items from the iterator while predicate returns `True`.

        Example
        -------
        ```py
        iterator = Iter(['VIP', 'Regular', 'Guard'])
        for membership in iterator.take_while(lambda m: m is 'VIP'):
            print(membership)

        # VIP
        ```

        Parameters
        ----------
        predicate: `collections.Callable[[Item], bool]`
            The function to predicate each item in the iterator.

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return Iter(itertools.takewhile(predicate, self._items))

    def drop_while(self, predicate: collections.Callable[[Item], bool]) -> Iter[Item]:
        """Yields items from the iterator while predicate returns `False`.

        Example
        -------
        ```py
        iterator = Iter(['VIP', 'Regular', 'Guard'])
        for membership in iterator.drop_while(lambda m: m is not 'VIP'):
            print(membership)

        # Regular
        # Guard
        ```

        Parameters
        ----------
        predicate: `collections.Callable[[Item], bool]`
            The function to predicate each item in the iterator.

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return Iter(itertools.dropwhile(predicate, self._items))

    def filter(self, predicate: collections.Callable[[Item], bool]) -> Iter[Item]:
        """Filters the iterator to only yield items that match the predicate.

        Example
        -------
        ```py
        places = Iter(['London', 'Paris', 'Los Angeles'])
        for place in places.filter(lambda place: place.startswith('L')):
            print(place)

        # London
        # Los Angeles
        ```
        """
        return Iter(item for item in self._items if predicate(item))

    def skip(self, n: int) -> Iter[Item]:
        """Skips the first number of items in the iterator.

        Example
        -------
        ```py
        iterator = Iter([MembershipType.STEAM, MembershipType.XBOX, MembershipType.STADIA])
        for platform in iterator.skip(1):
            print(platform)
        # Skip the first item in the iterator.
        # <Iter([MembershipType.XBOX, MembershipType.STADIA])>
        ```
        """
        return Iter(itertools.islice(self._items, n, None))

    def zip(
        self, other: collections.Iterable[OtherItem]
    ) -> Iter[tuple[Item, OtherItem]]:
        """Zips the iterator with another iterable.

        Example
        -------
        ```py
        iterator = Iter([1, 2, 3])
        for item, other_item in iterator.zip([4, 5, 6]):
            assert item == other_item
        <Iter([(1, 4), (2, 5), (3, 6)])>
        ```

        Parameters
        ----------
        other: `Iter[OtherItem]`
            The iterable to zip with.

        Returns
        -------
        `Iter[tuple[Item, OtherItem]]`
            The zipped iterator.

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return Iter(zip(self._items, other))

    def all(self, predicate: collections.Callable[[Item], bool]) -> bool:
        """Return `True` if all items in the iterator match the predicate.

        Example
        -------
        ```py
        iterator = Iter([1, 2, 3])
        while iterator.all(lambda item: isinstance(item, int)):
            print("Still all integers")
            continue
            # Still all integers
        ```

        Parameters
        ----------
        predicate: `collections.Callable[[Item], bool]`
            The function to test each item in the iterator.

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return all(predicate(item) for item in self._items)

    def any(self, predicate: collections.Callable[[Item], bool]) -> bool:
        """`True` if any items in the iterator match the predicate.

        Example
        -------
        ```py
        iterator = Iter([1, 2, 3])
        if iterator.any(lambda item: isinstance(item, int)):
            print("At least one item is an int.")
        # At least one item is an int.
        ```

        Parameters
        ----------
        predicate: `collections.Callable[[Item], bool]`
            The function to test each item in the iterator.

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return any(predicate(item) for item in self._items)

    def sort(
        self,
        *,
        key: collections.Callable[[Item], _typeshed.SupportsRichComparison],
        reverse: bool = False,
    ) -> Iter[Item]:
        """Sorts the iterator.

        Example
        -------
        ```py
        iterator = Iter([3, 1, 6, 7])
        for item in iterator.sort(key=lambda item: item < 3):
            print(item)
        # 1
        # 3
        # 6
        # 7
        ```

        ----------
        key: `collections.Callable[[Item], Any]`
            The function to sort by.
        reverse: `bool`
            Whether to reverse the sort.

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return Iter(sorted(self._items, key=key, reverse=reverse))

    def first(self) -> Option[Item]:
        """Returns the first item in the iterator.

        Example
        -------
        ```py
        iterator = Iter([3, 1, 6, 7])
        iterator.first().is_some_and(lambda x: x == 3)
        ```

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return self.take(1).next()

    def last(self) -> Option[Item]:
        """Returns the last item in the iterator.

        Example
        -------
        ```py
        iterator = Iter([3, 1, 6, 7])
        iterator.last().is_some_and(lambda x: x == 7)
        ```

        Raises
        ------
        `StopIteration`
        If no elements are left in the iterator.
        """
        return self.reversed().first()

    def reversed(self) -> Iter[Item]:
        """Returns a new iterator that yields the items in the iterator in reverse order.

        Example
        -------
        ```py
        iterator = Iter([3, 1, 6, 7])
        for item in iterator.reversed():
            print(item)
        # 7
        # 6
        # 1
        # 3
        ```

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return Iter(reversed(self.collect()))

    def count(self) -> int:
        """Return the count of elements in memory this iterator has.

        Example
        -------
        ```py
        it = Iter(range(3))
        assert it.count() == 3
        ```
        """
        count = 0
        for _ in self:
            count += 1

        return count

    def union(self, other: Iter[Item]) -> Iter[Item]:
        """Returns a new iterator that yields all items from both iterators.

        Example
        -------
        ```py
        iterator = Iter([1, 2, 3])
        other = Iter([4, 5, 6])
        for item in iterator.union(other):
            print(item)
        # 1
        # 2
        # 3
        # 4
        # 5
        # 6
        ```

        Parameters
        ----------
        other: `Iter[Item]`
            The iterable to union with.

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return Iter(itertools.chain(self._items, other))

    def for_each(self, func: collections.Callable[[Item], typing.Any]) -> None:
        """Calls `func` on each item in the iterator.

        Example
        -------
        ```py
        iterator = Iter([1, 2, 3])
        iterator.for_each(lambda item: print(item))
        # 1
        # 2
        # 3
        ```

        Parameters
        ----------
        func: `collections.Callable[[Item], typing.Any]`
            The function to call on each item in the iterator.
        """
        for item in self._items:
            func(item)

    async def async_for_each(
        self,
        func: collections.Callable[
            [Item], collections.Coroutine[None, typing.Any, OtherItem]
        ],
    ) -> _result.Result[collections.Sequence[OtherItem], futures.SpawnErr]:
        """Calls the async function on each item in the iterator concurrently.

        Example
        -------
        ```py
        async def fetch(username: str) -> dict[str, Any]:
            async with aiohttp.request('GET', '...') as r:
                return await r.json()

        async def main():
            users = sain.into_iter(["danny", "legalia"])
            results = await users.async_for_each(lambda username: fetch(username))
            for k, v in results.unwrap().items():
                ...
        ```

        Parameters
        ----------
        func: `collections.Callable[[Item], collections.Coroutine[None, None, None]]`
            The async function to call on each item in the iterator.
        """
        return await futures.spawn(*(func(item) for item in self._items))

    def enumerate(self, *, start: int = 0) -> Iter[tuple[int, Item]]:
        """Returns a new iterator that yields tuples of the index and item.

        Example
        -------
        ```py
        iterator = Iter([1, 2, 3])
        for index, item in iterator.enumerate():
            print(index, item)
        # 0, 1
        # 1, 2
        # 2, 3
        ```

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return Iter(enumerate(self._items, start=start))

    def _ok(self) -> typing.NoReturn:
        raise StopIteration("No more items in the iterator.") from None

    def __getitem__(self, index: int) -> Option[Item]:
        try:
            return self.skip(index).first()
        except IndexError:
            self._ok()

    # This is a never.
    def __setitem__(self, _: None, __: None) -> typing.NoReturn:
        raise NotImplementedError(
            f"{type(self).__name__} doesn't support item assignment."
        ) from None

    def __contains__(self, item: Item) -> bool:
        return item in self._items

    def __reversed__(self) -> Iter[Item]:
        return self.reversed()

    def __repr__(self) -> str:
        return f"<Iter: {type(self._items).__name__}>"

    def __copy__(self) -> Iter[Item]:
        return self.by_ref()

    def __deepcopy__(self) -> Iter[Item]:
        return self.copied()

    def __len__(self) -> int:
        return self.count()

    def __iter__(self) -> Iter[Item]:
        return self

    def __next__(self) -> Item:
        try:
            item = next(self._items)
        except StopIteration:
            self._ok()

        return item


def empty() -> Iter[ty_ext.Never]:
    """Create an iterator that yields nothing.

    Example
    -------
    ```py
    nope = sain.iter.empty()
    assert nope.next().is_none()
    ```
    """
    return Iter(_ for _ in ())


def once(item: Item) -> Iter[Item]:
    """Returns an iterator that yields exactly a single item.

    Example
    -------
    ```py
    iterator = sain.iter.once(1)
    assert iterator.next() == Some(1)
    assert iterator.next() == Some(None)
    ```
    """
    return Iter((item,))


def into_iter(
    iterable: collections.Iterable[Item],
) -> Iter[Item]:
    """Convert an iterable into `Iter`.
    Example
    -------
    ```py
    sequence = [1,2,3]
    for item in sain.iter(sequence).reversed():
        print(item)
    # 3
    # 2
    # 1
    ```

    Parameters
    ----------
    iterable: `Iterable[Item]`
        The iterable to convert.
    """
    return Iter(iterable)
