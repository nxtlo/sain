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
"""Module contains a Standard functional iterator implementation."""

from __future__ import annotations

__all__: typing.Tuple[str, str, str] = ("Iter", "into_iter", "Item")

import itertools
import typing

from . import deafult as _default

Item = typing.TypeVar("Item")
"""A type hint for the item type of the iterator."""

if typing.TYPE_CHECKING:
    import _typeshed as typeshed

    OtherItem = typing.TypeVar("OtherItem")
    _B = typing.TypeVar("_B", bound=typing.Callable[..., typing.Any])


class Iter(typing.Iterator[Item], typing.Generic[Item], _default.Default[typing.Iterable[Item]]):
    """Lazy, In-Memory iterator for sequence types with some functional methods.

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
    items: `typing.Iterable[Item]`
        The items to iterate over. This must be an iterable.
    """

    __slots__ = ("_items",)

    def __init__(self, items: typing.Iterable[Item]) -> None:
        self._items = iter(items)

    @staticmethod
    def default() -> typing.Iterable[Item]:
        """Returns the default value for the iterator. An empty list is returned."""
        return []

    @typing.overload
    def collect(self, /) -> typing.List[Item]:
        ...

    @typing.overload
    def collect(self, casting: _B, /) -> typing.List[_B]:
        ...

    def collect(self, casting: typing.Optional[_B] = None, /) -> typing.Union[typing.List[Item], list[_B]]:
        """Collects all items in the iterator into a list.

        Example
        -------
        >>> iterator = Iter([1, 2, 3])
        >>> iterator.collect()
        [1, 2, 3]
        >>> iterator.collect(str)
        ['1', '2', '3']

        Parameters
        ----------
        casting: `T | None`
            An optional type to cast the items into.
            If not provided the items will be returned as a normal list.

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        if casting is not None:
            return typing.cast("list[_B]", list(map(casting, self._items)))

        return list(self._items)

    def next(self) -> Item:
        """Returns the next item in the iterator.

        Example
        -------
        >>> iterator = Iter[str](["1", "2", "3"])
        item = iterator.next()
        assert item == "1"
        item = iterator.next()
        assert item == "2"

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        try:
            return self.__next__()
        except StopIteration:
            self._ok()

    def map(self, predicate: typing.Callable[[Item], OtherItem]) -> Iter[OtherItem]:
        """Maps each item in the iterator to its predicated value.

        Example
        -------
        >>> iterator = Iter[str](["1", "2", "3"]).map(lambda value: int(value))
        <Iter([1, 2, 3])>
        >>> for item in iterator:
                assert isinstance(item, int)

        Parameters
        ----------
        predicate: `typing.Callable[[Item], Item]`
            The function to map each item in the iterator to its predicated value.

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return Iter(map(predicate, self._items))

    def take(self, n: int) -> Iter[Item]:
        """Take the first number of items until the number of items are yielded or
        the end of the iterator is reached.

        Example
        -------
        >>> iterator = Iter([RAID, STRIKE, GAMBIT])
        >>> for mode in iterator.take(2):
                assert mode in [RAID, STRIKE]
        <Iter([RAID, STRIKE])>

        Parameters
        ----------
        n: `int`
            The number of items to take.

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return Iter(itertools.islice(self._items, n))

    def take_while(self, predicate: typing.Callable[[Item], bool]) -> Iter[Item]:
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
        predicate: `typing.Callable[[Item], bool]`
            The function to predicate each item in the iterator.

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return Iter(itertools.takewhile(predicate, self._items))

    def drop_while(self, predicate: typing.Callable[[Item], bool]) -> Iter[Item]:
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
        predicate: `typing.Callable[[Item], bool]`
            The function to predicate each item in the iterator.

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return Iter(itertools.dropwhile(predicate, self._items))

    def filter(self, predicate: typing.Callable[[Item], bool]) -> Iter[Item]:
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
        return Iter(filter(predicate, self._items))

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
        """
        return Iter(itertools.islice(self._items, n, None))

    def discard(self, predicate: typing.Callable[[Item], bool]) -> Iter[Item]:
        """Discards all elements in the iterator for which the predicate function returns true.

        Example
        -------
        >>> iterator = Iter([MembershipType.STEAM, MembershipType.XBOX, MembershipType.STADIA])
        >>> for _ in iterator.discard(lambda platform: platform is not MembershipType.STEAM):
                # Drops all memberships that are not steam.
                print(iterator)
        <Iter([MembershipType.XBOX, MembershipType.STADIA])>

        Parameters
        ----------
        predicate: `typing.Callable[[Item], bool]`
            The function to test each item in the iterator.

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return Iter(filter(lambda x: not predicate(x), self._items))

    def zip(self, other: Iter[OtherItem]) -> Iter[typing.Tuple[Item, OtherItem]]:
        """Zips the iterator with another iterable.

        Example
        -------
        >>> iterator = Iter([1, 2, 3])
        >>> other = Iter([4, 5, 6])
        >>> for item, other_item in iterator.zip(other):
                assert item == other_item
        <Iter([(1, 4), (2, 5), (3, 6)])>

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

    def all(self, predicate: typing.Callable[[Item], bool]) -> bool:
        """Return `True` if all items in the iterator match the predicate.

        Example
        -------
        >>> iterator = Iter([1, 2, 3])
        >>> while iterator.all(lambda item: isinstance(item, int)):
                print("Still all integers")
                continue
            # Still all integers

        Parameters
        ----------
        predicate: `typing.Callable[[Item], bool]`
            The function to test each item in the iterator.

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return all(predicate(item) for item in self)

    def any(self, predicate: typing.Callable[[Item], bool]) -> bool:
        """`True` if any items in the iterator match the predicate.

        Example
        -------
        >>> iterator = Iter([1, 2, 3])
        >>> if iterator.any(lambda item: isinstance(item, int)):
                print("At least one item is an int.")
        # At least one item is an int.

        Parameters
        ----------
        predicate: `typing.Callable[[Item], bool]`
            The function to test each item in the iterator.

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return any(predicate(item) for item in self)

    def sort(
        self,
        *,
        key: typing.Callable[[Item], typeshed.SupportsRichComparison],
        reverse: bool = False,
    ) -> Iter[Item]:
        """Sorts the iterator.

        Example
        -------
        >>> iterator = Iter([3, 1, 6, 7])
        >>> for item in iterator.sort(key=lambda item: item < 3):
                print(item)
        # 1
        # 3
        # 6
        # 7

        Parameters
        ----------
        key: `typing.Callable[[Item], Any]`
            The function to sort by.
        reverse: `bool`
            Whether to reverse the sort.

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return Iter(sorted(self._items, key=key, reverse=reverse))

    def first(self) -> Item:
        """Returns the first item in the iterator.

        Example
        -------
        >>> iterator = Iter([3, 1, 6, 7])
        >>> iterator.first()
        3

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return self.take(1).next()

    def reversed(self) -> Iter[Item]:
        """Returns a new iterator that yields the items in the iterator in reverse order.

        Example
        -------
        >>> iterator = Iter([3, 1, 6, 7])
        >>> for item in iterator.reversed():
                print(item)
        # 7
        # 6
        # 1
        # 3

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return Iter(reversed(self.collect()))

    def count(self) -> int:
        count = 0
        for _ in self:
            count += 1

        return count

    def union(self, other: Iter[Item]) -> Iter[Item]:
        """Returns a new iterator that yields all items from both iterators.

        Example
        -------
        >>> iterator = Iter([1, 2, 3])
        >>> other = Iter([4, 5, 6])
        >>> for item in iterator.union(other):
                print(item)
        # 1
        # 2
        # 3
        # 4
        # 5
        # 6

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

    def for_each(self, func: typing.Callable[[Item], typing.Any]) -> None:
        """Calls `func` on each item in the iterator.

        Example
        -------
        >>> iterator = Iter([1, 2, 3])
        >>> iterator.for_each(lambda item: print(item))
        # 1
        # 2
        # 3

        Parameters
        ----------
        func: `typing.Callable[[Item], typing.Any]`
            The function to call on each item in the iterator.
        """
        for item in self:
            func(item)

    def enumerate(self, *, start: int = 0) -> Iter[typing.Tuple[int, Item]]:
        """Returns a new iterator that yields tuples of the index and item.
        Example
        -------
        >>> iterator = Iter([1, 2, 3])
        >>> for index, item in iterator.enumerate():
                print(index, item)
        # 0, 1
        # 1, 2
        # 2, 3

        Raises
        ------
        `StopIteration`
            If no elements are left in the iterator.
        """
        return Iter(enumerate(self._items, start=start))

    def _ok(self) -> typing.NoReturn:
        raise StopIteration("No more items in the iterator.") from None

    def __getitem__(self, index: int) -> Item:
        try:
            return self.skip(index).first()
        except IndexError:
            self._ok()

    # This is a never.
    def __setitem__(self) -> typing.NoReturn:
        raise TypeError(f"{type(self).__name__} doesn't support item assignment.") from None

    def __contains__(self, item: Item) -> bool:
        return item in self._items

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}({", ".join([str(item) for item in self._items])})>'

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


def into_iter(
    iterable: typing.Iterable[Item],
) -> Iter[Item]:
    """Convert an iterable into `Iter`.
    Example
    -------
    ```py
    sequence = [1,2,3]
    for item in sain.into_iter(sequence).reversed():
            print(item)
    # 3
    # 2
    # 1
    ```

    Parameters
    ----------
    iterable: `typing.Iterable[Item]`
        The iterable to convert.

    Raises
    ------
    `StopIteration`
        If no elements are left in the iterator.
    """
    return Iter(iterable)
