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

`Result[T, E]` is a convenient replacement for exceptions `try/except`

where `Ok(T)` is the successful value and `Err(E)` is the error result.

A function returning a `Result` may be defined like this:
```py
from sain import Result, Ok, Err
from enum import Enum

class Version(Enum):
    VERSION_1 = 0x1
    VERSION_2 = 0x2

def parse_version(header: str) -> Result[Version, str]:
    match header.split('.')[0]:
        case '1':
            return Ok(Version.VERSION_1)
        case '2':
            return Ok(Version.VERSION_2)
        case _:
            return Err(f"Invalid version {header}")
```

simple pattern matching in `Result` is a straight-forward way to handle the returned value.

```py
version = parse_version("1.2.0")
match version:
    Ok(v): print(f"working with version {v}")
    Err(e): print(f"error parsing header {e}")
```

In addition to working with pattern matching, `Result` provides a
wide variety of different methods.

```py
# `unwrap_or` is used to return a default value in case of an `Err` variant returned.
good_result: Result[str, bool] = Ok("Name")
print(username.unwrap_or("default_name"))  # name

bad_result: Result[str, bool] = Err(False)
print(username.unwrap_or("default_name"))  # name
```

If you're expecting a value should never be an `Err` at runtime, use `.expect`
```py
def request(token: str) -> Result[bytes, None]:
    ...

response = request("token").expect("likely and invalid token")
# This will raise at runtime with the message 'likely ...'
```
"""

from __future__ import annotations

__all__ = ("Ok", "Err", "Result")

import dataclasses
import typing

from sain import iter as _iter
from sain import option as _option
from sain.macros import rustc_diagnostic_item

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
# ux and type checker, for an example `map` is only available for `Ok` but `Err` also needs to implement it
# which simply just returns self, same way goes around for `map_err`.
# Also for unwrapping values, `Err` guarantees an exception to be thrown but `Ok` doesn't.
@rustc_diagnostic_item("Ok")
@typing.final
@dataclasses.dataclass(slots=True, frozen=True, repr=False)
class Ok(typing.Generic[T]):
    """Contains the success value of `Result[T, ...]`."""

    _inner: T

    ###############################
    # * Querying operations. * #
    ###############################

    def is_ok(self) -> typing.Literal[True]:
        """Returns `True` if the contained value is `Ok` and `False` if it an `Err`.

        Example
        -------
        ```py
        value: Result[str, None] = Ok("value")
        assert value.is_ok() == True
        ```
        """
        return True

    def is_ok_and(self, f: F[T, bool]) -> bool:
        """Returns `True` if the contained value is `Ok` and `f()` returns True.

        Example
        -------
        ```py
        value: Result[str, None] = Ok("value")
        assert value.is_ok_and(lambda inner: inner == "value")
        # True
        ```
        """
        return f(self._inner)

    # These are never truthy in an `Ok` instance.
    def is_err(self) -> typing.Literal[False]:
        """Returns `True` if the contained value is `Err`.

        Example
        -------
        ```py
        value: Result[str, None] = Ok("value")

        assert value.is_err() == False
        ```
        """
        return False

    def is_err_and(self, f: F[T, bool]) -> typing.Literal[False]:
        """Returns `True` if the contained value is `Ok` and `f()` returns True.

        Example
        -------
        ```py
        value: Result[str, None] = Ok("value")

        assert value.is_err_and(lambda inner: inner == "value")
        # False
        ```
        """
        return False

    ###################
    # * Extractors * #
    ###################

    def expect(self, message: str, /) -> T:
        """Return the underlying value if it was `Ok`, Raising `RuntimeError`
        if it was `Err` with `message` passed to it.

        Example
        -------
        ```py
        ok: Result[str, None] = Ok("owo")
        ok.expect("err") # owo

        err: Result[str, None] = Err(None)
        err.expect("err") # RuntimeError("err")
        ```
        """
        return self._inner

    def expect_err(self) -> Never:
        """Return the `Err` value if `self` is an `Err`, panicking otherwise.

        Example
        -------
        ```py
        ok: Result[str, None] = Ok("owo")
        ok.expect_err()  # RuntimeError("Called expect_err on `Ok`)

        err: Result[str, None] = Err(None)
        err.expect_err() # None
        ```
        """
        raise RuntimeError("Called `expect_err` on an `Ok` value.")

    def unwrap(self) -> T:
        """Return the underlying value if it was `Ok`, Raising `RuntimeError` if it was `Err`.

        Example
        -------
        ```py
        ok: Result[str, None] = Ok("owo")
        ok.unwrap() # owo

        err: Result[str, None] = Err(None)
        err.unwrap() # RuntimeError
        ```
        """
        return self._inner

    def unwrap_or(self, default: T, /) -> T:
        """Return the underlying value if it was `Ok`, returning `default` if it was `Err`.

        Example
        -------
        ```py
        ok: Result[str, None] = Ok("OwO")
        ok.unwrap_or("uwu") # OwO

        err: Result[str, None] = Err(None)
        err.unwrap_or("uwu") # uwu
        ```
        """
        return self._inner

    def unwrap_or_else(self, f: F[E, T]) -> T:
        """Return the contained `Ok` value or computes it from `f()` if it was `Err`.

        Example
        -------
        ```py
        ok: Result[int, str] = Ok(4)
        ok.unwrap_or_else(lambda e: 0) # 4

        err: Result[int, str] = Err("word")
        err.unwrap_or_else(lambda e: len(e)) # 4
        ```
        """
        return self._inner

    def unwrap_err(self) -> Never:
        """Return the contained `Err` value, Raising if it was `Ok`.

        Example
        -------
        ```py
        ok: Result[str, None] = Ok("buh")
        ok.unwrap_err()  # RuntimeError

        err: Result[str, None] = Err(None)
        err.unwrap_err() == None
        # True
        ```
        """
        raise RuntimeError(f"Called `unwrap_err` on an `Ok` variant: {self._inner!r}")

    ############################
    # * Conversion adapters. * #
    ############################

    def ok(self) -> Option[T]:
        """Transform `Result[T, E]` to `Option[T]`, mapping `Ok(v)` to `Some(T)` and `Err(e)` to `None`.

        Example
        -------
        ```py
        value: Result[str, None] = Ok("buh")
        value.ok().is_some() # True

        value: Result[str, int] = Err(0)
        value.ok().is_none() # True
        ```
        """
        return _option.Some(self._inner)

    def err(self) -> Option[T]:
        """Transform `Result[T, E]` to `Option[E]`, mapping `Ok(v)` to `None` and `Err(e)` to `Some(e)`.

        Example
        -------
        ```py
        value: Result[str, None] = Ok("buh")
        value.err().is_none() # True

        value: Result[str, int] = Err(0)
        value.err().is_some() # True
        ```
        """
        return _option.NOTHING

    def inspect(self, f: F[T, typing.Any]) -> Self:
        """Call a function to the contained value if it was `Ok` and do nothing if it was `Err`

        Example
        -------
        ```py
        def sink(value: str) -> None:
            # do something with value
            print("Called " + value)

        x: Result[str, None] = Ok("ok")
        x.inspect(sink) # "Called ok"

        x: Result[str, str] = Err("err")
        x.inspect(sink) # None
        ```
        """
        f(self._inner)
        return self

    def inspect_err(self, f: F[E, typing.Any]) -> Self:
        """Call a function to the contained value if it was `Err` and do nothing if it was `Ok`

        Example
        -------
        ```py
        def sink(value: str) -> None:
            # do something with value
            print("Called " + value)

        x: Result[str, None] = Ok("ok")
        x.inspect_err(sink) # None

        x: Result[str, str] = Err("err")
        x.inspect_err(sink) # Called err
        ```
        """
        return self

    def map(self, f: F[T, U], /) -> Ok[U]:
        """Map `Result<T, E>` to `Result<U, E>` by applying a function to the `Ok` value,
        leaving `Err` untouched.

        Example
        -------
        ```py
        ok: Result[str, int] = Ok("1")
        ok.map(lambda c: int(c) + 1) # Ok(2)

        err: Result[str, int] = Err(0)
        err.map(str.upper) # Err(0)
        ```
        """
        return Ok(f(self._inner))

    def map_or(self, f: F[T, U], default: U, /) -> U:
        """Returns the provided `default` if the contained value is `Err`,

        Otherwise extracts the `Ok` value and maps it to `f()`

        Example
        -------
        ```py
        x: Result[str, str] = Ok("foo")
        assert x.map_or(lambda c: len(c), 42) == 3

        x: Result[str, str] = Err("bar")
        assert x.map_or(lambda c: len(c), 42) == 42
        ```
        """
        return f(self._inner)

    def map_or_else(self, f: F[T, U], default: F[E, U], /) -> U:
        """Maps a Result<T, E> to U by applying fallback function `default` to a contained Err value,
        or function `f` to a contained Ok value.

        Example
        -------
        ```py
        x: Result[str, str] = Ok("four")
        assert x.map_or_else(
            lambda ok: 2 * len(ok),
            default=lambda err: len(err)
        ) == 8

        x: Result[str, str] = Err("bar")
        assert x.map_or_else(
            lambda c: 2 * len(c),
            lambda err: len(err)
        ) == 3
        ```
        """
        return f(self._inner)

    def map_err(self, f: F[E, U], /) -> Self:
        """Maps a `Result[T, E]` to `Result[T, U]` by applying function `f`, leaving the `Ok` value untouched.

        Example
        -------
        ```py
        x: Result[str, int] = Ok("blue")
        x.map_err(lambda err: err + 1) # Ok("blue")

        x: Result[str, int] = Err(5)
        x.map_err(float) # Err(5.0)
        ```
        """
        return self

    ##############################
    # * Iterator constructors. * #
    ##############################

    def iter(self) -> _iter.ExactSizeIterator[T]:
        """An iterator over the possible contained value.

        If `self` was `Ok`, then the iterator will yield the Ok `T`. otherwise yields nothing.

        Example
        -------
        ```py
        c: Result[str, int] = Ok("blue")
        c.iter().next() == Some("blue")

        c: Result[str, int] = Err(0)
        c.iter().next() == Some(None)
        ```
        """
        return _iter.Once(self._inner)

    def __iter__(self) -> collections.Iterator[T]:
        yield self._inner

    #################
    # * Overloads * #
    #################

    def __repr__(self) -> str:
        return f"Ok({self._inner!r})"

    def __or__(self, other: T) -> T:
        return self._inner

    def __invert__(self) -> T:
        return self._inner


@rustc_diagnostic_item("Err")
@typing.final
@dataclasses.dataclass(slots=True, frozen=True, repr=False)
class Err(typing.Generic[E]):
    """Contains the error value of `Result[..., E]`."""

    _inner: E

    ################################
    # * Boolean operations. * #
    ################################

    def is_ok(self) -> typing.Literal[False]:
        """Returns `True` if the contained value is `Ok` and `False` if it an `Err`.

        Example
        -------
        ```py
        value: Result[str, None] = Err(None)

        assert value.is_ok() == False
        ```
        """
        return False

    def is_ok_and(self, f: F[E, bool]) -> typing.Literal[False]:
        """Returns `True` if the contained value is `Ok` and `f()` returns True.

        Example
        -------
        ```py
        value: Result[str, None] = Err(None)

        assert value.is_ok_and(lambda inner: inner == "value")
        # False
        ```
        """
        return False

    # These are never truthy in an `Ok` instance.
    def is_err(self) -> typing.Literal[True]:
        """Returns `True` if the contained value is `Err`.

        Example
        -------
        ```py
        value: Result[str, None] = Err(None)

        assert value.is_err() == True
        ```
        """
        return True

    def is_err_and(self, f: F[E, bool]) -> bool:
        """Returns `True` if the contained value is `Ok` and `f()` returns True..

        Example
        -------
        ```py
        value: Result[str, None] = Err(None)

        assert value.is_err_and(lambda err: err is None)
        # True
        ```
        """
        return f(self._inner)

    ###################
    # * Extractors. * #
    ###################

    def expect(self, msg: str) -> Never:
        """Return the underlying value if it was `Ok`, Raising `RuntimeError`
        if it was `Err` with `message` passed to it.

        Example
        -------
        ```py
        ok: Result[str, None] = Ok("owo")
        ok.expect("err") # owo

        err: Result[str, None] = Err(None)
        err.expect("err") # RuntimeError("err")
        ```
        """
        raise RuntimeError(msg) from None

    def expect_err(self) -> E:
        """Return the `Err` if it was `Err`, panicking otherwise.


        Example
        -------
        ```py
        x: Result[str, None] = Ok("owo")
        x.expect_err()  # RuntimeError("Called expect_err on `Ok`)

        x: Result[str, None] = Err(None)
        x.expect_err() # None
        ```
        """
        return self._inner

    def unwrap(self) -> Never:
        """Return the underlying value if it was `Ok`, Raising `RuntimeError` if it was `Err`.

        Example
        -------
        ```py
        ok: Result[str, None] = Ok("owo")
        ok.unwrap() # owo

        err: Result[str, None] = Err(None)
        err.unwrap() # RuntimeError
        ```
        """
        raise RuntimeError(
            f"Called `unwrap()` on an `Err` variant: {self._inner!r}"
        ) from None

    def unwrap_or(self, default: T, /) -> T:
        """Return the underlying value if it was `Ok`, returning `default` if it was `Err`.

        Example
        -------
        ```py
        ok: Result[str, None] = Ok("OwO")
        ok.unwrap_or("uwu") # OwO

        err: Result[str, None] = Err(None)
        err.unwrap_or("uwu") # uwu
        ```
        """
        return default

    def unwrap_or_else(self, f: F[E, T]) -> T:
        """Return the contained `Ok` value or computes it from `f()` if it was `Err`.

        Example
        -------
        ```py
        ok: Result[int, str] = Ok(4)
        ok.unwrap_or_else(lambda e: 0) # 4

        err: Result[int, str] = Err("word")
        err.unwrap_or_else(lambda e: len(e)) # 4
        ```
        """
        return f(self._inner)

    def unwrap_err(self) -> E:
        """Return the contained `Err` value, Raising if it was `Ok`.

        Example
        -------
        ```py
        ok: Result[str, None] = Ok("buh")
        ok.unwrap_err()  # RuntimeError

        err: Result[str, None] = Err(None)
        err.unwrap_err() == None
        # True
        ```
        """
        return self._inner

    ############################
    # * Conversion adapters. * #
    ############################

    def inspect(self, f: F[T, typing.Any]) -> Self:
        """Call a function to the contained value if it was `Ok` and do nothing if it was `Err`

        Example
        -------
        ```py
        def sink(value: str) -> None:
            # do something with value
            print("Called " + value)

        x: Result[str, None] = Ok("ok")
        x.inspect(sink) # "Called ok"

        x: Result[str, str] = Err("err")
        x.inspect(sink) # None
        ```
        """
        return self

    def inspect_err(self, f: F[E, typing.Any]) -> Self:
        """Call a function to the contained value if it was `Err` and do nothing if it was `Ok`

        Example
        -------
        ```py
        def sink(value: str) -> None:
            # do something with value
            print("Called " + value)

        x: Result[str, None] = Ok("ok")
        x.inspect_err(sink) # None

        x: Result[str, str] = Err("err")
        x.inspect_err(sink) # Called err
        ```
        """
        f(self._inner)
        return self

    def ok(self) -> Option[None]:
        """Transform `Result[T, E]` to `Option[T]`, mapping `Ok(v)` to `Some(T)` and `Err(e)` to `None`.

        Example
        -------
        ```py
        value: Result[str, None] = Ok("buh")
        value.ok().is_some() # True

        value: Result[str, int] = Err(0)
        value.ok().is_none() # True
        ```
        """
        return _option.NOTHING

    def err(self) -> Option[E]:
        """Transform `Result[T, E]` to `Option[E]`, mapping `Ok(v)` to `None` and `Err(e)` to `Some(e)`.

        Example
        -------
        ```py
        value: Result[str, None] = Ok("buh")
        value.err().is_none() # True

        value: Result[str, int] = Err(0)
        value.err().is_some() # True
        ```
        """
        return _option.Some(self._inner)

    def map(self, f: F[E, U]) -> Self:
        """Map `Result<T, E>` to `Result<U, E>` by applying a function to the `Ok` value,
        leaving `Err` untouched.

        Example
        -------
        ```py
        ok: Result[str, int] = Ok("1")
        ok.map(lambda c: int(c) + 1) # Ok(2)

        err: Result[str, int] = Err(0)
        err.map(str.upper) # Err(0)
        ```
        """
        return self

    def map_or(self, f: F[E, U], default: U, /) -> U:
        """Returns the provided `default` if the contained value is `Err`,

        Otherwise extracts the `Ok` value and maps it to `f()`

        Example
        -------
        ```py
        x: Result[str, str] = Ok("foo")
        assert x.map_or(lambda c: len(c), 42) == 3

        x: Result[str, str] = Err("bar")
        assert x.map_or(lambda c: len(c), 42) == 42
        ```
        """
        return default

    def map_or_else(self, f: F[T, U], default: F[E, U], /) -> U:
        """Maps a Result<T, E> to U by applying fallback function `default` to a contained Err value,
        or function `f` to a contained Ok value.

        Example
        -------
        ```py
        x: Result[str, str] = Ok("four")
        assert x.map_or_else(
            lambda ok: 2 * len(ok),
            default=lambda err: len(err)
        ) == 8

        x: Result[str, str] = Err("bar")
        assert x.map_or_else(
            lambda c: 2 * len(c),
            lambda err: len(err)
        ) == 3
        ```
        """
        return default(self._inner)

    def map_err(self, f: F[E, U]) -> Err[U]:
        """Maps a `Result[T, E]` to `Result[T, U]` by applying function `f`, leaving the `Ok` value untouched.

        Example
        -------
        ```py
        x: Result[str, int] = Ok("blue")
        x.map_err(lambda err: err + 1) # Ok("blue")

        x: Result[str, int] = Err(5)
        x.map_err(float) # Err(5.0)
        ```
        """
        return Err(f(self._inner))

    ##############################
    # * Iterator constructors. * #
    ##############################

    def iter(self) -> _iter.ExactSizeIterator[E]:
        """An iterator over the possible contained value.

        If `self` was `Ok`, then the iterator will yield `T`, otherwise yields nothing.

        Example
        -------
        ```py
        c: Result[str, int] = Ok("blue")
        c.iter().next() == Some("blue")

        c: Result[str, int] = Err(0)
        c.iter().next() == Some(None)
        ```
        """
        return _iter.Empty()

    def __iter__(self) -> collections.Iterator[E]:
        yield from ()

    #################
    # * Overloads * #
    #################

    def __repr__(self) -> str:
        return f"Err({self._inner!r})"

    def __or__(self, other: T) -> T:
        return other

    def __invert__(self) -> Never:
        self.unwrap()


Result: TypeAlias = "Ok[T] | Err[E]"
"""A type hint for a function that may return `Ok[T]` or `Err[E]`,

See the module documentation level for more information."""
