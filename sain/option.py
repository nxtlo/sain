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

__all__ = ("Some", "ValueT")

import typing

from . import default as _default
from . import iter
from .cell import ref

ValueT = typing.TypeVar("ValueT")
"""A type hint that represents the generic value of the `Some` type."""

T = typing.TypeVar("T")
T_co = typing.TypeVar("T_co", covariant=True)

if typing.TYPE_CHECKING:
    import collections.abc as collections

    Fn = collections.Callable[[ValueT], T]
    FnOnce = collections.Callable[[], T]


@typing.final
class Some(typing.Generic[ValueT], _default.Default[None]):
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

    def __init__(self, value: ValueT | None, /) -> None:
        self._value = value

    @staticmethod
    def default() -> None:
        """Default value for `Some`. Returns `None`."""
        return None

    # *- Reading the value -*

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
            raise RuntimeError(
                f"Called `Option::unwrap()` on {type(self._value).__name__}."
            ) from None

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
        value: Option[int] = Some(None)
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

        value: Option[bool] = Some(None)
        print(value.unwrap_or_else(lambda: True))
        # True
        ```
        """
        if self._value is None:
            return f()

        return self._value

    def unwrap_unchecked(self) -> ValueT:
        """Unwrap the inner value immediately returning it.

        ## Warning
        Unwrapping the value knowing its `None` is considered Undefined Behavior.

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
        return self._value  # type: ignore

    def expect(self, message: str, /) -> ValueT:
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

    # *- Functional operations -*
    def map(self, f: Fn[ValueT, T], /) -> Some[T]:
        """Map the inner value to a new value. Returning `Some[None]` if `ValueT` is `None`.

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
        value: Option[str] = Some(None)
        print(value.map_or("5", lambda x: str(x)))
        # "5"
        ```
        """
        if self._value is None:
            return default

        return f(self._value)

    def map_or_else(self, default: FnOnce[T], f: Fn[ValueT, T], /) -> T:
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

        value: Option[int] = Some(None)
        print(value.filter(lambda x: x > 3))
        # None
        ```
        """
        if (value := self._value) is not None:
            if predicate(value):
                return Some(value)

        return Some(None)

    # *- Inner operations *-

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
        if self._value is None:
            return

        self._value = None

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
        self._value = value
        return Some(self._value)

    def and_ok(self, optb: Some[T]) -> Some[T]:
        """Returns `Some[None]` if the contained value is `None`,

        Otherwise return optb as `Some[T | None]` if optb is `Some[T]`.

        Example
        -------
        ```py
        value = Some(5)

        print(value.and_ok(Some(10)))
        # Some(10)

        value: Option[int] = Some(10)
        print(value.and_ok(Some(None)))  # optb is `None`.
        # Some(None)
        ```
        """
        if self._value is None:
            return Some(None)

        return optb

    def and_then(self, f: Fn[ValueT, Some[T]]) -> Some[T]:
        """Returns `Some[None]` if the contained value is `None`,

        otherwise call `f` on `ValueT` and return `Some[T]` if it's value not `None`.

        Example
        -------
        ```py
        value = Some(5)
        print(value.and_then(lambda x: Option(x * 2)))
        # Some(10)

        value: Option[int] = Some(10)
        print(value.and_then(lambda x: Option(None)))
        # Some(None)
        ```
        """
        if self._value is None:
            return Some(None)

        return f(self._value)

    # *- Builder methods *-

    def iter(self) -> iter.Iter[ValueT]:
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
            return iter.into_iter(())

        return iter.once(self._value)

    def as_ref(self) -> Some[ref.Cell[ValueT]]:
        """Returns immutable `Some[Cell[ValueT]]` if the contained value is not `None`,

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
        value: Option[int] = Some(None)
        print(value.as_ref())
        # Some(AsRef(None))
        ```

        Raises
        ------
        `dataclasses.FrozenInstanceError`
            When attempting to modify the contained value. Use `sain.AsRef.copy()` method to create a copy.

            Or just use `.as_mut()` if you're dealing with mutable objects.
        """
        if self._value is not None:
            return Some(ref.Cell(self._value))

        return Some(None)

    def as_mut(self) -> Some[ref.RefCell[ValueT]]:
        """Returns mutable `Some[RefCell[ValueT]]` if the contained value is not `None`,

        Otherwise returns `Some[None]`.

        Example
        -------
        ```py
        value = Some(5).as_ref_mut().unwrap()
        value.object = 0
        print(value.object) # 0

        # None object.
        value: Option[int] = Some(None)
        print(value.as_ref_mut())
        # Some(AsMut(None))
        ```
        """
        if self._value is not None:
            return Some(ref.RefCell(self._value))

        return Some(None)

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

    def is_some_and(self, predicate: Fn[ValueT, bool]) -> bool:
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
        return f"Some({self._value!r})"

    __str__ = __repr__

    def __invert__(self) -> ValueT:
        return self.unwrap()

    def __or__(self, other: ValueT) -> ValueT:
        return self.unwrap_or(other)

    def __bool__(self) -> bool:
        return self.is_some()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Some):
            return NotImplemented

        return self._value == other.read  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self._value)


Option: typing.TypeAlias = Some[T]
"""A type hint for a value that can be `Some<T>`.

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
def nothing_unchecked() -> Option[T]:
    """A placeholder that always returns `sain.NOTHING` but acts like it returns `Option[T]`.

    This is useful when you don't want to build `Some(None)` and want to return `T` in the future.

    # Warning
    unwrapping a value that returns this placeholder is undefined behavior.

    Example
    -------
    ```py
    class User:
        def name(self) -> Option[str]:
            # Don't build a new `Some(None)`
            return nothing_unchecked()

    user = User()
    user.name().unwrap()  # returns str? This is wrong.

    class Member(User):
        def name(self) -> Option[str]:
            return Some("username")

    member = Member()
    member.name().unwrap()  Ok
    ```
    """
    return typing.cast("Option[T]", NOTHING)
