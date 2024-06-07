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

from . import cell
from . import default as _default
from . import iter
from . import macros

T = typing.TypeVar("T")
T_co = typing.TypeVar("T_co", covariant=True)

if typing.TYPE_CHECKING:
    import collections.abc as collections

    U = typing.TypeVar("U")
    Fn = collections.Callable[[T], U]
    FnOnce = collections.Callable[[], U]


@typing.final
class Some(typing.Generic[T], _default.Default[None]):
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

    __slots__ = ("_value", "__default")
    __match_args__ = ("_value",)

    def __init__(self, value: T | None, /) -> None:
        self._value = value

    @staticmethod
    def default() -> None:
        """Default value for `Some`. Returns `None`."""
        return None

    # *- Reading the value -*

    def into_inner(self) -> T | None:
        """Consume `Self`, returning the wrapped value as `T | None`.

        Examples
        --------
        ```py
        opt = Some('char')
        x = opt.into_inner()
        assert x is not None

        opt = Some(None)
        assert opt.into_inner() is None
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
            raise RuntimeError(
                f"Called `Option.unwrap()` on {type(self._value).__name__}."
            ) from None

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
        """Unwrap the inner value immediately returning it.

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

    # *- Functional operations -*
    def map(self, f: Fn[T, U], /) -> Some[U]:
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
            return nothing_unchecked()

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

    def filter(self, predicate: Fn[T, bool]) -> Some[T]:
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

        return nothing_unchecked()

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
            return nothing_unchecked()

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

        return nothing_unchecked()

    def replace(self, value: T) -> Some[T]:
        """Replace the contained value with another value.

        Example
        -------
        ```py
        value: Option[str] = Some(None)
        value = value.replace("Hello")
        # Some("Hello")
        ```
        """
        self._value = value
        return self

    def and_ok(self, optb: Some[T]) -> Some[T]:
        """Returns `Some(None)` if either contained value is `None`,

        Otherwise return `optb`.

        Example
        -------
        ```py
        x: Option[int] = Some(None)
        y: Option[str] = Some("bye")
        assert x.and_ok(y).is_none()

        x: Option[int] = Some(10)
        y: Option[str] = Some("bye")
        assert value.and_ok(y) == Some("bye")
        ```
        """
        if self._value is None or optb.is_none():
            return nothing_unchecked()

        return optb

    def and_then(self, f: Fn[T, Some[T]]) -> Some[T]:
        """Returns `Some(None)` if the contained value is `None`, otherwise call `f()`
        on `T` and return `Option[T]` if it's value not `None`.

        Example
        -------
        ```py
        value = Some(5)
        print(value.and_then(lambda x: Some(x * 2)))
        # Some(10)

        value: Option[int] = Some(10)
        print(value.and_then(lambda x: Some(None)))
        # Some(None)
        ```
        """
        if self._value is None:
            return nothing_unchecked()

        return f(self._value)

    # *- Builder methods *-

    def iter(self) -> iter.Iterator[T]:
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
            #! SAFETY: We know the value is None here.
            return iter.empty()  # pyright: ignore

        return iter.once(self._value)

    def as_ref(self) -> Some[cell.Cell[T]]:
        """Returns immutable `Some[sain.cell.Cell[T]]` if the contained value is not `None`,

        Otherwise returns `Some(None)`.

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
        # Some(None)
        ```

        Raises
        ------
        `dataclasses.FrozenInstanceError`
            When attempting to modify the contained value. Use `sain.AsRef.copy()` method to create a copy.

            Or just use `.as_mut()` if you're dealing with mutable objects.
        """
        if self._value is not None:
            return Some(cell.Cell(self._value))

        # SAFETY: self._value is None.
        return NOTHING  # pyright: ignore

    def as_mut(self) -> Some[cell.RefCell[T]]:
        """Returns mutable `Some[sain.cell.RefCell[T]]` if the contained value is not `None`,

        Otherwise returns `Some(None)`.

        Example
        -------
        ```py
        value = Some(5).as_mut().unwrap()
        value.object = 0
        print(value) # Some(RefCell(0))

        # None object.
        value: Option[int] = Some(None)
        print(value.as_mut())
        # Some(None)
        ```
        """
        if self._value is not None:
            return Some(cell.RefCell(self._value))

        # SAFETY: self._value is None.
        return NOTHING  # pyright: ignore

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
                return nothing_unchecked()

            return Some(self.username.split('@')[0])
    ```
    """
    return typing.cast("Option[T]", NOTHING)
