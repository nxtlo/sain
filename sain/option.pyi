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
from __future__ import annotations

import collections.abc as _collections
import typing as _typing

from . import Iter
from . import default as _default
from .result import Result

type Fn[T, U] = _collections.Callable[[T], U]
type FnOnce[T] = _collections.Callable[[], T]
type Option[T] = Some[T]
NOTHING: Option[None]

def nothing_unchecked[T]() -> Option[T]: ...
@_typing.final
class Some[T](_default.Default[Option[None]]):
    __match_args__: tuple[_typing.Literal["_inner"]]
    def __init__(self, value: T | None, /) -> None: ...
    @staticmethod
    def default() -> Option[None]: ...
    def transpose(self) -> T | None: ...
    def unwrap(self, /) -> T | _typing.NoReturn: ...
    def unwrap_or(self, default: T) -> T: ...
    def unwrap_or_else(self, f: FnOnce[T]) -> T: ...
    def unwrap_unchecked(self) -> T: ...
    def map[U](self, f: Fn[T, U]) -> Option[U]: ...
    def map_or[U](self, default: U, f: Fn[T, U]) -> U: ...
    def map_or_else[U](self, default: FnOnce[U], f: Fn[T, U]) -> U: ...
    def filter(self, predicate: Fn[T, bool]) -> Option[T]: ...
    def take(self) -> Option[T]: ...
    def take_if(self, predicate: Fn[T, bool]) -> Option[T]: ...
    def replace(self, value: T) -> Option[T]: ...
    def insert(self, value: T) -> T: ...
    def get_or_insert(self, value: T) -> T: ...
    def get_or_insert_with(self, f: FnOnce[T]) -> T: ...
    def zip[U](self, other: Option[U]) -> Option[tuple[T, U]]: ...
    def zip_with[U, R](
        self, other: Option[U], f: _collections.Callable[[T, U], R]
    ) -> Option[R]: ...
    def expect(self, message: str) -> T: ...
    def and_ok[U](self, optb: Option[T]) -> Option[U]: ...
    def and_then[U](self, f: Fn[T, Option[U]]) -> Option[U]: ...
    def inspect(self, f: Fn[T, _typing.Any]) -> Option[T]: ...
    def ok_or_else[E](self, err: FnOnce[E]) -> Result[T, E]: ...
    def ok_or[E](self, err: E) -> Result[T, E]: ...
    def is_some(self) -> bool: ...
    def is_some_and(self, predicate: Fn[T, bool]) -> bool: ...
    def is_none(self) -> bool: ...
    def iter(self) -> Iter[T]: ...
    def __bool__(self) -> bool: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __invert__(self) -> T: ...
    def __or__(self, other: T) -> T: ...
