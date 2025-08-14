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

__all__ = ("Bytes", "BytesMut", "Chars", "Buffer")

import array
import ctypes as _ctypes
import io as _io
import struct
import sys as _sys
import typing
from collections import abc as collections

from sain import convert
from sain import iter as _iter
from sain import option as _option
from sain import result as _result
from sain.macros import assert_precondition
from sain.macros import deprecated
from sain.macros import override
from sain.macros import rustc_diagnostic_item
from sain.macros import ub_checks
from sain.macros import unsafe
from sain.macros import unstable

from .slice import Slice
from .slice import SliceMut

if typing.TYPE_CHECKING:
    import inspect
    from types import EllipsisType

    from typing_extensions import Self

    from sain import Option
    from sain import Result


Buffer: typing.TypeAlias = (
    bytes
    | bytearray
    | collections.Iterable[int]
    | _io.StringIO
    | _io.BytesIO
    | _io.BufferedReader
)
"""Accepted types to create a `Bytes` from.

This can be any of:

bytes like types
---------------
* `bytes`
* `Bytes`
* `BytesMut`
* `bytearray`
* `Iterable[int]`
* `memoryview[int]`

IO like types
--------
* `io.StringIO`
* `io.BytesIO`
* `io.BufferedReader`
"""

ENCODING = "utf-8"


def unwrap_bytes(buf: Buffer) -> collections.Iterable[int]:
    if isinstance(buf, _io.StringIO):
        buf = bytes(buf.read(), encoding=ENCODING)
    elif isinstance(buf, (_io.BufferedReader, _io.BytesIO)):
        # BufferedReader | BytesIO
        buf = buf.read()

    # well, Iterable[int], array knows how to convert the passed type.
    return buf


@typing.final
class Chars(_iter.ExactSizeIterator[_ctypes.c_char]):
    """An iterator over the `c_char` of `Bytes`.

    This iterator is created by the `Bytes.chars` method. See its documentation for more.
    """

    __slots__ = ("_bytes", "_len", "_offset")

    def __init__(self, buf: Bytes) -> None:
        self._bytes = map(_ctypes.c_char, buf)
        self._len = len(buf)
        self._offset = buf.as_ptr()

    def as_slice(self) -> Slice[int]:
        """Views the underlying data as a subslice of the original data.

        Example
        -------
        ```py
        chars = Bytes.from_str("abc").chars()

        assert bytes(chars.as_slice()) == b"abc"
        chars.next()
        assert bytes(chars.as_slice()) == b"bc"
        chars.next()
        chars.next()
        assert bytes(chars.as_slice()) == b""
        ```
        """
        return Slice(self._offset[-self._len :])

    @override
    def __next__(self) -> _ctypes.c_char:
        self._len -= 1
        return self._bytes.__next__()

    @override
    def __len__(self) -> int:
        return self._len


@rustc_diagnostic_item("&[u8]")
@typing.final
class Bytes(convert.ToString, Slice[int]):
    """Provides immutable abstractions for working with bytes.

    The mutable version of this is `BytesMut`.

    # Overview

    This provides high-level, cheap, zero-copy slicing operations to perform on a sequence of bytes in
    an ergonomic way.

    `Bytes` is built on top of `array.array[int]` of type code `B`, so it has the same layout as `array.array[int]`,
    as well as all of it methods.

    The use cases of `Bytes` objects are usually within networking applications,
    binding with other foreign languages, manipulation of images and binaries, and more.

    ## Creating Bytes

    There're many different ways to create a `Bytes` object, the most straight-forward one is from a literal.

    ```py
    buffer = Bytes.from_bytes(b"hello")
    buffer2 = Bytes.from_str("hello")
    ```

    But, there're also many more ways to create one...

    * `Bytes()`: Initialize an empty `Bytes` object.
    * `from_str`: Create `Bytes` from `str`.
    * `from_bytes`: Create `Bytes` from a `Buffer` type.
    * `from_static`: Create `Bytes` that points to an `array.array[int]` without copying it
    * `Bytes.zeroed(count)`: Create `Bytes` filled with `zeroes * count`.

    ## Examples

    ```py
    from sain.collections import Bytes

    buf = Bytes.from_str("Hello")
    print(buf) # [72, 101, 108, 108, 111]
    # buf is currently immutable, to make it mutable use `buf.to_mut()`
    # the conversion costs nothing, as it just points to the same underlying array.
    buf_mut = buf.to_mut()
    buf_mut.put(32)
    assert buf_mut == b"Hello "
    ```
    """

    __slots__ = ("_buf",)

    def __init__(self) -> None:
        """Creates a new empty `Bytes`.

        Example
        -------
        ```py
        buf = Bytes()
        assert buf.is_empty()
        ```
        """
        self._buf: array.array[int] = array.array("B")

    # construction

    @classmethod
    def from_str(cls, s: str) -> Bytes:
        """Create a new `Bytes` from a string object.

        Example
        -------
        ```py
        buffer = Bytes.from_str("💀")
        ```
        """
        b = cls()
        b._buf.extend(s.encode(ENCODING))
        return b

    @classmethod
    def from_static(cls, arr: array.array[int]) -> Self:
        """Create a new `Bytes` from an array.

        The returned `Bytes` will directly point to `arr` without copying.

        Example
        -------
        ```py
        arr = array.array("B", b"Hello")
        buffer = Bytes.from_static(arr)
        ```
        """
        # this is technically an `assert` line
        # but Python isn't smart enough to inline and opt-out
        # this out of the generated bytecode for `assert_precondition`.
        # so we'll just leave this under `if` statement.
        if __debug__:
            assert_precondition(
                arr.typecode == "B",
                f"array type must be `B`, not `{arr.typecode}`",
                TypeError,
            )

        b = cls()
        b._buf = arr
        return b

    @classmethod
    @unsafe
    def from_static_unchecked(cls, arr: array.array[int]) -> Self:
        """Create a new `Bytes` from an array, without checking the type code.
        The returned `Bytes` will directly point to `arr` without copying.

        You must ensure that `arr` is of type `array.array[int]` with type code `B`.

        Example
        -------
        ```py
        arr = array.array("B", b"Hello")
        buffer = Bytes.from_static_unchecked(arr)
        ```
        """
        b = cls()
        b._buf = arr
        return b

    @classmethod
    def from_bytes(cls, buf: Buffer) -> Self:
        """Create a new `Bytes` from an initial bytes.

        If `buf` is a `Bytes`, then the returned `Bytes` will point
        to the same data that `buf` is pointing to.

        If you explicitly need an independent `Bytes`, call `.copy()` it.

        See `Buffer` to understand the accepted types.

        Example
        -------
        ```py
        buffer = Bytes.from_bytes(b"SIGNATURE")
        ```

        Passing a `Bytes` doesn't copy `buf`.
        ```py
        # Point to "buffer", this is isn't allowed in Rust because "buffer" is immutable
        # while "buffer2" is mutable, but, you do you.
        buffer2 = BytesMut.from_bytes(buffer)

        buffer2.put_str("-12")
        assert buffer.to_bytes() == b"SIGNATURE-12"
        ```
        """
        if isinstance(buf, Bytes) and buf._buf:
            # If buf is a Bytes, just point to its memory without copying it,
            # the exception being the memory must be initialized. otherwise
            # we create a new one.
            with ub_checks.nocheck():
                return cls.from_static_unchecked(buf._buf)

        b = cls()
        b._buf.extend(unwrap_bytes(buf))
        return b

    @classmethod
    def zeroed(cls, count: int) -> Self:
        """Initialize a new `Bytes` filled with `0 * count`.

        Example
        -------
        ```py
        ALLOC_SIZE = 1024 * 2
        buffer = Bytes.zeros(ALLOC_SIZE)
        assert buffer.len() == ALLOC_SIZE
        ```
        """
        c = cls()
        c._buf.extend(bytearray(count))
        return c

    @staticmethod
    @unstable(feature="bytes_raw_parts", issue="none")
    @unsafe
    def from_raw_parts(ptr: int, len: int) -> Bytes:
        """Construct a `Bytes` directly from a pointer address and a length.

        This can then be decomposed via `Bytes.to_raw_parts`.

        This is considered a very, low level method that FFI users may use to construct Bytes objects.

        Safety
        ------
        `ptr` must be a non-null, valid for reads for `len * u8` many bytes, and it must be properly aligned.

        Example
        -------
        Create `Bytes` from Rust raw pointer to an array of zeros.

        ```rs
        #[unsafe(no_mangle)]
        pub const extern "C" fn zeros() -> *const c_char {
            static DATA: [u8; 10] = [0; 10];
            DATA.as_ptr() as _
        }
        ```

        Compile and setup the FFI.

        ```py
        rust = ctypes.CDLL("zeros.dll")
        rust.zeros.restype = ctypes.POINTER(ctypes.c_uint8)

        # ...then use it
        ptr = rust.zeros()
        assert Bytes.from_raw_parts(ctypes.addressof(ptr.contents), 10).len() == 10
        ```
        """
        arr = (_ctypes.c_uint8 * len).from_address(ptr)

        # SAFETY: If the line above fails, thill will never be reached.
        with ub_checks.nocheck():
            return Bytes.from_static_unchecked(array.array("B", arr))

    @staticmethod
    @unstable(feature="bytes_raw_parts", issue="none")
    @unsafe
    def from_raw_parts_mut(ptr: int, len: int) -> BytesMut:
        """Construct a `BytesMut` directly from a pointer address and a length.

        This can then be decomposed via `Bytes.to_raw_parts`.

        This is considered a very, low level method that FFI users may use to construct Bytes objects.

        Safety
        ------
        `ptr` must be a non-null, valid for reads and writes for `len * u8` many bytes, and it must be properly aligned.

        Example
        -------
        Create `BytesMut` from Rust raw pointer to an array of zeros.

        ```rs
        #[unsafe(no_mangle)]
        pub const unsafe extern "C" fn zeros() -> *mut c_char {
            static mut DATA: [u8; 10] = [0; 10];
            &raw mut DATA as _
        }
        ```

        ```py
        # compile and setup the FFI.
        rust = ctypes.CDLL("zeros.dll")
        rust.zeros.restype = ctypes.POINTER(ctypes.c_uint8)

        # ...then use it
        ptr = rust.zeros()
        assert Bytes.from_raw_parts_mut(ctypes.addressof(ptr.contents), 10).len() == 10
        ```
        """
        arr = (_ctypes.c_uint8 * len).from_address(ptr)

        # SAFETY: If the line above fails, thill will never be reached.
        with ub_checks.nocheck():
            return BytesMut.from_static_unchecked(array.array("B", arr))

    # These are getting deprecated because they're trivial.
    # maybe we impl a `String` type and include them later.
    # anyways, they won't be leaving for sometime until 2.0.0.

    @deprecated(
        since="1.3.0",
        removed_in="2.0.0",
        use_instead='Bytes.to_bytes().decode("utf8")',
        hint="Converting a bytes object to string is fairly trivial.",
    )
    @override
    def to_string(self) -> str:
        """Convert the bytes to a string.

        Same as `Bytes.to_str`
        """
        # FIXME: Remove this pyright ignore when this method gets removed.
        return self.to_str()  # pyright: ignore

    @deprecated(
        since="1.3.0",
        removed_in="2.0.0",
        use_instead='Bytes.to_bytes().decode("utf8")',
        hint="Converting a bytes object to string is fairly trivial.",
    )
    def try_to_str(self) -> Result[str, bytes]:
        """A safe method to convert `self` into a string.

        This may fail if the `self` contains invalid bytes. strings
        needs to be valid utf-8.

        Example
        -------
        ```py
        buf = Bytes()
        sparkles_heart = [240, 159, 146, 150]
        buf.put_bytes(sparkles_heart)

        assert buf.try_to_str().unwrap() == "💖"
        ```

        Incorrect bytes
        ---------------
        ```py
        invalid_bytes = Bytes.from_bytes([0, 159, 146, 150])
        invalid_bytes.try_to_str().is_err()
        ```

        Returns
        -------
        `Result[str, bytes]`
            If successful, returns the decoded string, otherwise the original bytes that failed
            to get decoded.
        """
        try:
            return _result.Ok(self.to_bytes().decode(ENCODING))
        except UnicodeDecodeError as e:
            return _result.Err(e.object)

    @deprecated(
        since="1.3.0",
        removed_in="2.0.0",
        use_instead='str(Bytes, encoding="utf-8")',
        hint="Converting a bytes object to string is fairly trivial.",
    )
    def to_str(self) -> str:
        r"""Convert `self` to a utf-8 string.

        During the conversion process, any invalid bytes will get converted to
        [REPLACEMENT_CHARACTER](https://en.wikipedia.org/wiki/Specials_(Unicode_block))
        which looks like this `�`, so be careful on what you're trying to convert.

        Use `.try_to_str` try attempt the conversion in case of failure.

        Example
        -------
        ```py
        buf = Bytes()
        sparkles_heart = [240, 159, 146, 150]
        buf.put_bytes(sparkles_heart)

        assert buf.to_str() == "💖"
        ```

        Incorrect bytes
        ---------------
        ```py
        invalid_bytes = Bytes.from_bytes(b"Hello \xf0\x90\x80World")
        assert invalid_bytes.to_str() == "Hello �World"
        ```
        """
        if not self._buf:
            return ""

        return self._buf.tobytes().decode(ENCODING, errors="replace")

    def to_bytes(self) -> bytes:
        """Convert `self` into `bytes`, copying the underlying array into a new buffer.

        Example
        -------
        ```py
        buf = Bytes.from_str("Hello")
        assert buf.to_bytes() == b'Hello'
        ```
        """
        if not self._buf:
            return b""

        return self._buf.tobytes()

    def leak(self) -> array.array[int]:
        """Consumes and leaks the `Bytes`, returning the contents as an `array[int]`,

        A new empty array is returned if the underlying buffer is not initialized.

        `self` will deallocate the underlying array, therefore it becomes unusable.

        Safety
        ------
        It is unsafe to access the leaked array from `self` after calling this function.

        Example
        -------
        ```py
        bytes = Bytes.from_str("chunks of data")
        consumed = bytes.leak()
        # `bytes` doesn't point to anything, this is undefined behavior.
        bytes.put(0)
        # access the array directly instead.
        consumed.tobytes() == b"chunks of data"
        ```
        """
        arr = self._buf
        # We don't need to reference this anymore since the caller will own the array.
        del self._buf
        return arr

    @override
    def as_ptr(self) -> memoryview[int]:
        """Returns a read-only pointer to the buffer data.

        `pointer` here refers to a `memoryview` object.

        Example
        -------
        ```py
        buffer = Bytes.from_bytes(b"data")
        ptr = buffer.as_ptr()
        ptr[0] = 1 # TypeError: cannot modify read-only memory
        ```
        """
        return self.__buffer__(256).toreadonly()

    def as_slice(self) -> Slice[int]:
        """Get an immutable reference to the underlying sequence, without copying.

        An empty slice is returned if the underlying sequence is not initialized.

        Example
        -------
        ```py
        async def send_multipart(buf: Sequence[int]) -> None:
            ...

        buffer = Bytes.from_bytes([0, 0, 0, 0])
        # The `as_slice` call is not necessary, since `Bytes` can be treated
        # as both `Sequence[int]` and `Slice[int]`.
        # It just creates a new reference to the same data.
        await send_multipart(buffer.as_slice()) # no copy.
        ```
        """
        return Slice(self._buf)

    def to_mut(self) -> BytesMut:
        """Convert `self` into `BytesMut`.

        This consumes `self` and returns a new `BytesMut` that points to the same underlying array,
        The conversion costs nothing.

        After calling this, `self` will no longer be usable, as it will not point to the underlying array.

        The inverse method for this is `BytesMut.freeze()`

        Example
        -------
        ```py
        def modify(buffer: Bytes) -> BytesMut:
            buf = buffer.to_mut() # doesn't cost anything.
            buf.swap(0, 1)
            return buf

        buffer = Bytes.from_bytes([1, 2, 3, 4])
        new = modify(buffer)
        assert new == [2, 1, 3, 4]
        ```
        """
        with ub_checks.nocheck():
            return BytesMut.from_static_unchecked(self.leak())

    @override
    def iter(self) -> _iter.TrustedIter[int]:
        """Returns an iterator over the contained bytes.

        This iterator yields all `int`s from start to end.

        Example
        -------
        ```py
        buf = Bytes.from_bytes((1, 2, 3))
        iterator = buf.iter()

        # map each byte to a character
        for element in iterator.map(chr):
            print(element)
        # ☺
        # ☻
        # ♥
        ```
        """
        return _iter.TrustedIter(self.as_ptr())

    def chars(self) -> Chars:
        """Returns an iterator over the characters of `Bytes`.

        This iterator yields all of the bytes from start to end, mapping it as a `ctypes.c_char`.

        Example
        -------
        ```py
        b = Bytes.from_str("Hello")
        for char in b.chars():
            print(char)

        # c_char(b'H')
        # c_char(b'e')
        # c_char(b'l')
        # c_char(b'l')
        # c_char(b'o')
        ```
        """
        return Chars(self)

    def split_off(self, at: int) -> Bytes:
        """Split the bytes off at the specified position, returning a new
        `Bytes` at the range of `[at : len]`, leaving `self` at `[at : bytes_len]`.

        if this bytes is empty, `self` is returned unchanged.

        Example
        -------
        ```py
        origin = Bytes.from_bytes((1, 2, 3, 4))
        split = origin.split_off(2)

        print(origin, split)  # [1, 2], [3, 4]
        ```

        Raises
        ------
        `RuntimeError`
            This method will raise if `at` > `len(self)`
        """
        len_ = len(self._buf)
        if at > len_:
            raise RuntimeError(
                f"Index `at` ({at}) should be <= than len of `self` ({len_}) "
            ) from None

        # Either the list is empty or uninit.
        if not self._buf:
            return self

        split = self._buf[at:len_]  # split the items into a new buffer.
        del self._buf[at:len_]  # remove the items from the original list.
        return Bytes.from_static_unchecked(split)

    # array layout methods

    def copy(self) -> Bytes:
        """Create a copy of the bytes.

        Example
        -------
        ```py
        original = Bytes.from_bytes([255, 255, 255, 0])
        copy = original.copy()
        ```
        """
        if not self._buf:
            return Bytes()

        # SAFETY: `self._buf` is initialized.
        with ub_checks.nocheck():
            return self.from_static_unchecked(self._buf[:])

    def to_raw_parts(self) -> tuple[int, int]:
        """Decompose the metadata component of the bytes.

        Returns a `tuple<int, int>`, where the first element is the memory address of the bytes and the second is its length.

        This can then be re-composed via `Bytes.from_raw_parts`.

        This is an alias to `array.buffer_into`.

        Example
        -------
        ```py
        import ctypes
        from sain.collections import Bytes

        def c_array(ptr: int, len: int) -> ctypes.Array[ctypes.c_uint8]:
            return (ctypes.c_uint8 * len).from_address(ptr)

        buffer = Bytes.from_str("abc")
        ptr, size = buffer.to_raw_parts()
        print(
            bytes(from_raw_parts(ptr, size)) == b"abc"
        )
        """
        return self._buf.buffer_info()

    def size(self) -> int:
        """The length in bytes of one array item in the internal representation.

        This is an alias to `array.itemsize`

        Example
        -------
        ```py
        buf = Bytes.from_bytes([240, 159, 146, 150])
        assert buf.size() == 1
        ```
        """
        if not self._buf:
            return 0
        return self._buf.itemsize

    # special methods

    def __iter__(self) -> collections.Iterator[int]:
        return self._buf.__iter__()

    def __repr__(self) -> str:
        if not self._buf:
            return "[]"

        return "[" + ", ".join(str(x) for x in self._buf) + "]"

    __str__ = __repr__

    def __bytes__(self) -> bytes:
        return self.to_bytes()

    def __buffer__(self, flag: int | inspect.BufferFlags) -> memoryview[int]:
        if _sys.version_info >= (3, 12):
            mem = self._buf.__buffer__(flag)
        else:
            # arrays in 3.11 and under don't implement the buffer protocol.
            mem = memoryview(self._buf)

        return mem

    def __eq__(self, other: object, /) -> bool:
        if not self._buf:
            return False

        if isinstance(other, bytes):
            return self._buf.tobytes() == other

        # bytes IS a `Sequence[int]`, but not all `Sequence[int]`
        # represented as bytes.
        elif isinstance(other, collections.Sequence):
            return self._buf.tolist() == other

        return self._buf.__eq__(other)

    def __ne__(self, other: object, /) -> bool:
        return not self.__eq__(other)

    # defined like `array`'s
    __hash__: typing.ClassVar[None] = None

    @override
    def __copy__(self) -> Bytes:
        if not self._buf:
            return Bytes()

        with ub_checks.nocheck():
            return Bytes.from_static_unchecked(self._buf.__copy__())

    def __deepcopy__(self, unused: typing.Any, /) -> Bytes:
        if not self._buf:
            return Bytes()

        with ub_checks.nocheck():
            return Bytes.from_static_unchecked(self._buf.__deepcopy__(unused))


# NOTE: not a `SliceMut` because it causes layout conflicts.
# however, it can be achieved via `BytesMut.as_slice_mut()`
@rustc_diagnostic_item("&mut [u8]")
@typing.final
class BytesMut(
    Bytes,  # pyright: ignore - we want to inherit from `Bytes`.
    collections.MutableSequence[int],
):
    """Provides mutable abstractions for working with bytes.

    # Overview

    This provides high-level, cheap, zero-copy slicing operations to perform on a sequence of bytes in
    an ergonomic way.

    `BytesMut` is built on top of `array.array[int]` of type code `B`, so it has the same layout as `array.array[int]`,
    as well as all of it methods.

    The use cases of `BytesMut` objects are usually within networking applications,
    binding with other foreign languages, manipulation of images and binaries, and more.

    ## Creating a Bytes

    There're many different ways to create a `BytesMut` object, the most straight-forward one is from a literal.

    ```py
    buffer = BytesMut.from_bytes(b"hello")
    buffer2 = BytesMut.from_str("hello")
    ```

    But, there're also many more ways to create one...

    * `BytesMut()`: Initialize an empty `BytesMut` object.
    * `from_str`: Create `BytesMut` from `str`.
    * `from_bytes`: Create `BytesMut` from a `Buffer` bytes-like type.
    * `from_raw`: Create `BytesMut` from a `Rawish` type.
    * `from_static`: Create `BytesMut` that points to an `array.array[int]` without copying it
    * `BytesMut.zeroed(count)`: Create `BytesMut` filled with `zeroes * count`.

    ## Examples

    ```py
    from sain.collections import BytesMut

    buf = BytesMut.from_str("Hello")
    print(buf) # [72, 101, 108, 108, 111]
    buf.put(32)
    assert buf == b"Hello "

    # obtain a mutable slice out of `buf`.
    s = buf.as_slice_mut() # or buf[...]
    # do some operations on it.
    s.swap(buf[5], ord('!'))
    assert buf == b"Hello!"
    ```
    """

    __slots__ = ("_buf",)

    def __init__(self) -> None:
        """Creates a new empty `BytesMut`.

        Example
        -------
        ```py
        buf = BytesMut()
        ```
        """
        super().__init__()

    # default methods.

    def extend(self, src: Buffer) -> None:
        """Extend `self` from a `src`.

        Example
        -------
        ```py
        buf = Bytes()
        buf.extend([1, 2, 3])
        assert buf == [1, 2, 3]
        ```

        Parameters
        ----------
        src : `Buffer`
            The source to extend from. See `Buffer` for more details.
        """
        buf = unwrap_bytes(src)
        self._buf.extend(buf)

    def put(self, src: int) -> None:
        """Append a byte at the end of the array.

        unlike `.put_bytes`, this method appends instead of extending the array
        which is faster if you're putting a single byte in a single call.

        Example
        -------
        ```py
        buf = Bytes()
        buf.put(32) # append a space to the end of the buffer
        assert buf.to_bytes() == b' '
        ```

        Parameters
        ----------
        src : `int`
            An unsigned integer, also known as `u8`.
        """
        self._buf.append(src)

    def put_float(self, src: float) -> None:
        r"""Writes a single-precision (4 bytes) floating point number to `self` in big-endian byte order.

        The valid range for the float value is `-3.402823466e38` to `3.402823466e38`.

        Example
        -------
        ```py
        buf = BytesMut()
        buf.put_float(1.2)
        assert buf.to_bytes() == b'\x3f\x99\x99\x9a'
        ```

        Raises
        ------
        `OverflowError`
            If `src` is out of range.
        """
        assert_precondition(
            -3.402823466e38 <= src <= 3.402823466e38,
            f"Float {src} is out of range for a single-precision float",
            OverflowError,
        )
        pieces = struct.pack(">f", src)
        self._buf.extend(pieces)

    def put_char(self, char: str) -> None:
        """Append a single character to the buffer.

        This is the same as `self.put(ord(char))`.

        Example
        -------
        ```py
        buf = BytesMut()
        buf.put_char('a')
        assert buf == b"a"
        ```

        Parameters
        ----------
        char : `str`
            The character to put.
        """
        assert (ln := len(char)) == 1, f"Expected a single character, got {ln}"
        self.put(ord(char))

    def put_bytes(self, src: Buffer) -> None:
        """Put `bytes` into `self`.

        Example
        -------
        ```py
        buf = BytesMut.from_bytes(b"hello")
        buf.put_bytes([32, 119, 111, 114, 108, 100])
        assert buf == b"hello world"
        ```

        Parameters
        ----------
        src : `Buffer`
            The source to put into `self`. See `Buffer` for more details.
        """
        buf = unwrap_bytes(src)
        self._buf.extend(buf)

    def put_str(self, s: str) -> None:
        """Put a `utf-8` encoded bytes from a string.

        Example
        -------
        ```py
        buffer = BytesMut()
        buffer.put_str("hello")

        assert buffer == b"hello"
        ```

        Parameters
        ----------
        src: `str`
            The string
        """
        self.put_bytes(s.encode(ENCODING))

    def replace(self, index: int, byte: int) -> None:
        """Replace the byte at `index` with `byte`.

        This method is `NOOP` if:
        -------------------------
        * `self` is empty or unallocated.
        * `index` is out of range.

        Example
        -------
        ```py
        buf = BytesMut.from_bytes([1, 2, 3])
        buf.replace(1, 4)
        assert buf == [1, 4, 3]
        ```
        """
        if not self._buf or index < 0 or index >= self.len():
            return

        self._buf[index] = byte

    def replace_with(self, index: int, f: collections.Callable[[int], int]) -> None:
        """Replace the byte at `index` with a byte returned from `f`. Does nothing if empty.

        The signature of `f` is `Fn(int) -> int`, where the argument is the old byte.

        ## This method is `NOOP` if:
        * `self` is empty or unallocated.
        * `index` is out of range.

        Example
        -------
        ```py
        buf = BytesMut.from_bytes([1, 2, 3])
        buf.replace_with(1, lambda prev: prev * 2)
        assert buf == [1, 4, 3]
        ```
        """
        if not self._buf or index < 0 or index >= self.len():
            return

        old = self._buf[index]
        self._buf[index] = f(old)

    def offset(self, f: collections.Callable[[int], int]) -> None:
        """Modify each byte in the buffer with a new byte returned from `f`. Does nothing if empty.

        The signature of `f` is `Fn(int) -> int`, where the argument is the previous byte.

        Example
        -------
        ```py
        buf = BytesMut.from_bytes([1, 2, 3])
        buf.offset(lambda prev: prev * 2)
        assert buf == [2, 4, 6]
        ```
        """

        if not self._buf:
            return

        for index in range(len(self._buf)):
            self._buf[index] = f(self._buf[index])

    def fill(self, value: int) -> None:
        """Fills `self` with the given byte.

        Nothing happens if the buffer is empty or unallocated.

        Example
        -------
        ```py
        a = Bytes.from_bytes([0, 1, 2, 3])
        a.fill(0)
        assert a == [0, 0, 0, 0]
        ```
        """
        if not self._buf:
            return

        self.as_mut_ptr()[:] = bytearray([value] * self.len())

    def fill_with(self, f: collections.Callable[[], int]) -> None:
        """Fills `self` with the given byte returned from `f`.

        Nothing happens if the buffer is empty or unallocated.

        Example
        -------
        ```py
        def default() -> int:
            return 0

        a = Bytes.from_bytes([0, 1, 2, 3])
        a.fill_with(default)
        assert a == [0, 0, 0, 0]
        ```
        """
        if not self._buf:
            return

        self.as_mut_ptr()[:] = bytearray([f()] * self.len())

    def as_mut_ptr(self) -> memoryview[int]:
        """Returns a mutable pointer to the buffer data.

        `pointer` here refers to a `memoryview` object.

        Example
        -------
        ```py
        buffer = BytesMut.from_str("ouv")
        ptr = buffer.as_mut_ptr()
        ptr[0] = ord(b'L')
        assert buffer.to_bytes() == b"Luv"
        ```
        """
        return self.__buffer__(512)

    def as_slice_mut(self) -> SliceMut[int]:
        """Get a mutable slice to the underlying array, without copying.

        Example
        -------
        ```py
        buf = BytesMut.from_str("Hello")
        ref = buf.as_slice_mut()
        ```
        """
        return SliceMut(self._buf)

    def freeze(self) -> Bytes:
        """Convert `self` into an immutable `Bytes`.

        This conversion is zero-cost, meaning it doesn't any _hidden-copy_ operations behind the scenes.
        This consumes `self` and returns a new `Bytes` that points to the same underlying array,

        Notes
        -----
        * If `self` is not initialized, a new empty `Bytes` is returned.
        * `self` will no longer be usable, as it will not point to the underlying array.

        The inverse method of this is `Bytes.to_mut()`

        Example
        -------
        ```py
        def shrink_to(cap: int, buffer: BytesMut) -> Bytes:
            buf.truncate(cap)
            return buf.freeze()

        buffer = BytesMut.from_bytes([32, 23, 34, 65])
        # accessing `buffer` after this is undefined behavior.
        modified = shrink_to(2, buffer)
        assert modified == [32, 23]
        ```
        """
        with ub_checks.nocheck():
            return Bytes.from_static_unchecked(self.leak())

    def swap_remove(self, byte: int) -> int:
        """Remove the first appearance of `item` from this buffer and return it.

        Raises
        ------
        `ValueError`
            if `item` is not in this buffer.

        Example
        -------
        ```py
        buf = BytesMut.from_bytes([1, 2, 3, 4])
        assert 1 == buf.swap_remove(1)
        assert buf == [2, 3, 4]
        ```
        """
        return self._buf.pop(self.index(byte))

    def truncate(self, size: int) -> None:
        """Shortens the bytes, keeping the first `size` elements and dropping the rest.

        Example
        -------
        ```py
        buf = BytesMut.from_bytes([0, 0, 0, 0])
        buf.truncate(1)
        assert buf.len() == 1
        ```
        """
        if not self._buf:
            return

        del self._buf[size:]

    def split_off_mut(self, at: int) -> BytesMut:
        """Split the bytes off at the specified position, returning a new
        `BytesMut` at the range of `[at : len]`, leaving `self` at `[at : bytes_len]`.

        if this bytes is empty, `self` is returned unchanged.

        Example
        -------
        ```py
        origin = BytesMut.from_bytes((1, 2, 3, 4))
        split = origin.split_off_mut(2)

        print(origin, split)  # [1, 2], [3, 4]
        ```

        Raises
        ------
        `IndexError`
            This method will raise if `at` > `len(self)`
        """
        len_ = self.len()
        if at > len_:
            raise IndexError(
                f"the index of `at` ({at}) should be <= than len of `self` ({len_}) "
            ) from None

        if not self._buf:
            return self

        split = BytesMut.from_static(self._buf[at:len_])
        del self._buf[at:len_]
        return split

    # * Layout * #

    def insert(self, index: int, value: int) -> None:
        """Insert a new item with `value` in the buffer before position `index`.

        Negative values are treated as being relative to the end of the buffer.
        """
        self._buf.insert(index, value)

    def pop(self, i: int = -1) -> Option[int]:
        """Removes the last element from the buffer and returns it, `Some(None)` if it is empty.

        Example
        -------
        ```py
        buf = BytesMut((21, 32, 44))
        assert buf.pop() == Some(44)
        ```
        """
        if not self._buf:
            return _option.NOTHING

        return _option.Some(self._buf.pop(i))

    def remove(self, i: int) -> None:
        """Remove the first appearance of `i` from `self`.

        Example
        ------
        ```py
        buf = BytesMut.from_bytes([1, 1, 2, 3, 4])
        buf.remove(1)
        print(buf) # [1, 2, 3, 4]
        ```
        """
        if not self._buf:
            return

        self._buf.remove(i)

    def clear(self) -> None:
        """Clear the buffer.

        Example
        -------
        ```py
        buf = BytesMut.from_bytes([255])
        buf.clear()

        assert buf.is_empty()
        ```
        """
        if not self._buf:
            return

        del self._buf[:]

    def byteswap(self) -> None:
        """Swap the byte order of the bytes in `self`."""
        if not self._buf:
            return

        self._buf.byteswap()

    @override
    def copy(self) -> BytesMut:
        """Create a copy of the bytes.

        Example
        -------
        ```py
        original = BytesMut.from_bytes([255, 255, 255, 0])
        copy = original.copy()
        ```
        """
        if not self._buf:
            return BytesMut()

        with ub_checks.nocheck():
            return self.from_static_unchecked(self._buf[:])

    @override
    def __copy__(self) -> BytesMut:
        if not self._buf:
            return BytesMut()

        with ub_checks.nocheck():
            return BytesMut.from_static_unchecked(self._buf.__copy__())

    def __deepcopy__(self, unused: typing.Any, /) -> BytesMut:
        if not self._buf:
            return BytesMut()

        with ub_checks.nocheck():
            return BytesMut.from_static_unchecked(self._buf.__deepcopy__(unused))

    @typing.overload
    def __getitem__(self, index: int) -> int: ...

    @typing.overload
    def __getitem__(self, index: slice) -> SliceMut[int]: ...

    @typing.overload
    def __getitem__(self, index: EllipsisType) -> SliceMut[int]: ...

    @override
    def __getitem__(self, index: int | slice | EllipsisType) -> SliceMut[int] | int:
        if index is ...:
            # Full slice self[...], creates another reference to _buf
            return SliceMut(self._buf)

        if isinstance(index, slice):
            # Slicing like self[1:], self[:2], self[1:2]
            return SliceMut(self._buf[index])

        else:
            # index get item, i.e. self[0]
            return self._buf[index]

    @typing.overload
    def __setitem__(self, index: int, item: int) -> None: ...

    @typing.overload
    def __setitem__(self, index: slice, item: collections.Sequence[int]) -> None: ...

    def __setitem__(
        self, index: int | slice, item: int | collections.Sequence[int]
    ) -> None:
        self._buf[index] = item  # pyright: ignore - this is exactly how its defined in MutableSequence.

    def __delitem__(self, idx: int) -> None:
        del self._buf[idx]
