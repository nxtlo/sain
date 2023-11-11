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

import typing_extensions as _typing_extensions

from . import default as _default
from . import ref as _ref

ValueT = _typing.TypeVar("ValueT")
T = _typing.TypeVar("T")
T_co = _typing.TypeVar("T_co", covariant=True)
Fn = _collections.Callable[[ValueT], T]
FnOnce = _collections.Callable[[], T]

Option: _typing_extensions.TypeAlias = "Some[ValueT]"
"""A Zero runtime cost type hint for a value that can be `Option<T>`.

Warning
-------
* This must be used as a type hint for a value that can be `Some<T>`
* You must import `__future__` annotations for this to work. at least for now.
* You must import this under `typing.TYPE_CHECKING`.

Example
-------
```py
from __future__ import annotations

import typing
from sain import Some

if typing.CHECKING:
    from sain import Option

foo: Option[str] = Some(None)
```
"""

class Some(_typing.Generic[ValueT], _default.Default[None]):
    def __init__(self, value: ValueT | None) -> None: ...
    @staticmethod
    def default() -> None: ...
    @property
    def read(self) -> ValueT | None: ...
    def unwrap(self, /) -> ValueT | _typing.NoReturn: ...
    def unwrap_or(self, default: ValueT) -> ValueT: ...
    def unwrap_or_else(self, f: FnOnce[ValueT]) -> ValueT: ...
    def unwrap_unchecked(self) -> ValueT: ...
    def map(self, f: Fn[ValueT, T]) -> Option[T]: ...
    def map_or(self, default: T, f: Fn[ValueT, T]) -> T: ...
    def map_or_else(self, default: FnOnce[T], f: Fn[ValueT, T]) -> T: ...
    def filter(self, predicate: Fn[ValueT, bool]) -> Option[ValueT]: ...
    def take(self) -> None: ...
    def replace(self, value: ValueT) -> Option[ValueT]: ...
    def expect(self, message: str) -> ValueT: ...
    def and_ok(self, optb: Option[T]) -> Option[T]: ...
    def and_then(self, f: Fn[ValueT, Option[T]]) -> Option[T]: ...
    def as_ref(self) -> Option[_ref.Ref[ValueT]]: ...
    def as_mut(self) -> Option[_ref.RefMut[ValueT]]: ...
    def is_some(self) -> bool: ...
    def is_some_and(self, predicate: Fn[ValueT, bool]) -> bool: ...
    def is_none(self) -> bool: ...
    def __bool__(self) -> bool: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
