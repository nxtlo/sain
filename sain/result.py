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
"""Error handling with the `Result` type.

`Result[T, E]` is a drop-in replacement for exceptions `try/except`

where`Ok(T)` is the successful value and `Err(E)` is the error result.

```py
import enum

from sain import Result, Ok, Err

class FileError(enum.Enum):
    READ = enum.auto()
    WRITE = enum.auto()
    EMPTY = enum.auto()

def ready_lines(path: str) -> Result[list[str], FileError]:
    with open(path, 'r') as file:
        if (lines := file.readable()):
            if not lines:
                # File is readable but doesn't contain any lines.
                return Err(FileError.EMPTY)
            # File is not readable.
            return Err(FileError.READ)
        # Success.
        return Ok(file.readlines())
```

simple pattern matching in `Result` is a straightforward way to handle the returned value.

```py
match read_lines('quotes.txt'):
    # Ok(T) represents the success result which's `list[str]`.
    case Ok(lines):
        for line in lines:
            print(line)

    # Error represents the error contained value which's the enum `FileError`.
    case Err(reason):
        # Match the reason.
        match reason:
            case FileError.READ | FileError.WRITE:
                print("Can't read/write file.")
            case FileError.EMPTY:
                print("No lines in file.")
```

In addition to working with pattern matching, `Result` provides a
wide variety of different methods.

### Boolean checkers.
* `is_ok`: The contained value is derived from `Ok[T]`
* `is_err`: The contained value is derived from `Err[E]`

### Extracting contained values
These methods can be used to extract contained values if it was `Ok[T]`, raising `RuntimeError` if it was `Err[E]`.

- `expect`: Raises with a given message to the user.
- `unwrap`: Raises with an internal message provided by the library.
- `unwrap_or`: Returns with a default value.
- `unwrap_or_else`: Returns with a default function which returns a value.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ("Ok", "Err", "Result")

import typing

from sain import iter as _iter
from sain import option as _option

T = typing.TypeVar("T")
E = typing.TypeVar("E")

if typing.TYPE_CHECKING:
    import collections.abc as collections

    from typing_extensions import Never
    from typing_extensions import Self
    from typing_extensions import TypeAlias

    from sain import Option

    U = typing.TypeVar("U")
    F = collections.Callable[[T], U]


# Due to the nature of Python, Some methods here are repetitive to satisfy
# language and type checker, for an example `map` is only available for `Ok` but `Err` also needs to implement it
# which simply just returns self, same way goes around for `map_err`.
# Also for unwrapping values, `Err` guarantees an exception to be thrown but `Ok` doesn't.
@typing.final
@dataclass(weakref_slot=False, slots=True, frozen=True, repr=False)
class Ok(typing.Generic[T]):
    """Contains the success value of `Result[T, ...]`."""

    _inner: T

    ###############################
    # * Boolean operations. * #
    ###############################

    def is_ok(self) -> typing.Literal[True]:
        return True

    def is_ok_and(self, f: F[T, bool]) -> bool:
        return self.is_ok() and f(self._inner)

    # These are never truthy in an `Ok` instance.
    def is_err(self) -> typing.Literal[False]:
        return False

    def is_err_and(self, f: F[T, bool]) -> typing.Literal[False]:
        return False

    ###################
    # * Extractors. * #
    ###################

    @property
    def read(self) -> T:
        return self._inner

    def expect(self, message: str, /) -> T:
        return self._inner

    def unwrap(self) -> T:
        return self._inner

    def unwrap_or(self, default: T, /) -> T:
        return self._inner

    def unwrap_or_else(self, f: F[E, T]) -> T:
        return self._inner

    def unwrap_err(self) -> typing.NoReturn:
        raise RuntimeError(f"Called `unwrap_err` on an `Ok` variant: {self._inner!r}")

    ############################
    # * Conversion adapters. * #
    ############################

    def ok(self) -> Option[T]:
        return _option.Some(self._inner)

    def err(self) -> Option[None]:
        return _option.NOTHING

    def map(self, f: F[T, U], /) -> Ok[U]:
        return Ok(f(self._inner))

    def map_or(self, f: F[T, U], default: U, /) -> U:
        return f(self._inner)

    def map_or_else(self, f: F[T, U], default: F[E, U], /) -> U:
        return f(self._inner)

    def map_err(self, f: F[E, U], /) -> Self:
        return self

    ##############################
    # * Iterator constructors. * #
    ##############################

    def iter(self) -> _iter.Iter[T]:
        return self.__iter__()

    def __iter__(self) -> _iter.Iter[T]:
        return _iter.once(self._inner)

    def __repr__(self) -> str:
        return f"Ok({self._inner})"


@typing.final
@dataclass(weakref_slot=False, slots=True, frozen=True, repr=False)
class Err(typing.Generic[E]):
    """Contains the error value of `Result[..., E]`."""

    _inner: E

    ################################
    # * Boolean operations. * #
    ################################

    def is_ok(self) -> typing.Literal[False]:
        return False

    def is_ok_and(self, f: F[E, bool]) -> typing.Literal[False]:
        return False

    # These are never truthy in an `Ok` instance.
    def is_err(self) -> typing.Literal[True]:
        return True

    def is_err_and(self, f: F[E, bool]) -> bool:
        return self.is_err() and f(self._inner)

    ###################
    # * Extractors. * #
    ###################

    @property
    def read(self) -> E:
        return self._inner

    def expect(self, msg: str) -> typing.NoReturn:
        raise RuntimeError(msg) from None

    def expect_err(self) -> E:
        return self._inner

    def unwrap(self) -> typing.NoReturn:
        raise RuntimeError(
            f"Called `unwrap()` on an `Err` variant: {self._inner!r}"
        ) from None

    def unwrap_or(self, __default: T, /) -> T:
        return __default

    def unwrap_or_else(self, f: F[E, T]) -> T:
        return f(self._inner)

    def unwrap_err(self) -> E:
        return self._inner

    ############################
    # * Conversion adapters. * #
    ############################

    def ok(self) -> Option[None]:
        return _option.NOTHING

    def err(self) -> Option[E]:
        return _option.Some(self._inner)

    def map(self, f: F[E, U]) -> Self:
        return self

    def map_or(self, f: F[E, U], default: U, /) -> U:
        return default

    def map_or_else(self, f: F[T, U], default: F[E, U], /) -> U:
        return default(self._inner)

    def map_err(self, f: F[E, U]) -> Err[U]:
        return Err(f(self._inner))

    ##############################
    # * Iterator constructors. * #
    ##############################

    def iter(self) -> _iter.Iter[Never]:
        return self.__iter__()

    def __iter__(self) -> _iter.Iter[Never]:
        return _iter.empty()

    def __repr__(self) -> str:
        return f"Err({self._inner})"


Result: TypeAlias = Ok[T] | Err[E]
