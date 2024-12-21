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

"""
Protocols for conversions between types.

The protocols in this module provide a way to convert from one type to another type. Each trait serves a different purpose:

* Implement the From trait for consuming value-to-value conversions
* Implement the Into trait for consuming value-to-value conversions to types outside the current crate
* The TryFrom and TryInto traits behave like From and Into, but should be implemented when the conversion can fail.
* Implement the `ToString` trait for explicitly converting objects to string.

Example
--------
```py
@dataclass
class Id(From[UUID], Into[int]):
    id: int | float

    @classmethod
    def from_t(cls, value: UUID) -> Self:
        # Keep in mind, this stores a 128 bit <long> integer.
        return cls(int(value))

    def into(self) -> int:
        return int(self.id)

# Simply perform conversions.
from_uuid = Id.from_t(uuid4())
into_int = from_uuid.into()
```

For type conversions that may fail, two safe interfaces, `TryInto` and `TryFrom` exist which deal with that.

This is useful when you are doing a type conversion that may trivially succeed but may also need special handling.

```py
@dataclass
class Message(Into[bytes], TryFrom[bytes, None]):
    content: str
    id: int

    def into(self) -> bytes:
        return json.dumps(self.__dict__).encode()

    @classmethod
    def try_from(cls, value: bytes) -> Result[Self, None]:
        try:
            payload = json.loads(value)
            return Ok(cls(content=payload['content'], id=payload['id']))
        except (json.decoder.JSONDecodeError, KeyError):
            # Its rare to see a JSONDecodeError raised, but usually
            # keys goes missing, which raises a KeyError.
            return Err(None)

message_bytes = b'{"content": "content", "id": 0}'

match Message.try_from(message_bytes):
    case Ok(message):
        print("Successful conversion", message)
    case Err(invalid_bytes):
        print("Invalid bytes:", invalid_bytes)

payload = Message(content='...', id=0)
assert payload.into() == message_bytes
```
"""

from __future__ import annotations

__slots__ = ("Into", "TryInto", "From", "TryFrom", "ToString")

import typing

if typing.TYPE_CHECKING:
    from typing_extensions import Self

    from sain import Result

T = typing.TypeVar("T")
T_co = typing.TypeVar("T_co", contravariant=True)
T_cov = typing.TypeVar("T_cov", covariant=True)
E = typing.TypeVar("E")


@typing.runtime_checkable
class From(typing.Protocol[T_co]):
    """Used to do value-to-value conversions while consuming the input value. It is the reciprocal of Into.

    As the Rust documentation says, One should always prefer implementing From over Into
    because implementing From automatically provides one with an implementation of Into.

    But there's no such thing in Python, as it's impossible to auto-impl `Into<T>` for all types
    that impl `From<T>`.

    So for the sake of simplicity, You should implement whichever interface you want deal with,
    Or simply, implement both as the same time.

    Example
    -------
    ```py
    @dataclass
    class Id(From[str]):
        value: int

        @classmethod
        def from_t(cls, value: str) -> Self:
            return cls(value=int(value))

    ```
    """

    __slots__ = ()

    @classmethod
    def from_t(cls, value: T_co) -> Self:
        """Perform the conversion."""
        raise NotImplementedError


@typing.runtime_checkable
class TryFrom(typing.Protocol[T_co, E]):
    """Simple and safe type conversions that may fail in a controlled way under some circumstances.
    It is the reciprocal of `TryInto`.

    It is useful to implement this when you know that the conversion may fail in some way.

    Generic Implementations
    -------------------
    This interface takes two type arguments, and return `Result<Self, E>`

    * `T`: Which's the first generic `T` is the type that's being converted from.
    * `E`: If the conversion fails in a way, this is what will return as the error.
    * `Self`: Which's the instance of the class that is being converted into.

    Example
    -------
    ```py
    @dataclass
    class Id(TryFrom[str, str]):
        value: int

        @classmethod
        def try_from(cls, value: str) -> Result[Self, str]:
            if not value.isnumeric():
                # NaN
                return Err(f"Couldn't convert: {value} to self")
            # otherwise convert it to an Id instance.
            return Ok(value=cls(int(value)))
    ```
    """

    __slots__ = ()

    @classmethod
    def try_from(cls, value: T_co) -> Result[Self, E]:
        """Perform the conversion."""
        raise NotImplementedError


@typing.runtime_checkable
class Into(typing.Protocol[T_cov]):
    """Conversion from `self`, which may or may not be expensive.

    Example
    -------
    ```py
    @dataclass
    class Id(Into[str]):
        value: int

        def into(self) -> str:
            return str(self.value)
    ```
    """

    __slots__ = ()

    def into(self) -> T_cov:
        """Perform the conversion."""
        raise NotImplementedError


@typing.runtime_checkable
class TryInto(typing.Protocol[T, E]):
    """An attempted conversion from `self`, which may or may not be expensive.

    It is useful to implement this when you know that the conversion may fail in some way.

    Generic Implementations
    -------------------
    This interface takes two type arguments, and return `Result<T, E>`

    * `T`: The first generic `T` is the type that's being converted into.
    * `E`: If the conversion fails in a way, this is what will return as the error.

    Example
    -------
    ```py
    @dataclass
    class Id(TryInto[int, str]):
        value: str

        def try_into(self) -> Result[int, str]:
            if not self.value.isnumeric():
                return Err(f"{self.value} is not a number...")
            return Ok(int(self.value))
    ```
    """

    __slots__ = ()

    def try_into(self) -> Result[T, E]:
        """Perform the conversion."""
        raise NotImplementedError


@typing.runtime_checkable
class ToString(typing.Protocol):
    """A trait for explicitly converting a value to a `str`.

    Example
    -------
    ```py
    class Value[T: bytes](ToString):
        buffer: T

        def to_string(self) -> str:
            return self.buffer.decode("utf-8")
    ```
    """

    __slots__ = ()

    def to_string(self) -> str:
        """Converts the given value to a `str`.

        Example
        --------
        ```py
        i = 5  # assume `int` implements `ToString`
        five = "5"
        assert five == i.to_string()
        ```
        """
        raise NotImplementedError

    def __str__(self) -> str:
        return self.to_string()
