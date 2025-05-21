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
"""Composable external iteration. See `Iterator` for more details."""

from __future__ import annotations

__all__ = (
    # Core
    "Iter",
    "Iterator",
    "TrustedIter",
    # Adapters
    "Cloned",
    "Copied",
    "Take",
    "Filter",
    "Map",
    "Skip",
    "Enumerate",
    "TakeWhile",
    "DropWhile",
    "Chunks",
    "Empty",
    "Repeat",
    "Once",
    "ExactSizeIterator",
    # Functions
    "into_iter",
    "empty",
    "once",
    "repeat",
)

import abc
import collections.abc as collections
import copy
import itertools
import typing

from . import default as _default
from . import futures
from . import option as _option
from . import result as _result
from .collections import vec as _vec
from .macros import rustc_diagnostic_item
from .macros import unsafe

Item = typing.TypeVar("Item")
"""The type of the item that is being yielded."""

OtherItem = typing.TypeVar("OtherItem")
"""The type of the item that is being mapped into then yielded."""

AnyIter = typing.TypeVar("AnyIter", bound="Iterator[typing.Any]")


if typing.TYPE_CHECKING:
    import _typeshed

    from .option import Option

    Collector = (
        collections.MutableSequence[Item]
        | set[Item]
        | collections.MutableMapping[int, Item]
    )
    _typeshed.ConvertibleToInt
    Sum: typing.TypeAlias = (
        "Iterator[str]"
        | "Iterator[typing.SupportsInt]"
        | "Iterator[typing.SupportsIndex]"
        | "Iterator[_typeshed.ReadableBuffer]"
        | "Iterator[_typeshed.SupportsTrunc]"
        | "Iterator[float]"
    )


def unreachable() -> typing.NoReturn:
    raise StopIteration(
        "No more items exist in this iterator. It has been exhausted."
    ) from None


def diagnostic(cls: type[AnyIter]) -> type[AnyIter]:
    def _repr(self: Iterator[typing.Any]) -> str:
        return f"{type(self).__name__}(source: Iter<{type(self._it).__name__}>)"  # pyright: ignore

    cls.__repr__ = _repr
    return cls


@rustc_diagnostic_item("Iterator")
class Iterator(
    typing.Generic[Item],
    abc.ABC,
    _default.Default["Empty[Item]"],
):
    """An abstract interface for dealing with iterators.

    This is exactly the same trait as `core::iter::Iterator` trait from Rust.

    This is the main interface that any type can implement by basically inheriting from it.
    The method `__next__` is the only method that needs to be implemented, You get all the other methods for free.

    If you want to use a ready iterator for general purposes, Use `Iter`. This interface is only for implementors
    and type hints.

    Example
    -------
    ```py
    @dataclass
    class Counter(Iterator[int]):
        start: int = 0
        stop: int | None = None

        # implement the required method.
        def __next__(self) -> int:
            result = self.start
            self.start += 1

            if self.stop is not None and result >= self.stop:
                raise StopIteration

            return result

    counter = Counter(start=0, stop=10)
    for i in counter.map(lambda x: x * 2): # multiply each number
        ...
    ```
    """

    __slots__ = ()

    @abc.abstractmethod
    def __next__(self) -> Item:
        raise NotImplementedError

    ###################
    # const functions #
    ###################

    @staticmethod
    @typing.final
    def default() -> Empty[Item]:
        """Return the default iterator for this type. It returns an empty iterator.

        Example
        -------
        ```py
        it: Iterator[int] = Iter.default()
        assert t.next().is_none()
        ```
        """
        return Empty()

    @typing.overload
    def collect(self) -> collections.MutableSequence[Item]: ...

    @typing.overload
    def collect(
        self, *, cast: collections.Callable[[Item], OtherItem]
    ) -> collections.MutableSequence[OtherItem]: ...

    @typing.final
    def collect(
        self, *, cast: collections.Callable[[Item], OtherItem] | None = None
    ) -> collections.MutableSequence[Item] | collections.MutableSequence[OtherItem]:
        """Collects all items in the iterator into a sequence.

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
            return list(cast(i) for i in self)

        return list(_ for _ in self)

    @typing.final
    def collect_into(self, collection: Collector[Item]) -> None:
        """Consume this iterator, extending all items in the iterator into a mutable `collection`.

        Example
        -------
        ```py
        iterator = Iter([1, 1, 2, 3, 4, 2, 6])
        uniques = set()
        iterator.collect_into(uniques)
        # assert uniques == {1, 2, 3, 4, 6}
        ```

        Parameters
        ----------
        collection: `MutableSequence[T]` | `set[T]`
            The collection to extend the items in this iterator with.
        """
        if isinstance(collection, collections.MutableSequence):
            collection.extend(_ for _ in self)
        elif isinstance(collection, collections.MutableSet):
            collection.update(_ for _ in self)
        else:
            for idx, item in enumerate(self):
                collection[idx] = item

    @typing.final
    def to_vec(self) -> _vec.Vec[Item]:
        """Convert this iterator into `Vec[T]`.

        Example
        -------
        ```py
        it = sain.iter.once(0)
        vc = it.to_vec()

        assert to_vec == [0]
        ```
        """
        return _vec.Vec(_ for _ in self)

    @typing.final
    def sink(self) -> None:
        """Consume all elements from this iterator, flushing it into the sink.

        Example
        -------
        ```py
        it = Iter((1, 2, 3))
        it.sink()
        assert it.next().is_none()
        ```
        """
        for _ in self:
            pass

    @typing.final
    def raw_parts(self) -> collections.Generator[Item, None, None]:
        """Decompose this iterator into a `Generator[Item]` that yields all of the remaining items.

        This mainly used for objects that needs to satisfy its exact type.

        ```py
        it = Iter("cba")
        sort = sorted(it.raw_parts())

        assert it.count() == 0
        assert sort == ["a", "b", "c"]
        ```
        """
        for item in self:
            yield item

    ##################
    # default impl's #
    ##################

    def next(self) -> Option[Item]:
        """Advance the iterator, Returning the next item, `Some(None)` if all items yielded.

        Example
        -------
        ```py
        iterator = Iter(["1", "2"])
        assert iterator.next() == Some("1")
        assert iterator.next() == Some("2")
        assert iterator.next().is_none()
        ```
        """
        try:
            return _option.Some(self.__next__())
        except StopIteration:
            # ! SAFETY: No more items in the iterator.
            return _option.NOTHING

    def cloned(self) -> Cloned[Item]:
        """Creates an iterator which shallow copies its elements by reference.

        If you need a copy of the actual iterator and not the elements.
        use `Iter.clone()`

        .. note::
            This method calls [`copy.copy()`](https://docs.python.org/3/library/copy.html)
            on each item that is being yielded.

        Example
        -------
        ```py
        @dataclass
        class User:
            users_ids: list[int] = []

        # An iterator which elements points to the same user.
        user = User()
        it = Iter((user, user))

        for u in it.cloned():
            u.user_ids.append(1)

        # We iterated over the same user pointer twice and appended "1"
        # since `copy` returns a shallow copy of nested structures.
        assert len(user.user_ids) == 2
        ```
        """
        return Cloned(self)

    def copied(self) -> Copied[Item]:
        """Creates an iterator which copies all of its elements by value.

        If you only need a copy of the item reference, Use `.cloned()` instead.

        .. note::
            This method simply calls [`copy.deepcopy()`](https://docs.python.org/3/library/copy.html)
            on each item that is being yielded.

        Example
        -------
        ```py
        @dataclass
        class User:
            users_ids: list[int] = []

        # An iterator which elements points to the same user.
        user = User()
        it = Iter((user, user))

        for u in it.copied():
            # A new list is created for each item.
            u.user_ids.append(1)

        # The actual list is untouched since we consumed a deep copy of it.
        assert len(user.user_ids) == 0
        ```
        """
        return Copied(self)

    def map(self, fn: collections.Callable[[Item], OtherItem]) -> Map[Item, OtherItem]:
        """Maps each item in the iterator to another type.

        Example
        -------
        ```py
        iterator = Iter(["1", "2", "3"]).map(int)

        for item in iterator:
            assert isinstance(item, int)
        ```

        Parameters
        ----------
        predicate: `Callable[[Item], OtherItem]`
            The function to map each item in the iterator to the other type.
        """
        return Map(self, fn)

    def filter(self, predicate: collections.Callable[[Item], bool]) -> Filter[Item]:
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
        return Filter(self, predicate)

    def take(self, count: int) -> Take[Item]:
        """Take the first number of items until the number of items
        are yielded or the end of the iterator is exhausted.

        Example
        -------
        ```py
        iterator = Iter(['c', 'x', 'y'])

        for x in iterator.take(2):
            assert x in ('c', 'x')

        # <Iter(['c', 'x'])>
        ```
        """
        return Take(self, count)

    def skip(self, count: int) -> Skip[Item]:
        """Skips the first number of items in the iterator.

        Example
        -------
        ```py
        iterator = Iter((1, 2, 3, 4))
        for i in iterator.skip(2):
            print(i)

        # 3
        # 4
        ```
        """
        return Skip(self, count)

    def enumerate(self, *, start: int = 0) -> Enumerate[Item]:
        """Create a new iterator that yields a tuple of the index and item.

        Example
        -------
        ```py
        iterator = Iter([1, 2, 3])
        for index, item in iterator.enumerate():
            print(index, item)

        # 0 1
        # 1 2
        # 2 3
        ```
        """
        return Enumerate(self, start)

    def take_while(self, f: collections.Callable[[Item], bool]) -> TakeWhile[Item]:
        """yields items from the iterator while predicate returns `True`.

        The rest of the items are discarded as soon as the predicate returns `False`

        Example
        -------
        ```py
        iterator = Iter(['a', 'ab', 'xd', 'ba'])
        for x in iterator.take_while(lambda x: 'a' in x):
            print(x)

        # a
        # ab
        ```

        Parameters
        ----------
        predicate: `collections.Callable[[Item], bool]`
            The function to predicate each item in the iterator.
        """
        return TakeWhile(self, f)

    def drop_while(self, f: collections.Callable[[Item], bool]) -> DropWhile[Item]:
        """Yields items from the iterator while predicate returns `False`.

        Example
        -------
        ```py
        iterator = Iter(['a', 'ab', 'xd', 'ba'])
        for x in iterator.drop_while(lambda x: 'a' in x):
            print(x)

        # xd
        # ba
        ```

        Parameters
        ----------
        predicate: `collections.Callable[[Item], bool]`
            The function to predicate each item in the iterator.
        """
        return DropWhile(self, f)

    def chunks(self, chunk_size: int, /) -> Chunks[Item]:
        """Returns an iterator over `chunk_size` elements of the iterator at a time,
        starting at the beginning of the iterator.

        Example
        -------
        ```py
        iter = Iter(['a', 'b', 'c', 'd', 'e'])
        chunks = iter.chunks()
        assert chunks.next().unwrap() == ['a', 'b']
        assert chunks.next().unwrap() == ['c', 'd']
        assert chunks.next().unwrap() == ['e']
        assert chunks.next().is_none()
        ```
        """
        return Chunks(self, chunk_size)

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
        """
        return all(predicate(item) for item in self)

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
        """
        return any(predicate(item) for item in self)

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

        """
        return Iter(zip(self.raw_parts(), other))

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

        Parameters
        ----------
        key: `collections.Callable[[Item], Any]`
            The function to sort by.
        reverse: `bool`
            Whether to reverse the sort.
        """
        return Iter(sorted(self.raw_parts(), key=key, reverse=reverse))

    def reversed(self) -> Iter[Item]:
        """Returns a new iterator that yields the items in the iterator in reverse order.

        This consumes this iterator into a sequence and return a new iterator containing all of the elements
        in reversed order.

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
        """
        # NOTE: In order to reverse the iterator we need to
        # first collect it into some collection.
        return Iter(reversed(list(_ for _ in self)))

    def union(self, other: collections.Iterable[Item]) -> Iter[Item]:
        """Returns a new iterator that yields all items from both iterators.

        Example
        -------
        ```py
        iterator = Iter([1, 2, 3])
        other = [4, 5, 6]

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
        """
        return Iter(itertools.chain(self.raw_parts(), other))

    def first(self) -> Option[Item]:
        """Returns the first item in the iterator.

        Example
        -------
        ```py
        iterator = Iter([3, 1, 6, 7])
        iterator.first().is_some_and(lambda x: x == 3)
        ```
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
        """
        return self.reversed().first()

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

    def find(self, predicate: collections.Callable[[Item], bool]) -> Option[Item]:
        """Searches for an element of an iterator that satisfies a predicate.

        If you want the position of the element, use `Iterator.position` instead.

        `find()` takes a lambda that returns true or false. It applies this closure to each element of the iterator,
        and if any of them return true, then find() returns `Some(element)`. If they all return false, it returns None.

        Example
        -------
        ```py
        it = Iter(range(10))
        item = it.find(lambda num: num > 5)
        print(item) # 6
        ```
        """
        for item in self:
            if predicate(item):
                return _option.Some(item)

        # no more items
        return _option.NOTHING

    def position(self, predicate: collections.Callable[[Item], bool]) -> Option[int]:
        """Searches for the position of an element in the iterator that satisfies a predicate.

        If you want the object itself, use `Iterator.find` instead.

        `position()` takes a lambda that returns true or false. It applies this closure to each element of the iterator,
        and if any of them return true, then position() returns `Some(position_of_element)`. If they all return false, it returns None.

        Example
        -------
        ```py
        it = Iter(range(10))
        position = it.find(lambda num: num > 5)
        assert position.unwrap() == 6
        ```
        """
        for position, value in self.enumerate():
            if predicate(value):
                return _option.Some(position)

        # no more items
        return _option.NOTHING

    def fold(
        self, init: OtherItem, f: collections.Callable[[OtherItem, Item], OtherItem]
    ) -> OtherItem:
        """Folds every element into an accumulator by applying an operation, returning the final result.

        fold() takes two arguments: an initial value, and a closure with two arguments: an ‘accumulator’, and an element.
        The closure returns the value that the accumulator should have for the next iteration.

        The initial value is the value the accumulator will have on the first call.

        After applying this closure to every element of the iterator, fold() returns the accumulator.

        This operation is sometimes called ‘reduce’ or ‘inject’.

        Example
        -------
        ```py
        a = Iter([1, 2, 3, 4])
        sum = a.fold(0, lambda acc, elem: acc + elem)
        assert sum == 10
        ```
        """
        accum = init
        while True:
            try:
                x = self.__next__()
                accum = f(accum, x)
            except StopIteration:
                break

        return accum

    def advance_by(self, n: int) -> _result.Result[None, int]:
        """Advances the iterator by `n` elements.

        Returns `Result[None, int]`, where `Ok(None)` means the iterator
        advanced successfully, and `Err(int)` if `None` encountered, where `int`
        represents the remaining number of steps that could not be advanced because the iterator ran out.

        Example
        -------
        ```py
        it = into_iter([1, 2, 3, 4])
        assert it.advance_by(2).is_ok()
        assert it.next() == Some(3)
        assert it.advance_by(0).is_ok()
        assert it.advance_by(100) == Err(99)
        ```
        """
        for i in range(n):
            try:
                self.__next__()
            except StopIteration:
                return _result.Err(n - i)

        return _result.Ok(None)

    def nth(self, n: int) -> Option[Item]:
        """Returns the `n`th element of the iterator

        Just like normal indexing, the count `n` starts from zero, so `nth(0)` returns the first
        value.

        Note all elements before `n` will be skipped / consumed.

        Example
        -------
        ```py
        a = into_iter([1, 2, 3])
        assert a.iter().nth(1) == Some(2)
        ```
        """
        for _ in range(n):
            try:
                self.__next__()
            except StopIteration:
                return _option.NOTHING

        return self.next()

    def sum(self: Sum) -> int:
        """Sums an iterator of a possible type that can be converted to an integer.

        Example
        -------
        ```py
        numbers: Iterator[str] = Iter(["1", "2", "3"])
        total = numbers.sum()
        assert total == 6
        ```
        """
        return sum(int(_) for _ in self)

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
        for item in self:
            func(item)

    async def async_for_each(
        self,
        func: collections.Callable[
            [Item], collections.Coroutine[typing.Any, typing.Any, OtherItem]
        ],
    ) -> _result.Result[collections.Sequence[OtherItem], futures.JoinError]:
        """Calls the async function on each item in the iterator *concurrently*.

        Concurrently meaning that the next item will not wait for other items
        to finish to execute, each item gets called in a separate task.

        After all the tasks finish, a `Result[list[T], JoinError]` will be returned,
        which will need to be handled by the caller.

        Example
        -------
        ```py
        async def create_user(username: str) -> None:
            await aiohttp.request("POST", f'.../{username}')

        async def main():
            users = sain.into_iter(["Danny", "Flower"])
            match await users.async_for_each(lambda username: create_user(username)):
                case Ok(result):
                    # all good
                case Err(why):
                    print(f"couldn't gather all futures, err={why}")
        ```

        Parameters
        ----------
        func: `collections.Callable[[Item], Coroutine[None, Any, Any]]`
            The async function to call on each item in the iterator.
        """
        return await futures.join(*(func(item) for item in self))

    def __reversed__(self) -> Iter[Item]:
        return self.reversed()

    def __repr__(self) -> str:
        return "<Iterator>"

    def __copy__(self) -> Cloned[Item]:
        return self.cloned()

    def __deepcopy__(
        self, memo: collections.MutableMapping[int, typing.Any], /
    ) -> Copied[Item]:
        return self.copied()

    def __len__(self) -> int:
        return self.count()

    def __iter__(self) -> Iterator[Item]:
        return self


class ExactSizeIterator(typing.Generic[Item], Iterator[Item], abc.ABC):
    """An iterator that knows its exact size.

    The implementations of this interface indicates that the iterator knows exactly
    how many items it can yield.

    however, this is not a requirement for the iterator to implement this trait, as its
    only used for iterators that can know their size.

    Example
    -------
    ```py
    @dataclass
    class Letters(ExactSizeIterator[str]):
        letters: list[str]

        def __next__(self) -> str:
            return self.letters.pop(0)

        def __len__(self) -> int:
            return len(self.letters)

    letters = Letters(['a', 'b', 'c'])
    assert letters.count() == 3
    assert letters.next() == Some('a')
    assert letters.count() == 2
    ```
    """

    __slots__ = ()

    @typing.final
    def count(self) -> int:
        return len(self)

    @typing.final
    def len(self) -> int:
        """Returns the remaining number of items in the iterator.

        This doesn't exhaust the iterator.

        Example
        -------
        ```py
        it = once(0)
        assert it.len() == 1
        assert it.len() == 1
        it.next()
        assert it.len() == 0
        ```
        """
        return len(self)

    @typing.final
    def is_empty(self) -> bool:
        """Return `True` if this iterator has no items left to yield.

        Example
        -------
        ```py
        iterator = once(1)
        assert not iterator.is_empty()
        assert once.next() == Some(1)
        assert iterator.is_empty()
        ```
        """
        return len(self) == 0

    @abc.abstractmethod
    def __len__(self) -> int: ...


@rustc_diagnostic_item("Iter")
@typing.final
@diagnostic
class Iter(typing.Generic[Item], Iterator[Item]):
    """a lazy iterator that has its items ready in-memory.

    This is similar to Rust `std::slice::Iter<T>` item which iterables can build
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
        The items to iterate over. This can be anything that implements `__iter__` and `__next__`.
    """

    __slots__ = ("_it",)

    def __init__(self, iterable: collections.Iterable[Item]) -> None:
        self._it = iter(iterable)

    def clone(self) -> Iter[Item]:
        """Return a copy of this iterator.

        ```py
        it = Iterator([1, 2, 3])

        for i in it.clone():
            ...

        # The actual iterator hasn't been exhausted.
        assert it.count() == 3
        ```
        """
        return Iter(copy.copy(self._it))

    def __next__(self) -> Item:
        return next(self._it)

    def __getitem__(self, index: int) -> Option[Item]:
        try:
            return self.skip(index).first()
        except IndexError:
            unreachable()

    def __contains__(self, item: Item) -> bool:
        return item in self._it


@typing.final
class TrustedIter(typing.Generic[Item], ExactSizeIterator[Item]):
    """Similar to `Iter`, but it reports an accurate length using `ExactSizeIterator`.

    iterable objects such as `Vec`, `Bytes`, `list` and other `Sized` may be created
    using this iterator.

    Example
    -------
    ```py
    # we know the size of the iterator.
    sized_buf: TrustedIter[int] = into_iter((1, 2, 3, 4))
    # this is `Iter[int]` since we don't know when the generator will stop yielding.
    unsized_buf: Iter[int] = into_iter((_ for _ in ([1, 2, 3, 4] if cond else [1, 2])))
    ```

    Parameters
    ----------
    items: `collections.Collection[Item]`
        A sized collection of items to iterate over.
    """

    __slots__ = ("_it", "_len", "__alive")

    def __init__(self, iterable: collections.Sequence[Item]) -> None:
        self.__alive = iterable
        self._len = len(iterable)
        self._it = iter(iterable)

    def next(self) -> Option[Item]:
        if self._len == 0:
            # ! SAFETY: len == 0
            return _option.NOTHING

        return _option.Some(self.__next__())

    @unsafe
    def next_unchecked(self) -> Item:
        """Returns the next item in the iterator without checking if it exists.

        This is equivalent to calling `next()` on the iterator directly.

        Example
        -------
        ```py
        iterator = Iter([1])
        assert iterator.next_unchecked() == 1
        iterator.next_unchecked() # raises StopIteration
        ```
        """
        return self.__next__()

    def as_slice(self) -> collections.Sequence[Item]:
        """Returns an immutable slice of all elements that have not been yielded

        Example
        -------
        ```py
        iterator = into_iter([1, 2, 3])
        iterator.as_slice() == [1, 2, 3]
        iterator.next()
        assert iterator.as_slice() == [2, 3]
        ```
        """
        return self.__alive[-self._len :]

    def __repr__(self) -> str:
        return f"TrustedIter({self.as_slice()})"

    def __next__(self) -> Item:
        i = next(self._it)
        self._len -= 1
        return i

    def __getitem__(self, index: int) -> Option[Item]:
        if self._len == 0:
            return _option.NOTHING

        try:
            return self.skip(index).first()
        except IndexError:
            unreachable()

    def __contains__(self, item: Item) -> bool:
        return item in self._it

    def __len__(self) -> int:
        return self._len


@diagnostic
class Cloned(typing.Generic[Item], Iterator[Item]):
    """An iterator that copies the elements from an underlying iterator.

    This iterator is created by the `Iterator.cloned` method.
    """

    __slots__ = ("_it",)

    def __init__(self, it: Iterator[Item]) -> None:
        self._it = it

    def __next__(self) -> Item:
        n = self._it.__next__()

        # Avoid useless function call for a list.
        if isinstance(n, list):
            # SAFETY: We know this is a list.
            return n[:]  # pyright: ignore

        return copy.copy(n)


@diagnostic
class Copied(typing.Generic[Item], Iterator[Item]):
    """An iterator that deeply-copies the elements from an underlying iterator.

    This iterator is created by the `Iterator.copied` method.
    """

    __slots__ = ("_it",)

    def __init__(self, it: Iterator[Item]) -> None:
        self._it = it

    def __next__(self) -> Item:
        return copy.deepcopy(self._it.__next__())


@diagnostic
class Map(typing.Generic[Item, OtherItem], Iterator[OtherItem]):
    """An iterator that maps the elements to a callable.

    This iterator is created by the `Iterator.map` method.
    """

    __slots__ = ("_it", "_call")

    def __init__(
        self, it: Iterator[Item], call: collections.Callable[[Item], OtherItem]
    ) -> None:
        self._it = it
        self._call = call

    def __next__(self) -> OtherItem:
        return self._call(self._it.__next__())


@diagnostic
class Filter(typing.Generic[Item], Iterator[Item]):
    """An iterator that filters the elements to a `predicate`.

    This iterator is created by the `Iterator.filter` method.
    """

    __slots__ = ("_it", "_call")

    def __init__(
        self, it: Iterator[Item], call: collections.Callable[[Item], bool]
    ) -> None:
        self._it = it
        self._call = call

    def __next__(self) -> Item:
        for item in self._it:
            if self._call(item):
                return item

        unreachable()


@diagnostic
class Take(typing.Generic[Item], Iterator[Item]):
    """An iterator that yields the first `number` of elements and drops the rest.

    This iterator is created by the `Iterator.take` method.
    """

    __slots__ = ("_it", "_taken", "_count")

    def __init__(self, it: Iterator[Item], count: int) -> None:
        if count <= 0:
            raise ValueError("`count` must be non-zero")

        self._it = it
        self._taken = count
        self._count = 0

    def __next__(self) -> Item:
        if self._count >= self._taken:
            unreachable()

        item = self._it.__next__()
        self._count += 1
        return item


@diagnostic
class Skip(typing.Generic[Item], Iterator[Item]):
    """An iterator that skips the first `number` of elements and yields the rest.

    This iterator is created by the `Iterator.skip` method.
    """

    __slots__ = ("_it", "_count", "_skipped")

    def __init__(self, it: Iterator[Item], count: int) -> None:
        if count <= 0:
            raise ValueError("`count` must be non-zero")

        self._it = it
        self._count = count
        self._skipped = 0

    def __next__(self) -> Item:
        while self._skipped < self._count:
            self._skipped += 1
            self._it.__next__()

        return self._it.__next__()


@diagnostic
class Enumerate(typing.Generic[Item], Iterator[tuple[int, Item]]):
    """An iterator that yields the current count and the element during iteration.

    This iterator is created by the `Iterator.enumerate` method.
    """

    __slots__ = ("_it", "_count")

    def __init__(self, it: Iterator[Item], start: int) -> None:
        self._it = it
        self._count = start

    def __next__(self) -> tuple[int, Item]:
        a = self._it.__next__()
        i = self._count
        self._count += 1
        return i, a


@diagnostic
class TakeWhile(typing.Generic[Item], Iterator[Item]):
    """An iterator that yields elements while `predicate` returns `True`.

    This iterator is created by the `Iterator.take_while` method.
    """

    __slots__ = ("_it", "_predicate")

    def __init__(
        self, it: Iterator[Item], predicate: collections.Callable[[Item], bool]
    ) -> None:
        self._it = it
        self._predicate = predicate

    def __next__(self) -> Item:
        item = self._it.__next__()

        if self._predicate(item):
            return item

        unreachable()


@diagnostic
class DropWhile(typing.Generic[Item], Iterator[Item]):
    """An iterator that yields elements while `predicate` returns `False`.

    This iterator is created by the `Iterator.drop_while` method.
    """

    __slots__ = ("_it", "_predicate", "_dropped")

    def __init__(
        self, it: Iterator[Item], predicate: collections.Callable[[Item], bool]
    ) -> None:
        self._it = it
        self._predicate = predicate
        self._dropped = False

    def __next__(self) -> Item:
        if not self._dropped:
            while not self._predicate(item := self._it.__next__()):
                pass

            self._dropped = True
            return item

        unreachable()


@diagnostic
class Chunks(typing.Generic[Item], Iterator[collections.Sequence[Item]]):
    """An iterator that yields elements in chunks.

    This iterator is created by the `Iterator.chunks` method.
    """

    __slots__ = ("chunk_size", "_it")

    def __init__(self, it: Iterator[Item], chunk_size: int) -> None:
        self.chunk_size = chunk_size
        self._it = it

    def __next__(self) -> collections.Sequence[Item]:
        chunk: list[Item] = []

        for item in self._it:
            chunk.append(item)

            if len(chunk) == self.chunk_size:
                break

        if chunk:
            return chunk

        unreachable()


@typing.final
@diagnostic
class Empty(typing.Generic[Item], ExactSizeIterator[Item]):
    """An iterator that yields nothing.

    This is the default iterator that is created by `Iterator.default()` or `empty()`
    """

    __slots__ = ()

    def __init__(self) -> None:
        pass

    def next(self) -> Option[Item]:
        # SAFETY: an empty iterator always returns None.
        # also we avoid calling `nothing_unchecked()` here for fast returns.
        return _option.NOTHING

    def __len__(self) -> typing.Literal[0]:
        return 0

    def any(
        self, predicate: collections.Callable[[Item], bool]
    ) -> typing.Literal[False]:
        return False

    def all(
        self, predicate: collections.Callable[[Item], bool]
    ) -> typing.Literal[False]:
        return False

    def __next__(self) -> Item:
        unreachable()


@typing.final
@diagnostic
class Repeat(typing.Generic[Item], ExactSizeIterator[Item]):
    """An iterator that repeats a given value an exact number of times.

    This iterator is created by calling `repeat()`.
    """

    __slots__ = ("_count", "_element")

    def __init__(self, element: Item, count: int) -> None:
        self._count = count
        self._element = element

    def __next__(self) -> Item:
        if self._count > 0:
            self._count -= 1
            if self._count == 0:
                # Return the origin element last
                return self._element

            return copy.copy(self._element)

        unreachable()

    def __len__(self) -> int:
        return self._count


@typing.final
@diagnostic
class Once(typing.Generic[Item], ExactSizeIterator[Item]):
    """An iterator that yields exactly one item.

    This iterator is created by calling `once()`.
    """

    __slots__ = ("_item",)

    def __init__(self, item: Item) -> None:
        self._item: Option[Item] = _option.Some(item)

    def __next__(self) -> Item:
        return self._item.take().unwrap_or_else(unreachable)

    def __len__(self) -> typing.Literal[0, 1]:
        return 1 if self._item else 0


# a hack to trick the type-checker into thinking that this iterator yield `Item`.
@rustc_diagnostic_item("empty")
def empty() -> Empty[Item]:  # pyright: ignore
    """Create an iterator that yields nothing.

    Example
    -------
    ```py
    nope: Iterator[int] = sain.iter.empty()
    assert nope.next().is_none()
    ```
    """
    return Empty()


@rustc_diagnostic_item("repeat")
def repeat(element: Item, count: int) -> Repeat[Item]:
    """Returns an iterator that yields the exact same `element` number of `count` times.

    The yielded elements is a copy of `element`, but the last element is guaranteed to be the same as the
    original `element`.

    Example
    -------
    ```py
    nums = [1, 2, 3]
    it = sain.iter.repeat(nums, 5)
    for i in range(4):
        cloned = it.next().unwrap()
        assert cloned == [1, 2, 3]

    # But the last item is the origin one...
    last = it.next().unwrap()
    last.append(4)
    assert nums == [1, 2, 3, 4]
    ```
    """
    return Repeat(element, count)


@rustc_diagnostic_item("once")
def once(item: Item) -> Once[Item]:
    """Returns an iterator that yields exactly a single item.

    Example
    -------
    ```py
    iterator = sain.iter.once(1)
    assert iterator.next() == Some(1)
    assert iterator.next() == Some(None)
    ```
    """
    return Once(item)


@typing.overload
def into_iter(
    iterable: collections.Sequence[Item],
) -> TrustedIter[Item]: ...


@typing.overload
def into_iter(
    iterable: collections.Iterable[Item],
    /,
) -> Iter[Item]: ...


@rustc_diagnostic_item("into_iter")
def into_iter(
    iterable: collections.Sequence[Item] | collections.Iterable[Item],
) -> Iter[Item] | TrustedIter[Item] | TrustedIter[int]:
    """Convert any iterable into `Iterator[Item]`.

    if the size of the iterable is known, it will return `TrustedIter`,
    otherwise it will return `Iter`.

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
    """
    if isinstance(iterable, collections.Sequence):
        return TrustedIter(iterable)
    return Iter(iterable)
