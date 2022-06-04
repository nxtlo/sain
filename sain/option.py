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
"""Rust's `Option<T> error handling implementation for Python`."""

from __future__ import annotations

__all__: tuple[str, ...] = ("Some", "Fn", "FnOnce", "ValueT", "OkT", "ErrT", "Option")

import typing

from . import default as _default
from . import ref as _ref

ValueT = typing.TypeVar("ValueT")
"""A type hint that represents the generic value of the `Some` type."""
OkT = typing.TypeVar("OkT")
"""The `Ok` result of a `Result`."""
ErrT = typing.TypeVar("ErrT")
"""The `Err` result of a `Result`."""

T = typing.TypeVar("T")
U = typing.TypeVar("U")
T_co = typing.TypeVar("T_co", covariant=True)

Fn = typing.Callable[[ValueT], T]
"""A type hint for a function that can take a `ValueT` and return a `T`."""
FnOnce = typing.Callable[[], T]
"""A type hint for a function that takes no arguments and return `T`"""


@typing.final
class Some(typing.Generic[ValueT], _default.Default[None]):
    """The `Some` object. A typesafe object is used for values that might be `T` or `None`.

    It is similar to `typing.Optional[T]`, But has proper methods to handle the contined value.

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

    def __init__(self, value: ValueT | None, /) -> None:
        self._value = value

    @staticmethod
    def default() -> None:
        """Return the default value for `Some`. This always returns `None`."""
        return None

    @property
    def read(self) -> ValueT | None:
        """Read the contained value."""
        return self._value

    def unwrap(self) -> ValueT:
        """Unwrap the inner value either returning if its not `None` or raising a `RuntimeError`.

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
            raise RuntimeError(f"Can't unwrap {type(self).__name__} value.") from None

        return self._value

    def unwrap_or(self, default: ValueT, /) -> ValueT:
        """Unwrap the inner value either returning if its not `None` or returning `default`.

        Example
        -------
        ```py
        value = Some(5)
        print(value.unwrap_or(10))
        # 5

        # Type hint is required here.

        value: Some[int] = Some(None)
        print(value.unwrap_or(10))
        # 10
        ```
        """
        if self._value is None:
            return default

        return self._value

    def unwrap_or_else(self, f: FnOnce[ValueT], /) -> ValueT:
        """Unwrap the inner value either returning if its not `None` or calling `f` to get a default value.

        Example
        -------
        ```py
        value = Some(5)
        print(value.unwrap_or_else(lambda: 10))
        # 5

        value: Some[bool] = Some(None)
        print(value.unwrap_or_else(lambda: True))
        # True
        ```
        """
        if self._value is None:
            return f()

        return self._value

    # Functional.
    def map(self, f: Fn[ValueT, T], /) -> Some[T | None]:
        """Map the inner value to a new value. Returning `Some[None]` if `ValueT` is `None`.

        Example
        -------
        ```py
        value = Some(5.0)

        print(value.map(lambda x: x * 2.0))
        # Some(10.0)

        value: Some[bool] = Some(None)
        print(value)
        # Some(None)
        ```
        """
        if self._value is None:
            return Some(None)

        return Some(f(self._value))

    def map_or(self, default: T, f: Fn[ValueT, T], /) -> T:
        """Map the inner value to a new value or return `default` if its `None`.

        Example
        -------
        ```py
        value = Some(5.0)

        # Since the value is not `None` this will get mapped.
        print(value.map_or(10.0, lambda x: x + 1.0))
        # 6.0

        # This is `None`, so the default value will be returned.
        value: Some[str] = Some(None)
        print(value.map_or("5", lambda x: str(x)))
        # "5"
        ```
        """
        if self._value is None:
            return default

        return f(self._value)

    def map_or_else(self, default: FnOnce[T], f: typing.Callable[[ValueT], T], /) -> T:
        """Map the inner value to a new value, Or return default which maps to `default()` if its `None`.

        Example
        -------
        ```py
        value = Some(5.0)

        # Since the value is not `None` this will get mapped.
        print(value.map_or_else(lambda: 10.0, lambda x: x + 1.0))
        # 6.0

        # This is `None`, so the default func will be returned.
        value: Option[str] = Some(None)
        print(value.map_or_else(lambda: "5", lambda x: str(x)))
        # "5"
        ```
        """
        if self._value is None:
            return default()

        return f(self._value)

    def filter(self, predicate: Fn[ValueT, bool]) -> Some[ValueT]:
        """Returns `Some[None]` if the contained value is `None`,

        otherwise calls the predicate and returns `Some[ValueT]` if the predicate returns `True`.

        Example
        -------
        ```py
        value = Some([1, 2, 3])

        print(value.filter(lambda x: len(x) >= 2))
        # Some([1, 2, 3])

        value: Some[int] = Some(None)
        print(value.filter(lambda x: x > 3))
        # None
        ```
        """
        if (value := self._value) is not None:
            if predicate(value):
                return Some(value)

        # We could return `None` here, but we want to return `Some[None]` instead.
        return Some(None)

    def take(self) -> None:
        """Take the value from the `Some` object setting it to `None`.

        Example
        -------
        ```py
        value = Some("Hi")
        value = value.take()
        print(value)
        # None
        ```
        """
        v = self._value = None
        return v

    def replace(self, value: ValueT) -> Some[ValueT]:
        """Replace the contained value with another value.

        Example
        -------
        ```py
        value = Some("Hi")
        value = value.replace("Hello")

        print(value)
        # Some("Hello")
        ```
        """
        v = self._value = value
        return Some(v)

    # Boolean checkings.
    def expect(self, message: str, /) -> ValueT:
        """Returns `ValueT` if the contained value is not `None` otherwise raises a `RuntimeError`.

        Example
        -------
        ```py
        value = Some("Hello")

        print(value.expect("Value is None"))
        # "Hello"

        value: Some[str] = Some(None)
        print(value.expect("Value is None"))
        # RuntimeError("Value is None")
        ```
        """
        if self._value is None:
            raise RuntimeError(message)

        return self._value

    def and_ok(self, optb: Some[T | None]) -> Some[T | None]:
        """Returns `Some[None]` if the contained value is `None`,

        Otherwise return optb as `Some[T | None]` if optb is `Some[T]`.

        Example
        -------
        ```py
        value = Some(5)

        print(value.and_ok(Some(10)))
        # Some(10)

        value: Some[int] = Some(10)
        print(value.and_ok(Some(None)))  # optb is `None`.
        # Some(None)
        ```
        """
        if self._value is None:
            return Some(None)

        return optb

    def and_then(self, f: Fn[ValueT, Some[T | None]]) -> Some[T | None]:
        """Returns `Some[None]` if the contained value is `None`,

        otherwise call `f` on `ValueT` and return `Some[T]` if it's value not `None`.

        Example
        -------
        ```py
        value = Some(5)
        print(value.and_then(lambda x: Some(x * 2)))
        # Some(10)

        value: Some[int] = Some(10)
        print(value.and_then(lambda x: Some(None)))
        # Some(None)
        ```
        """
        if self._value is None:
            return Some(None)

        return f(self._value)

    def as_ref(self) -> Some[_ref.Ref[ValueT]]:
        """Returns immutable `Some[Ref[ValueT]]` if the contained value is not `None`,

        Otherwise returns `Some[None]`.

        Example
        -------
        ```py
        value = Some(5).as_ref().unwrap()
        value.object = 0 # FrozenError!

        owned = value.object
        print(owned) # 5

        # Create a copy of object.
        clone = value.copy()
        clone = 0  # Thats fine.
        print(clone == owned) # False, 0 != 5

        # None object.
        value: Some[int] = Some(None)
        print(value.as_ref())
        # Some(Ref(None))
        ```

        Raises
        ------
        `dataclasses.FrozenInstanceError`
            When attempting to modify the contained value. Use `sain.Ref.copy()` method to create a copy.

            Or just use `Some.as_ref_mut()` if you're dealing with mutable objects.
        """
        if self._value is not None:
            return Some(_ref.Ref(self._value))

        return Some(None)

    def as_mut(self) -> Some[_ref.RefMut[ValueT]]:
        """Returns mutable `Some[RefMut[ValueT]]` if the contained value is not `None`,

        Otherwise returns `Some[None]`.

        Example
        -------
        ```py
        value = Some(5).as_ref_mut().unwrap()
        value.object = 0
        print(value.object) # 0

        # None object.
        value: Some[int] = Some(None)
        print(value.as_ref_mut())
        # Some(RefMut(None))
        ```
        """
        if self._value is not None:
            return Some(_ref.RefMut(self._value))

        return Some(None)

    def is_some(self) -> bool:
        """Returns `True` if the contained value is not `None`, otherwise returns `False`.

        Example
        -------
        ```py
        value = Some(5)
        print(value.is_some())
        # True

        value: Some[int] = Some(None)
        print(value.is_some())
        # False
        ```
        """
        return self._value is not None

    def is_some_and(self, predicate: Fn[ValueT, bool]) -> bool:
        """Returns `True` if the contained value is not `None` and
        the predicate returns `True`, otherwise returns `False`.

        Example
        -------
        ```py
        value = Some(5)
        print(value.is_some_and(lambda x: x > 3))
        # True

        value: Some[int] = Some(None)
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

        value: Some[int] = Some(None)
        print(value.is_none())
        # True
        ```
        """
        return not self.is_some()

    def __str__(self) -> str:
        return f"Some({self._value!r})"

    def __repr__(self) -> str:
        return f"Some({self._value!r})"

    def __bool__(self) -> bool:
        return self.is_some()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Some):
            return NotImplemented

        return self._value == other.read

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self._value)


# TODO: Make a .pyi file.
Option = Some[ValueT]
"""A type hint for a value that can be `Some[T]`.

Example
-------
```py
import sain

foo: sain.Option[str] = sain.Some("foo")
```
"""
