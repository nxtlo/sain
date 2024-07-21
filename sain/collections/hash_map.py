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

import typing
import collections.abc as collections

from sain import option as _option
from sain import iter as _iter

K = typing.TypeVar("K")
V = typing.TypeVar("V")
T = typing.TypeVar("T")

if typing.TYPE_CHECKING:
    from typing_extensions import Never
    from typing_extensions import Self
    from sain.option import Option


class _RawMap(collections.Mapping[K, V]):
    __slots__ = ("_source",)

    def __init__(self, source: dict[K, V] | None = None, /) -> None:
        self._source = source if source else {}

    # constructors

    @classmethod
    def from_keys(cls, *iterable: tuple[K, V]) -> Self:
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
        return cls({k: v for k, v in iterable})

    # default impls

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

    def get(self, key: K) -> Option[V]:
        """Get the value associated with `key`, returns `None` if not found.

        Unlike `dict.get` which returns builtin `None`, This returns `Option[T]`.

        Example
        -------
        ```py
        users: HashMap[str, int] = HashMap()
        assert null.get("jack").is_none()

        null = HashMap({"jack": None})
        assert null.get("jack").is_some()
        ```
        """
        if key not in self:
            return _option.nothing_unchecked()

        return _option.Some(self._source[key])

    def iter(self) -> _iter.Iterator[tuple[K, V]]:
        """An iterator visiting all key-value pairs in arbitrary order.

        This returns `sain.Iterator` and not a normal iterator.

        Example
        -------
        ```py
        map: HashMap[str, int] = HashMap({
            "a": 1,
            "b": 2,
            "c": 3,
        })
        for k, v in map.iter():
            print(f"{k=}: {v=}")
        """
        return _iter.Iter(self.items())

    def len(self) -> int:
        """Get how many elements are in this map.

        Example
        -------
        ```py
        map: HashMap[str, int] = HashMap()
        assert map.len() == 0
        ```
        """
        return self.__len__()

    # conversions

    def leak(self) -> collections.MutableMapping[K, V]:
        """Leaks and returns an owned mutable mapping of the underlying source.

        Example
        -------
        ```py
        map = HashMap({0: 1})
        inner = map.leak()
        assert inner == {0: 1}
        ```
        """
        return self._source

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

    def __setitem__(self, _key: Never, _value: Never) -> typing.NoReturn:
        raise NotImplementedError(
            "`HashMap` is immutable, use `.as_mut()` to make it mutable instead"
        )

    def __delitem__(self, _key: Never) -> typing.NoReturn:
        raise NotImplementedError(
            "`HashMap` is immutable, use `.as_mut()` to make it mutable instead"
        )


class HashMap(_RawMap[K, V]):
    """An immutable key-value dictionary.

    But default, it is immutable it cannot change its values after initializing it. however,
    you can return a mutable reference to this hashmap via `HashMap.as_mut` method, it doesn't return copy.

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

    @classmethod
    def new_mut(cls, source: dict[K, V] | None = None, /) -> RefMut[K, V]:
        """Create a new mutable `HashMap`, with the given source if available.

        Example
        -------
        ```py
        books = HashMap.new_mut()
        books[0] = "Twilight"
        ```
        """
        return RefMut(source or {})

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
class RefMut(typing.Generic[K, V], _RawMap[K, V], collections.MutableMapping[K, V]):
    """A reference to a mutable dictionary / hashmap.

    This is built from the `HashMap.as_mut()` method.
    """

    if typing.TYPE_CHECKING:
        _source: dict[K, V]

    __slots__ = ("_source",)

    def __init__(self, source: dict[K, V], /) -> None:
        super().__init__(source)

    def insert(self, key: K, value: V) -> _option.Option[V]:
        """Insert a key/value pair into the map.

        if the map doesn't already `key` present, `None` is returned.

        if `key` is already present in the map, the value is updated, and the old value
        is returned.

        Example
        -------
        ```py
        users = HashMap.new_mut({0: "admin"})
        assert users.insert(1, "admin").is_none()
        old = users.insert(0, "normal").unwrap()
        assert old == "admin"
        ```
        """
        if key not in self:
            self[key] = value
            return _option.nothing_unchecked()

        old = self[key]
        self[key] = value
        return _option.Some(old)

    def remove(self, key: K) -> Option[V]:
        """Remove a key from the map, returning the value of the key if it was previously in the map.

        Example
        -------
        ```py
        map = HashMap.new_mut()
        map.insert(0, "a")
        map.remove(0).unwrap() == "a"
        map.remove(0).is_none()
        ```
        """
        if key not in self:
            return _option.nothing_unchecked()

        v = self[key]
        del self[key]
        return _option.Some(v)

    def remove_entry(self, key: K) -> Option[tuple[K, V]]:
        """Remove a key from the map, returning the key and value if it was previously in the map.

        Example
        -------
        ```py
        map = HashMap.new_mut()
        map.insert(0, "a")
        map.remove(0).unwrap() == "a"
        map.remove(0).is_none()
        ```
        """
        if key not in self:
            return _option.nothing_unchecked()

        v = self[key]
        del self[key]
        return _option.Some((key, v))

    def retain(self, f: collections.Callable[[K, V], bool]) -> None:
        """Remove items from this map based on `f(key, value)` returning `False`.

        Example
        -------
        ```py
        users = HashMap.new_mut({
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

    def __repr__(self) -> str:
        return self._source.__repr__()

    def __setitem__(self, key: K, value: V, /) -> None:
        self._source[key] = value

    def __getitem__(self, key: K, /) -> V:
        return self._source[key]

    def __delitem__(self, key: K, /) -> None:
        del self._source[key]

    def __iter__(self) -> collections.Iterator[K]:
        return self._source.__iter__()

    def __len__(self) -> int:
        return self._source.__len__()
