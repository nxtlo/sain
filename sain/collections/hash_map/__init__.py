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
"""An extended version of built-in `dict` but with extra functionality.

This contains Rust's `std::collections::HashMap` methods.
"""

from __future__ import annotations

__all__ = ("HashMap", "RefMut")

import collections.abc as collections
import typing

from sain import option as option
from sain.convert import From
from sain.convert import Into
from sain.default import Default
from sain.macros import override
from sain.macros import rustc_diagnostic_item
from sain.result import Err
from sain.result import Ok

from .base_iter import Drain
from .base_iter import ExtractIf
from .base_iter import Fn
from .base_iter import IntoIterator
from .base_iter import IntoKeys
from .base_iter import IntoValues
from .base_iter import Iter

K = typing.TypeVar("K")
V = typing.TypeVar("V")

if typing.TYPE_CHECKING:
    from typing_extensions import Never
    from typing_extensions import Self

    from sain.option import Option
    from sain.result import Result


class _RawMap(
    typing.Generic[K, V],
    collections.Mapping[K, V],
    From[collections.Iterable[tuple[K, V]]],
    Into[list[tuple[K, V]]],
):
    __slots__ = ("_source",)

    def __init__(self, source: dict[K, V] | None = None, /) -> None:
        self._source = source if source else {}

    # constructors

    @classmethod
    def from_keys(cls, *iterable: tuple[K, V]) -> HashMap[K, V]:
        """Create a new `HashMap` from a sequence of key-value pairs.

        Example
        -------
        ```py
        tier_list = [
            ("S", "Top tier"),
            ("A", "Very Good"),
            ("B", "Good"),
            ("C", "Average"),
            ("D", "dodo")
        ]
        mapping = HashMap[str, str].from_keys(*tier_list)
        ```
        """
        return HashMap({k: v for k, v in iterable})

    # trait impls

    @classmethod
    @override
    def from_value(cls, value: collections.Iterable[tuple[K, V]]) -> HashMap[K, V]:
        """Creates a `HashMap` from an iterable of `(K, V)` key-value paris.

        Same as `HashMap.from_keys(*iter)`
        """
        return HashMap({k: v for k, v in value})

    @override
    def into(self) -> list[tuple[K, V]]:
        """Turn this `HashMap` into a `[(K, V); len(self)]` key-value paris.

        `self` is consumed afterwards.

        Example
        -------
        ```py
        users = [(0, "user-0"), (1, "user-1")]
        map1 = HashMap.from_keys(*users)
        assert map1.into() == users
        # map1 is dropped.
        ```
        """
        return [(k, v) for k, v in self.leak().items()]

    # default impls

    def into_keys(self) -> IntoKeys[K]:
        """Creates an iterator that consumes the map, yielding all of its keys.

        `self` cannot be used after calling this.

        Example
        -------
        ```py
        map1 = HashMap({
            "a": 1,
            "b": 2,
            "c": 3,
        })
        keys = map1.into_keys().collect()
        assert keys == ["a", "b", "c"]
        ```
        """
        return IntoKeys(self.leak().keys())

    def into_values(self) -> IntoValues[V]:
        """Creates an iterator that consumes the map, yielding all of its values.

        `self` cannot be used after calling this.

        Example
        -------
        ```py
        map1 = HashMap({
            "a": 1,
            "b": 2,
            "c": 3,
        })
        values = map1.into_values().collect()
        assert values == [1, 2, 3]
        ```
        """
        return IntoValues(self.leak().values())

    def contains_key(self, k: K) -> bool:
        """Check whether `k` is in `self` or not.

        Example
        -------
        ```py
        users = HashMap({0: "user-0"})
        assert users.contains_key(0) is True
        # similar to just doing
        assert 0 in users
        ```
        """
        return k in self

    def is_empty(self) -> bool:
        """Whether this `self` contains any items or not.

        Example
        -------
        ```py
        storage: HashMap[str, None] = HashMap()
        if storage.is_empty():
            ...
        # Or just
        if not storage:
            ...
        ```
        """
        return not self

    @override
    def get(self, key: K) -> Option[V]:
        """Get the value associated with `key`, returns `None` if not found.

        Unlike `dict.get` which returns builtin `None`, This returns `Option[T]`.

        Example
        -------
        ```py
        users: HashMap[str, int] = HashMap()
        assert users.get("jack").is_none()

        users = HashMap({"jack": None})
        assert users.get("jack").is_some()
        ```
        """
        if key not in self:
            return option.NOTHING

        return option.Some(self._source[key])

    def get_with(self, f: collections.Callable[[], K]) -> Option[V]:
        """Get the value associated with `key` returned from a callable `f()`, returns `None` if not found.

        Example
        -------
        ```py
        def get_id() -> int:
            return 0

        map = HashMap({0: "buh", 1: "guh", 2: "luh"})
        assert map.get_with(get_id).unwrap() == "a"
        ```
        """
        key = f()
        if key not in self:
            return option.NOTHING

        return option.Some(self._source[key])

    def get_pairs(self, key: K) -> Option[tuple[K, V]]:
        """Get both `key-value` pairs associated with `key`, returns `None` if not found.

        Example
        -------
        ```py
        users: HashMap[str, int] = HashMap()
        assert users.get_pairs("jack").is_none()

        users = HashMap({"jack": 0})
        assert users.get("jack").unwrap() == ("jack", 0)
        ```
        """
        if key not in self:
            return option.NOTHING

        return option.Some((key, self._source[key]))

    def get_many(self, *keys: K) -> Option[collections.Collection[V]]:
        """Attempts to get `len(keys)` values in the map at once.

        Returns a collection of length `keys` with the results of each query.
        None will be returned if any of the keys missing.

        The time complexity is `O(N)`, where `N` is the length of `keys`.

        Example
        -------
        ```py
        urls = HashMap({
            "google": "www.google.com",
            "github": "www.github.com",
            "facebook": "www.facebook.com",
            "twitter": "www.twitter.com",
        })
        assert urls.get_many("google","github").unwrap() == ["www.google.com", "www.github.com"]

        # missing keys results in `None`
        assert urls.get_many("google", "linkedin").is_none()
        # duplicate keys results in `None`
        assert urls.get_many("google", "google").is_none()
        ```
        """
        if not self._source:
            return option.NOTHING

        seen: set[K] = set()
        result: list[V] = []

        for key in keys:
            if key not in self._source or key in seen:
                return option.NOTHING

            seen.add(key)
            result.append(self._source[key])

        return option.Some(result)

    def iter(self) -> Iter[tuple[K, V]]:
        """Creates an iterator over the key-value pairs of the map.

        Example
        -------
        ```py
        map = HashMap.from_keys([
            ("a", 1),
            ("b", 2),
        ])
        for k, v in map.iter():
            print(f"{k=}: {v=}")
        ```
        """
        return Iter(self._source.items())

    def into_iter(self) -> IntoIterator[K, V]:
        """Creates a consuming iterator, that is, one that moves each key-value pair out of the map.
        The map cannot be used after calling this.

        Example
        -------
        ```py
        map = HashMap.from_keys([
            ("a", 1),
            ("b", 2),
            ("c", 3),
        ])
        for k, v in map.into_iter():
            print(f"{k=}: {v=}")
        ```
        """
        return IntoIterator(self.leak())

    def len(self) -> int:
        """Get how many elements are in this map.

        Example
        -------
        ```py
        map: HashMap[str, int] = HashMap()
        assert map.len() == 0
        ```
        """
        return len(self._source)

    # conversions

    def leak(self) -> collections.MutableMapping[K, V]:
        """Leaks and returns a mutable reference to the underlying map.

        `self` becomes unusable after calling this.

        Example
        -------
        ```py
        map = HashMap({0: 1})
        inner = map.leak()
        assert inner == {0: 1}
        ```
        """
        out = self._source
        del self._source
        return out

    # built-ins

    def copy(self) -> Self:
        """Copy the contents of this hash map into a new one.

        Example
        -------
        ```py
        hashmap: HashMap[str, None] = HashMap({'1': None, '2': None})
        copy = hashmap.copy()
        assert hashmap == copy
        ```
        """
        return self.__class__(self._source.copy())

    def __repr__(self) -> str:
        return self._source.__repr__()

    def __iter__(self) -> collections.Iterator[K]:
        return self._source.__iter__()

    def __len__(self) -> int:
        return self._source.__len__()

    def __getitem__(self, key: K, /) -> V:
        return self._source[key]

    def __setitem__(self, _key: Never, _value: Never) -> Never:
        raise NotImplementedError(
            "`HashMap` is immutable, use `.as_mut()` to make it mutable instead"
        )

    def __delitem__(self, _key: Never) -> Never:
        raise NotImplementedError(
            "`HashMap` is immutable, use `.as_mut()` to make it mutable instead"
        )


@rustc_diagnostic_item("HashMap")
class HashMap(_RawMap[K, V], Default["HashMap[K, V]"]):
    """An immutable key-value dictionary.

    But default, `HashMap` is immutable, it cannot change its values after initializing it. however,
    you can return a mutable reference to this hashmap via `HashMap.as_mut` method, it returns a reference to the underlying map.

    Example
    -------
    ```py
    # initialize it with a source. after that, item insertion is not allowed.
    books: HashMap[str, str] = HashMap({
        "Adventures of Huckleberry Finn": "My favorite book."
    })
    # get a mutable reference to it to be able to.
    books_mut = books.as_mut()
    # You can either call `.insert`, which is similar to Rust's.
    books_mut.insert(
        "Grimms Fairy Tales",
        "Masterpiece.",
    )
    # Or via item assignments
    books_mut["Pride and Prejudice"] = "Very enjoyable."
    print(books)

    for book, review in books.items():
        print(book, review)
    ```

    Parameters
    ----------
    source: `dict[K, V]`
        A dictionary to point to. this will be used as the underlying source.
    """

    __slots__ = ("_source",)

    def __init__(self, source: dict[K, V] | None = None, /) -> None:
        super().__init__(source)

    @staticmethod
    @override
    def default() -> HashMap[K, V]:
        """Creates an empty `HashMap<K, V>`."""
        return HashMap()

    @classmethod
    def from_mut(cls, source: dict[K, V] | None = None, /) -> RefMut[K, V]:
        """Create a new mutable `HashMap`, with the given source if available.

        Example
        -------
        ```py
        books = HashMap.from_mut()
        books[0] = "Twilight"
        ```
        """
        return RefMut(source or {})

    @staticmethod
    def from_keys_mut(*iterable: tuple[K, V]) -> RefMut[K, V]:
        """Create a new mutable `HashMap` from a sequence of key-value pairs.

        Example
        -------
        ```py
        tier_list = [
            ("S", "Top tier"),
            ("A", "Very Good"),
            ("B", "Good"),
            ("C", "Average"),
            ("D", "dodo")
        ]
        mapping: RefMut[str, str] = HashMap.from_keys_mut(*tier_list)
        ```
        """
        return RefMut({k: v for k, v in iterable})

    def as_mut(self) -> RefMut[K, V]:
        """Get a mutable reference to this hash map.

        Example
        -------
        ```py
        map: HashMap[str, float] = HashMap()

        # Get a reference to map
        mut = map.as_mut()
        mut.insert("sqrt", 1.0)
        del mut # not needed anymore

        assert map == {"sqrt": 1.0}
        ```
        """
        return RefMut(self._source)


@typing.final
class RefMut(_RawMap[K, V], collections.MutableMapping[K, V], Default["RefMut[K, V]"]):
    """A reference to a mutable dictionary / hashmap.

    Ideally, you want to use `HashMap.as_mut()` / `HashMap.from_mut` methods to create this.
    """

    __slots__ = ("_source",)

    def __init__(self, source: dict[K, V], /) -> None:
        super().__init__(source)
        self._source = source

    @staticmethod
    @override
    def default() -> RefMut[K, V]:
        """Creates a new, mutable, empty `RefMut<K, V>`."""
        return RefMut({})

    def insert(self, key: K, value: V) -> Option[V]:
        """Insert a key/value pair into the map.

        if `key` is not present in the map, `None` is returned. otherwise, the value is updated, and the old value
        is returned.

        Example
        -------
        ```py
        users = HashMap.from_mut({0: "admin"})
        assert users.insert(1, "admin").is_none()
        old = users.insert(0, "normal").unwrap()
        assert old == "admin"
        ```
        """
        if key not in self:
            self[key] = value
            return option.NOTHING

        old = self[key]
        self[key] = value
        return option.Some(old)

    def try_insert(self, key: K, value: V) -> Result[V, K]:
        """Tries to insert `key` and `value` into the map, returning `Err(key)` if `key` is already present.

        Example
        -------
        ```py
        users = HashMap.from_mut({0: "admin"})
        assert users.try_insert(1, "claudia").is_ok()
        assert users.try_insert(0, "doppler").is_err()
        ```
        """
        if key in self:
            return Err(key)

        self[key] = value
        return Ok(value)

    def remove(self, key: K) -> Option[V]:
        """Remove a key from the map, returning the value of the key if it was previously in the map.

        Example
        -------
        ```py
        map = HashMap.from_mut()
        map.insert(0, "a")
        map.remove(0).unwrap() == "a"
        map.remove(0).is_none()
        ```
        """
        if key not in self:
            return option.NOTHING

        v = self[key]
        del self[key]
        return option.Some(v)

    def remove_entry(self, key: K) -> Option[tuple[K, V]]:
        """Remove a key from the map, returning the key and value if it was previously in the map.

        Example
        -------
        ```py
        map = HashMap.from_mut()
        map[0] = "a"
        assert map.remove_entry(0).unwrap() == (0, "a")
        assert map.remove_entry(0).is_none()
        ```
        """
        if key not in self:
            return option.NOTHING

        v = self[key]
        del self[key]
        return option.Some((key, v))

    def retain(self, f: collections.Callable[[K, V], bool]) -> None:
        """Remove items from this map based on `f(key, value)` returning `False`.

        Example
        -------
        ```py
        users = HashMap.from_mut({
            "user1": "admin",
            "user2": "admin",
            "user3": "regular",
            "jack": "admin"
        })
        users.retain(
            lambda user, role: role == "admin" and
            user.startswith("user")
        )
        for user, role in users.items():
            print(user, role)

        # user1 admin
        # user2 admin
        """
        for k, v in self._source.copy().items():
            if not f(k, v):
                del self[k]

    def drain(self) -> Drain[K, V]:
        """Clears the map, returning all key-value pairs as an iterator. Keeps the hashmap for reuse.

        Example
        -------
        ```py
        map = HashMap.from_mut()
        map.insert(0, "a")
        map.drain().collect() == [(0, "a")]
        assert map.is_empty()
        ```
        """
        return Drain(self._source)

    def extract_if(self, pred: Fn[K, V]) -> ExtractIf[K, V]:
        """Creates an iterator which uses a closure to determine if an element should be removed.

        If the closure returns true, the element is removed from the map and yielded. If the closure returns false,
        the element remains in the map and will not be yielded.

        If you don't need at iterator, use `retain` instead.

        Example
        -------
        ```py
        odds = HashMap.from_mut({0: 0, 1: 1, 2: 2, 3: 3, 4: 4})
        evens = odds.extract_if(lambda k, _v: k % 2 == 0).collect()
        assert odds == {1: 1, 3: 3}
        assert evens == [(0, 0), (2, 2), (4, 4)]
        ```
        """
        return ExtractIf(self._source, pred)

    def __repr__(self) -> str:
        return self._source.__repr__()

    def __setitem__(self, key: K, value: V, /) -> None:
        self._source[key] = value

    def __delitem__(self, key: K, /) -> None:
        del self._source[key]

    def __iter__(self) -> collections.Iterator[K]:
        return self._source.__iter__()

    def __len__(self) -> int:
        return self._source.__len__()
