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

"""Basic implementation of a cheap container for dealing with byte buffers."""

from __future__ import annotations

__all__ = ("Bytes", "Rawish")

import array
import io
import sys as _sys
import typing
from collections import abc as collections

from sain import iter as _iter
from sain import option as _option
from sain import result as _result

if typing.TYPE_CHECKING:
    from typing_extensions import Self

    from sain import Option
    from sain import Result

    Rawish: typing.TypeAlias = io.StringIO | io.BytesIO | io.BufferedReader | memoryview
    Buffer: typing.TypeAlias = bytes | bytearray | collections.Iterable[int] | "Bytes"

ENCODING = "utf-8"
REPLACEMENT_CHARACTER = "�"


def unwrap_bytes(data: Rawish) -> bytes:
    if isinstance(data, io.StringIO):
        buf = bytes(data.read(), encoding=ENCODING)
    elif isinstance(data, memoryview):
        buf = data.tobytes()
    else:
        buf = data.read()
    return buf


@typing.final
class Bytes:
    """Provides abstractions for working with UTF-8 compatible bytes.

    It is an efficient container for storing and operating with bytes.
    It behaves very much like `array.array[int]` as well has the same layout.

    A `Bytes` objects are usually used within networking applications, but can also be used
    elsewhere as well.

    Construction
    ------------
    `Bytes` object accept multiple rawish data types, See `Rawish` for all supported types.

    * `Bytes()`: Initialize an empty `Bytes` object
    * `from_str`: Create `Bytes` from `str`
    * `from_bytes`: Create `Bytes` from `bytes` | `bytearray` | `Sequence[int]`
    * `from_raw`: Create `Bytes` from a `Rawish` type
    * `from_static`: Create `Bytes` that points to an `array.array[int]`, no copying.

    Example
    -------
    ```py
    # Create basic `Bytes` object
    buffer = Bytes()
    buffer.put_str("Hello")
    print(buffer) # [72, 101, 108, 108, 111]
    print(buffer.to_str()) # Hello
    ```
    """

    __slots__ = ("_buf",)

    def __init__(self) -> None:
        """Creates a new empty `Bytes`.

        This won't allocate the array and the returned `Bytes` will be empty.
        """
        self._buf: array.array[int] | None = None

    # construction

    @classmethod
    def from_str(cls, s: str) -> Self:
        """Create a new `Bytes` from a string with the given encoding.

        Example
        -------
        ```py
        buffer = Bytes.from_str("💀")
        assert buffer.as_ref() == (240, 159, 146, 128)
        ```
        """
        b = cls()
        b._buf = array.array("B", s.encode(ENCODING))
        return b

    @classmethod
    def from_static(cls, arr: array.array[int]) -> Self:
        """Create a new `Bytes` from an array.

        The returned `Bytes` will directly point to `arr` without copying.

        Example
        -------
        ```py
        arr = array.array("B")
        buffer = Bytes.from_static(arr)
        ```
        """
        b = cls()
        b._buf = arr
        return b

    @classmethod
    def from_bytes(cls, buf: Buffer) -> Self:
        """Create a new `Bytes` from an initial bytes.

        Example
        -------
        ```py
        arr = array.array("B")
        buffer = Bytes.from_bytes(b"SIGNATURE")
        ```
        """
        b = cls()
        b._buf = array.array("B", buf)
        return b

    @classmethod
    def from_raw(cls, raw: Rawish) -> Self:
        """Initialize a new `Bytes` in-place from a valid raw data type.

        Example
        -------
        ```py
        with open('file.txt', 'rb') as file:
            buff = Bytes.from_raw(file)

        # in memory bytes io
        bytes_io = io.BytesIO(b"data")
        buffer1 = Bytes.from_raw(bytes_io)
        # in memory string io
        string_io = io.StringIO("data")
        buffer2 = Bytes.from_raw(string_io)
        ```

        Raises
        ------
        `ValueError`
            If `raw` contains a byte not in range `0..255`
        """
        c = cls()
        c._buf = array.array("B", unwrap_bytes(raw))
        return c

    def try_to_str(self) -> Result[str, bytes]:
        """A safe method to convert `self` into a string.

        This may fail if the `self` contains invalid bytes. strings
        needs to be valid utf-8.

        Example
        -------
        ```py
        buf = Bytes()
        sparkles_heart = [240, 159, 146, 150]
        buf.put(sparkles_heart)

        assert buf.try_to_str().unwrap() == "💖"
        ```

        Incorrect bytes
        ---------------
        ```py
        invalid_bytes = Bytes.from_raw([0, 159, 146, 150])
        invalid_bytes.try_to_str().is_err()
        ```

        Returns
        -------
        `Result[str, bytes]`
            If successful, returns the decoded string, otherwise the original bytes that failed.
        """
        try:
            return _result.Ok(self.as_bytes().decode(ENCODING))
        except UnicodeDecodeError as e:
            return _result.Err(e.object)

    def to_str(self) -> str:
        """Convert `self` to a utf-8 string. which may or may not be expensive.

        During the conversion process, any invalid bytes will get converted to
        [REPLACEMENT_CHARACTER](https://en.wikipedia.org/wiki/Specials_(Unicode_block))
        which looks like this `�`, so be carful on what you're trying to convert.

        Or just use `.try_to_str` which returns a `Result[str, bytes]` incase of failure.

        Example
        -------
        ```py
        buff = Bytes()
        sparkles_heart = [240, 159, 146, 150]
        buff.put(sparkles_heart)

        assert buf.to_str() == "💖"
        ```

        Incorrect bytes
        ---------------
        ```py
        invalid_bytes = Bytes.from_raw(b"Hello \xf0\x90\x80World")
        assert invalid_bytes.to_str() == "Hello �World"
        ```

        Unrecoverable failures
        ----------------------
        This method may raise `UnicodeDecodeError` if `self` contains
        invalid bytes that cannot be decoded.

        ```py
        invalid_bytes = Bytes.from_raw([0, 159, 146, 150])
        invalid_bytes.to_str() # ERROR
        ```
        """
        bytes_ = self.as_bytes()
        try:
            return bytes_.decode(ENCODING)
        except UnicodeDecodeError as err:
            start, end = err.start, err.end
            # we need to create a new copy of the bytes to replace the invalid bytes.
            new = bytes_.replace(bytes_[start:end], REPLACEMENT_CHARACTER.encode())
            return new.decode(ENCODING)

    # buffer evolution

    def leak(self) -> Option[array.array[int]]:
        """Consumes and leaks the underlying array, setting it to `None` and returning it.

        Nothing happen if it was already `None`.

        Example
        -------
        ```py
        bytes = Bytes.from_str("chunks of data")
        consumed = bytes.leak()

        assert bytes.is_empty()
        assert consumed.tobytes() == b"chunks of data"
        ```
        """
        if self._buf is None:
            return _option.nothing_unchecked()

        arr = self._buf
        self._buf = None
        return _option.Some(arr)

    def as_bytes(self) -> bytes:
        """Convert `self` into `bytes`.

        Example
        -------
        ```py
        buf = Bytes.from_str("Hello")
        assert buf.as_bytes() == b'Hello'
        ```
        """
        if not self._buf:
            return b""

        return self._buf.tobytes()

    def as_ref(self) -> collections.Sequence[int]:
        """Convert `self` into an immutable sequence.

        An empty sequence is returned if `self` hasn't been initialized.

        Example
        -------
        ```py
        buff = Bytes.from_str("Hello")
        assert buff.as_ref() == (72, 101, 108, 108, 111)
        ```
        """
        return tuple(self._buf) if self._buf is not None else ()

    def as_mut(self) -> collections.MutableSequence[int]:
        """Return `self` as a mutable sequence without copying.

        An empty sequence is returned if `self` hasn't been initialized.

        Example
        -------
        ```py
        buff = Bytes.from_str("Hello")
        assert buff.as_mut() == [72, 101, 108, 108, 111]
        ```
        """
        return self._buf.tolist() if self._buf is not None else []

    def raw_parts(
        self,
    ) -> tuple[typing.Annotated[int, "address"], typing.Annotated[int, "len"]]:
        """Return `self` as tuple containing the memory address to the buffer and how many bytes it currently contains"""
        if not self._buf:
            return (0x0, 0)

        return self._buf.buffer_info()

    # default methods.

    def put_raw(self, src: Rawish) -> None:
        """Extend `self` from a raw `src`.

        Example
        -------
        ```py
        ```

        Parameters
        ----------
        src : `Rawish`
            A valid raw data type. See `Rawish` for more details.

        Raises
        ------
        `OverflowError`
            If a byte in `src` is greater than `u8->MAX` which is 255.
        """
        if self._buf is None:
            self._buf = array.array("B", unwrap_bytes(src))
        else:
            self._buf.extend(unwrap_bytes(src))

    def put_int(self, u8: int) -> None:
        if self._buf is None:
            self._buf = array.array("B", (u8,))

    def put_bytes(self, src: Buffer) -> None:
        """Put `bytes` into `self`.

        `src` can be any type that is `bytes`, `bytearray` or a sequence of ints.

        Example
        -------
        ```py
        ```

        Parameters
        ----------
        src : `Buffer`
            Can be one of `Bytes`, `bytes`, `bytearray` or `Sequence[int]`

        Raises
        ------
        `OverflowError`
            If a byte in `src` is greater than `u8->MAX` which is 255.
        """
        if self._buf is None:
            # If it was `None`, we initialize it with a source instead of extending.
            self._buf = array.array("B", src)
        else:
            self._buf.extend(src)

    def put_str(self, s: str) -> None:
        """Put bytes into `self` from an encoded string, the string must be a valid UTF-8 encoded string.

        Example
        -------
        ```py
        buffer = Bytes()
        buffer.put_str("hello")

        assert buffer.to_str() == "hello"
        ```

        Parameters
        ----------
        src: `str`
            The string

        Raises
        ------
        `UnicodeEncodeError`
            If the string isn't a valid `UTF-8`.
        """
        self.put_bytes(s.encode(ENCODING))

    def len(self) -> int:
        """Return the number of elements in this buffer.

        Example
        -------
        ```py
        buf = Bytes()
        buf.put((1, 2, 3))
        assert buf.len() == 3
        ```
        """
        return self.__len__()

    def size(self) -> int:
        """The length in bytes of one array item in the internal representation.

        Example
        -------
        ```py
        buf = Bytes.from_raw([240, 159, 146, 150])
        assert buf.size() == 1
        ```
        """
        if not self._buf:
            return 0
        return self._buf.itemsize

    def iter(self) -> _iter.Iterator[int]:
        """Returns an iterator over the bytes of `self`.

        This iterator yields all `int`s from start to end.

        Example
        -------
        ```py
        buf = Bytes.from_raw((1, 2, 3))
        iterator = buf.iter()

        # map each byte to a character
        for element in iterator.map(chr):
            print(element)
        # ☺
        # ☻
        # ♥
        ```
        """
        return _iter.Iter(self)

    def is_empty(self) -> bool:
        """Check whether `self` contains any bytes or not.

        Example
        -------
        ```py
        buffer = Bytes()
        assert buffer.is_empty()
        ```
        """
        return not self._buf

    # layout methods.

    def copy(self) -> Self:
        """Create a copy of the bytes.

        Example
        -------
        ```py
        original = Bytes.from_raw([255, 255, 255, 0])
        copy = original.copy()
        ```
        """
        if not self._buf:
            return self.__class__()

        return self.from_static(self._buf[:])

    def clear(self) -> None:
        """Clear the buffer.

        Example
        -------
        ```py
        buf = Bytes([255])
        buf.clear()

        assert buf.is_empty()
        ```
        """
        if not self._buf:
            return

        self._buf.clear()

    def index(self, v: int, start: int = 0, stop: int = _sys.maxsize) -> int:
        """Return the smallest `i` such that `i` is the index of the
        first occurrence of `v` in the buffer.

        The optional arguments start and stop can be specified to search for x within a
        subsection of the array. Raise ValueError if x is not found
        """
        if not self._buf:
            raise ValueError from None

        return self._buf.index(v, start, stop)

    def count(self, x: int) -> int:
        """Return the number of occurrences of `x` in the buffer.

        Example
        --------
        ```py
        buf = Bytes([32, 32, 31])
        assert buf.count(32) == 2
        ```
        """
        if self._buf is None:
            return 0

        return self._buf.count(x)

    def insert(self, index: int, value: int) -> None:
        """Insert a new item with `value` in the buffer before position `index`.

        Negative values are treated as being relative to the end of the buffer.
        """
        if self._buf is None:
            return

        self._buf.insert(index, value)

    def pop(self, i: int = -1) -> Option[int]:
        """Removes the last element from the buffer and returns it, `Some(None)` if it is empty.

        Example
        -------
        ```py
        buf = Bytes((21, 32, 44))
        assert buf.pop() == Some(44)
        ```
        """
        if not self._buf:
            return _option.nothing_unchecked()

        return _option.Some(self._buf.pop(i))

    # special methods

    def __iter__(self) -> collections.Iterator[int]:
        if self._buf:
            return self._buf.__iter__()

        return ().__iter__()

    def __len__(self) -> int:
        return len(self._buf) if self._buf else 0

    def __repr__(self) -> str:
        return (
            "[]"
            if not self._buf
            else "[" + ", ".join(i.__str__() for i in self._buf) + "]"
        )

    __str__ = __repr__

    def __bytes__(self) -> bytes:
        return self.as_bytes()

    def __contains__(self, byte: int) -> bool:
        return byte in self._buf if self._buf else False

    def __eq__(self, other: object, /) -> bool:
        if not self._buf:
            return False

        return self._buf.__eq__(other)

    def __ne__(self, other: object, /) -> bool:
        return not self.__eq__(other)

    def __le__(self, other: object) -> bool:
        if not self._buf:
            return False

        if not isinstance(other, Bytes):
            return NotImplemented

        if not other._buf:
            return False

        return self._buf <= other._buf

    def __ge__(self, other: object) -> bool:
        if not self._buf:
            return False

        if not isinstance(other, Bytes):
            return NotImplemented

        if not other._buf:
            return False

        return self._buf >= other._buf

    def __lt__(self, other: object) -> bool:
        if not self._buf:
            return False

        if not isinstance(other, Bytes):
            return NotImplemented

        if not other._buf:
            return False

        return self._buf < other._buf

    def __gt__(self, other: object) -> bool:
        if not self._buf:
            return False

        if not isinstance(other, Bytes):
            return NotImplemented

        if not other._buf:
            return False

        return self._buf > other._buf

    def __setitem__(self, index: int, value: int):
        if not self._buf:
            raise IndexError from None

        self._buf[index] = value

    @typing.overload
    def __getitem__(self, index: slice) -> Self: ...

    @typing.overload
    def __getitem__(self, index: int) -> int: ...

    def __getitem__(self, index: int | slice) -> int | Self:
        if not self._buf:
            raise IndexError("Index out of range")

        if isinstance(index, slice):
            return self.from_static(self._buf[index])

        return self._buf[index]

    def __delitem__(self, key: typing.SupportsIndex | slice, /) -> None:
        if not self._buf:
            return

        del self._buf[key]
