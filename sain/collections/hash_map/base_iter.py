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
"""Iterator extensions for `HashMap` and `RefMut`."""

from __future__ import annotations

__all__ = ("IntoKeys", "IntoValues", "Drain", "ExtractIf", "IntoIterator", "Iter")

import collections.abc as collections
import typing

from sain.iter import ExactSizeIterator
from sain.iter import Iter
from sain.macros import override

K = typing.TypeVar("K")
V = typing.TypeVar("V")
Fn = collections.Callable[[K, V], bool]


@typing.final
class IntoKeys(ExactSizeIterator[K]):
    """An iterator that consumes the map and yields its keys.

    This is created by `HashMap.into_keys`.
    """

    __slots__ = ("_map", "_len")

    def __init__(self, view: collections.KeysView[K]) -> None:
        self._map = view.__iter__()
        self._len = len(view)

    @override
    def __next__(self) -> K:
        n = next(self._map)
        self._len -= 1
        return n

    @override
    def __len__(self) -> int:
        return self._len


@typing.final
class IntoValues(ExactSizeIterator[V]):
    """An iterator that consumes the map and yields its values.

    This is created by `HashMap.into_values`.
    """

    __slots__ = ("_map", "_len")

    def __init__(self, view: collections.ValuesView[V]) -> None:
        self._map = view.__iter__()
        self._len = len(view)

    @override
    def __next__(self) -> V:
        n = next(self._map)
        self._len -= 1
        return n

    @override
    def __len__(self) -> int:
        return self._len


@typing.final
class Drain(ExactSizeIterator[tuple[K, V]]):
    """A draining iterator over the entries of a hashmap.

    This iterator is created by the drain method on `RefMut.drain`. See its documentation for more.
    """

    __slots__ = ("_len", "_it")

    def __init__(self, raw: dict[K, V]) -> None:
        self._len = len(raw)
        self._it = iter(raw.copy().items())
        raw.clear()

    @override
    def __next__(self) -> tuple[K, V]:
        n = next(self._it)
        self._len -= 1
        return n

    @override
    def __len__(self) -> int:
        return self._len


@typing.final
class ExtractIf(ExactSizeIterator[tuple[K, V]]):
    """A draining, filtering iterator over the entries of a mutable `HashMap`.

    This is created by `RefMut.extract_if`.
    """

    __slots__ = ("_map", "_it", "_pred")

    def __init__(self, raw: dict[K, V], pred: Fn[K, V]) -> None:
        self._map = raw
        # we're not allowed to modify the map while iterating over it.
        # so we need to make a copy of the items.
        self._it = iter(raw.copy().items())
        self._pred = pred

    @override
    def __next__(self) -> tuple[K, V]:
        for k, v in self._it:
            if self._pred(k, v):
                del self._map[k]
                return k, v

        raise StopIteration

    @override
    def __len__(self) -> int:
        return len(self._map)


@typing.final
class IntoIterator(ExactSizeIterator[tuple[K, V]]):
    """An iterator that moves each key-value pair out of the map.

    This is created by `HashMap.into_iter`.
    """

    __slots__ = ("_it", "_len")

    def __init__(self, source: collections.Mapping[K, V]) -> None:
        self._it = iter(source.items())
        self._len = len(source)

    @override
    def __next__(self) -> tuple[K, V]:
        n = next(self._it)
        self._len -= 1
        return n

    @override
    def __len__(self) -> int:
        return self._len

    def __repr__(self) -> str:
        return f"IntoIterator({self._it})"
