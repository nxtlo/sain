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
"""Rust's `Option<T>` type. A value that can either be `T` or `None`"""

from __future__ import annotations

__all__ = ("Some", "Option", "NOTHING")

import typing

from . import default as _default
from . import iter as _iter
from . import macros
from . import result as _result

T = typing.TypeVar("T")
T_co = typing.TypeVar("T_co", covariant=True)

if typing.TYPE_CHECKING:
    import collections.abc as collections

    U = typing.TypeVar("U")
    Fn = collections.Callable[[T], U]
    FnOnce = collections.Callable[[], U]


@typing.final
class Some(typing.Generic[T], _default.Default["Option[None]"]):
    """The `Option` type. An object that might be `T` or `None`.

    It is a drop-in replacement for `typing.Optional[T]`, But has proper methods to handle the contained value.

    Example
    -------
    ```py
    value = Some("Hello")
    print(value)
    # Some("Hello")

    # This will unwrap the contained value as long as
    # it is not `None` otherwise this will raise an error.
    print(value.unwrap())
    # "Hello"

    none_value = Some(None)
    while none_value.unwrap():
        # Never unreachable!

    # Solving it with `unwrap_or` method to unwrap the value or return a default value.
    print(none_value.unwrap_or(10))
    # 10
    ```
    """

    __slots__ = ("_value",)
    __match_args__ = ("_value",)

    def __init__(self, value: T | None, /) -> None:
        self._value = value

    @staticmethod
    def default() -> Option[None]:
        """Default value for `Some`. Returns `None` wrapped in `Some`.

        Example
        -------
        ```py
        assert Some.default() == NOTHING
        ```
        """
        return NOTHING

    # *- Reading the value -*

    def transpose(self) -> T | None:
        """Convert `Option[T]` into `T | None`.

        Examples
        --------
        ```py
        opt = Some('char')
        x = opt.transpose()
        assert x == 'char'

        opt = Some(None)
        assert opt.transpose() is None
        ```
        """
        return self._value

    def unwrap(self) -> T:
        """Unwrap the inner value either returning if its not `None` or raising a `RuntimeError`.

        It's usually not recommended to use this method in production code, since it raises.

        Example
        -------
        ```py
        value = Some(5)
        print(value.unwrap())
        # 5

        value = Some(None)
        print(value.unwrap())
        # RuntimeError
        ```

        Raises
        ------
        `RuntimeError`
            If the inner value is `None`.
        """
        if self._value is None:
            raise RuntimeError("Called `Option.unwrap()` on `None`.") from None

        return self._value

    def unwrap_or(self, default: T, /) -> T:
        """Unwrap the inner value either returning if its not `None` or returning `default`.

        Example
        -------
        ```py
        value = Some(5)
        print(value.unwrap_or(10))
        # 5

        # Type hint is required here.
        value: Option[int] = Some(None)
        print(value.unwrap_or(10))
        # 10
        ```
        """
        if self._value is None:
            return default

        return self._value

    def unwrap_or_else(self, f: FnOnce[T], /) -> T:
        """Unwrap the inner value either returning if its not `None` or calling `f` to get a default value.

        Example
        -------
        ```py
        value = Some(5)
        print(value.unwrap_or_else(lambda: 10))
        # 5

        value: Option[bool] = Some(None)
        print(value.unwrap_or_else(lambda: True))
        # True
        ```
        """
        if self._value is None:
            return f()

        return self._value

    @macros.unsafe
    def unwrap_unchecked(self) -> T:
        """Returns the contained Some value without checking that the value is not None.

        Example
        -------
        ```py
        v: Option[float] = Some(1.2)
        v.unwrap_unchecked() # 1.2

        v: Option[float] = Some(None)
        print(v.unwrap_unchecked()) # Undefined Behavior
        ```
        """
        #! SAFETY: The caller guarantees that the value is not None.
        return self._value  # pyright: ignore

    def expect(self, message: str, /) -> T:
        """Returns the contained value if it is not `None` otherwise raises a `RuntimeError`.

        Example
        -------
        ```py
        value = Some("Hello")

        print(value.expect("Value is None"))
        # "Hello"

        value: Option[str] = Some(None)
        print(value.expect("Value is None"))
        # RuntimeError("Value is None")
        ```
        """
        if self._value is None:
            raise RuntimeError(message)

        return self._value

    # *- object transformation -*

    def map(self, f: Fn[T, U], /) -> Option[U]:
        """Map the inner value to another type. Returning `Some(None)` if `T` is `None`.

        Example
        -------
        ```py
        value = Some(5.0)

        print(value.map(lambda x: x * 2.0))
        # Some(10.0)

        value: Option[bool] = Some(None)
        print(value)
        # Some(None)
        ```
        """
        if self._value is None:
            return NOTHING  # pyright: ignore

        return Some(f(self._value))

    def map_or(self, default: U, f: Fn[T, U], /) -> U:
        """Map the inner value to another type or return `default` if its `None`.

        Example
        -------
        ```py
        value: Option[float] = Some(5.0)

        # map to int.
        print(value.map_or(0, int))
        # 6

        value: Option[float] = Some(None)
        print(value.map_or(0, int)
        # 0
        ```
        """
        if self._value is None:
            return default

        return f(self._value)

    def map_or_else(self, default: FnOnce[U], f: Fn[T, U], /) -> U:
        """Map the inner value to another type, or return `default()` if its `None`.

        Example
        -------
        ```py
        def default() -> int:
            return sys.getsizeof(object())

        value: Option[float] = Some(5.0)

        # map to int.
        print(value.map_or_else(default, int))
        # 6

        value: Option[float] = Some(None)
        print(value.map_or_else(default, int)
        # 28 <- size of object()
        ```
        """
        if self._value is None:
            return default()

        return f(self._value)

    def filter(self, predicate: Fn[T, bool]) -> Option[T]:
        """Returns `Some(None)` if the contained value is `None`,

        otherwise calls the predicate and returns `Some(T)` if the predicate returns `True`.

        Example
        -------
        ```py
        value = Some([1, 2, 3])

        print(value.filter(lambda x: 1 in x))
        # Some([1, 2, 3])

        value: Option[int] = Some([1, 2, 3]) # or Some(None)
        print(value.filter(lambda x: 1 not in x))
        # None
        ```
        """
        if (value := self._value) is not None:
            if predicate(value):
                return Some(value)

        return NOTHING  # pyright: ignore

    def ok_or(self, err: U) -> _result.Result[T, U]:
        """Transforms the `Option<T>` into a `Result<T, E>`, mapping `Some(v)` to `Ok(v)` and `None` to `Err(err)`.

        Example
        -------
        ```py
        xyz: Option[str] = Some("foo")
        assert xyz.ok_or(None) == Ok("foo")

        xyz: Option[str] = Some(None)
        assert xyz.ok_or(None) == Err(None)
        ```
        """
        if self._value is None:
            return _result.Err(err)

        return _result.Ok(self._value)

    def ok_or_else(self, err: FnOnce[U]) -> _result.Result[T, U]:
        """Transforms the `Option<T>` into a `Result<T, E>`, mapping `Some(v)` to `Ok(v)` and `None` to `Err(err())`.

        Example
        -------
        ```py
        xyz: Option[str] = Some("foo")
        assert xyz.ok_or(None) == Ok("foo")

        xyz: Option[str] = Some(None)
        assert xyz.ok_or(None) == Err(None)
        ```
        """
        if self._value is None:
            return _result.Err(err())

        return _result.Ok(self._value)

    def zip(self, other: Option[U]) -> Option[tuple[T, U]]:
        """Zips `self` with `other`.

        if `self` is `Some(s)` and other is `Some(o)`, this returns `Some((s, o))` otherwise `None`.

        Example
        -------
        ```py
        x = Some(1)
        y = Some("hi")
        z: Option[str] = Some(None)

        assert x.zip(y) == Some((1, "hi"))
        assert x.zip(z) == Some(None)
        ```
        """
        if self._value is not None and other._value is not None:
            return Some((self._value, other._value))

        return NOTHING  # type: ignore

    def zip_with(
        self, other: Option[U], f: collections.Callable[[T, U], T_co]
    ) -> Option[T_co]:
        """Zips `self` with `other` using function `f`.

        if `self` is `Some(s)` and other is `Some(o)`, this returns `Some(f(s, o))` otherwise `None`.

        Example
        -------
        ```py
        @dataclass
        class Point:
            x: float
            y: float

        x, t = Some(32.1), Some(42.4)
        assert x.zip_with(t, Point) == Some(Point(32.1, 42.4))
        ```
        """
        if self._value is not None and other._value is not None:
            return Some(f(self._value, other._value))

        return NOTHING  # type: ignore

    # *- Inner operations *-

    def take(self) -> Option[T]:
        """Take the value from `Self`, Setting it to `None`.

        Example
        -------
        ```py
        original = Some("Hi")
        new = original.take()

        print(original, new)
        # None, Some("Hi")
        ```
        """
        if self._value is None:
            return NOTHING  # pyright: ignore

        val = self._value
        self._value = None
        return Some(val)

    def take_if(self, predicate: collections.Callable[[T], bool]) -> Option[T]:
        """Take the value from `Self`, Setting it to `None` only if predicate returns `True`.

        Example
        -------
        ```py
        def validate(email: str) -> bool:
            # you can obviously validate this better.
            return email.find('@') == 1

        original = Some("flex@gg.com")
        valid = original.take_if(validate)
        assert is_allowed.is_some() and original.is_none()

        original = Some("mail.example.com")
        invalid = original.take_if(validate)
        assert invalid.is_none() and original.is_some()
        ```
        """
        if self.map_or(False, predicate):
            return self.take()

        return NOTHING  # pyright: ignore

    def replace(self, value: T) -> Option[T]:
        """Replace the contained value with another value.

        Use `Option.insert` if you want to return the original value
        that got inserted instead of `self`

        Example
        -------
        ```py
        value: Option[str] = Some(None)
        value.replace("Hello")
        # Some("Hello")
        ```
        """
        self._value = value
        return self

    def insert(self, value: T) -> T:
        """Insert a value into the option, and then return a reference to it.

        This will overwrite the old value if it was already contained.

        Example
        -------
        ```py
        flag: Option[bool] = Some(None)
        flag_ref = flag.insert(True)
        assert flag_ref == True
        assert flag.unwrap() == True
        ```
        """
        self._value = value
        return value

    def get_or_insert(self, value: T) -> T:
        """Insert a value into the option if it was `None`,
        and then return a reference to it.

        Example
        -------
        ```py
        state: Option[bool] = Some(None)
        assert state.get_or_insert(True) is True
        assert state.get_or_insert(False) is True
        ```
        """
        if self._value is not None:
            return self._value

        self._value = value
        return value

    def get_or_insert_with(self, f: FnOnce[T]) -> T:
        """Insert a value into the option computed from `f()` if it was `None`,
        and then return a reference to it.

        Example
        -------
        ```py
        flag: Option[bool] = Some(None)
        flag_ref = flag.insert(True)
        assert flag_ref == True
        assert flag.unwrap() == True
        ```
        """
        if self._value is not None:
            return self._value

        v = self._value = f()
        return v

    def and_ok(self, optb: Option[T]) -> Option[T]:
        """Returns `None` if `self` or `optb` is `None`, otherwise return `optb`.

        aliases: `Option::and`

        Example
        -------
        ```py
        x = Some(1)
        y: Option[str] = Some(None)
        assert x.and_ok(y) == Some(None)

        x: Option[str] = Some(None)
        y = Some(1)
        assert x.and_ok(y) == Some(None)

        y: Option[str] = Some("hi")
        y = Some(100)
        assert x.and_ok(y) == Some(100)
        ```
        """
        if self._value is None or optb._value is None:
            return optb

        return NOTHING  # pyright: ignore

    def and_then(self, f: Fn[T, Option[T]]) -> Option[T]:
        """Returns `Some(None)` if the contained value is `None`, otherwise call `f()`
        on `T` and return `Option[T]`.

        Example
        -------
        ```py
        value = Some(5)
        print(value.and_then(lambda x: Some(x * 2)))
        # Some(10)

        value: Option[int] = Some(None)
        print(value.and_then(lambda x: Some(x * 2)))
        # Some(None)
        ```
        """
        if self._value is None:
            return NOTHING  # pyright: ignore

        return f(self._value)

    def inspect(self, f: Fn[T, typing.Any]) -> Option[T]:
        """Calls `f()` on the contained value if it was `Some(v)`, otherwise does nothing.

        Example
        -------
        ```py
        def debug(x: Option[str]) -> None:
            print("Debugging:", x.into_inner())

        value = Some("foo")
        inner = value.inspect(debug).expect("no value to debug")
        # prints: Debugging: "foo"

        value: Option[str] = Some(None)
        value.inspect(debug) # prints nothing
        """
        if self._value is not None:
            f(self._value)

        return self

    # *- Builder methods *-

    def iter(self) -> _iter.Iterator[T]:
        """Returns an iterator over the contained value.

        Example
        -------
        ```py
        from sain import Some
        value = Some("gg")
        value.next() == Some("gg")

        value: Option[int] = Some(None)
        value.next().is_none()
        ```
        """
        if self._value is None:
            return _iter.empty()

        return _iter.once(self._value)

    # *- Boolean checks *-

    def is_some(self) -> bool:
        """Returns `True` if the contained value is not `None`, otherwise returns `False`.

        Example
        -------
        ```py
        value = Some(5)
        print(value.is_some())
        # True

        value: Option[int] = Some(None)
        print(value.is_some())
        # False
        ```
        """
        return self._value is not None

    def is_some_and(self, predicate: Fn[T, bool]) -> bool:
        """Returns `True` if the contained value is not `None` and
        the predicate returns `True`, otherwise returns `False`.

        Example
        -------
        ```py
        value = Some(5)
        print(value.is_some_and(lambda x: x > 3))
        # True

        value: Option[int] = Some(None)
        print(value.is_some_and(lambda x: x > 3))
        # False
        ```
        """
        return self._value is not None and predicate(self._value)

    def is_none(self) -> bool:
        """Returns `True` if the contained value is `None`, otherwise returns `False`.

        Example
        -------
        ```py
        value = Some(5)
        print(value.is_none())
        # False

        value: Option[int] = Some(None)
        print(value.is_none())
        # True
        ```
        """
        return self._value is None

    def __repr__(self) -> str:
        if self._value is None:
            return "None"
        return f"Some({self._value!r})"

    __str__ = __repr__

    def __invert__(self) -> T:
        return self.unwrap()

    def __or__(self, other: T) -> T:
        return self.unwrap_or(other)

    def __bool__(self) -> bool:
        return self.is_some()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Some):
            return NotImplemented

        return self._value == other._value  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self._value)


Option: typing.TypeAlias = Some[T]
"""A type hint for a value that can be `Some<T>` or `None`.

The reason this exist is to satisfy the UX with Rust's type system.

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

NOTHING: typing.Final[Some[None]] = Some(None)
"""A constant that is always `Option<None>`.

Example
-------
```py
from sain import NOTHING, Some

place_holder = NOTHING
assert NOTHING == Some(None) # True
```
"""


@typing.no_type_check
@macros.unsafe
def nothing_unchecked() -> Option[T]:
    """A placeholder that always returns `sain.NOTHING` but acts like it returns `Option[T]`.

    This is useful to avoid constructing new `Some(None)` and want to return `T` in the future.

    Example
    -------
    ```py
    class User:
        username: str

        def name(self) -> Option[str]:
            if '@' not in self.username:
                # even though the type of `NOTHING` is `Option[None]`.
                # we trick the type checker into thinking
                # that its an `Option[str]`.
                return NOTHING  # pyright: ignore

            return Some(self.username.split('@')[0])
    ```
    """
    return typing.cast("Option[T]", NOTHING)
