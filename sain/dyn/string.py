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

"""A UTF-8–encoded, growable string, equivalent to Rust's `String`."""

from __future__ import annotations

__all__ = ("String",)

import typing

from sain import Err
from sain import Ok

from . import vec as _vec

if typing.TYPE_CHECKING:
    from collections import abc as collections
    from typing import Self

    from sain import Result

UTF_8 = "utf-8"


@typing.final
class String:
    __slots__ = ("_vec",)

    @typing.overload
    def __init__(self, origin: collections.Iterable[int]) -> None: ...

    @typing.overload
    def __init__(self) -> None: ...

    def __init__(self, origin: collections.Iterable[int] = []):
        # TODO: Change Vec to Buf when implemented.
        self._vec = _vec.Vec(origin)

    # object constructors.

    @classmethod
    def with_capacity(cls) -> Self:
        new = cls()
        return new

    @classmethod
    def from_bytes(cls, s: bytes):
        new = cls()
        new.push_bytes(s)
        return new

    @classmethod
    def from_str(cls, s: str):
        new = cls()
        new.push_str(s)
        return new

    @classmethod
    def from_utf8(cls, s: collections.Iterable[int]) -> Result[Self, None]:
        new = cls(s)
        if not s:
            return Ok(new)

        new._vec.extend(s)
        try:
            # We need to make sure that the bytes are valid UTF-8.
            bytearray(new._vec).decode(UTF_8)
        except UnicodeDecodeError:
            return Err(None)

        return Ok(new)

    # object mutation.

    def push_str(self, s: str):
        self._vec.extend(s.encode(UTF_8))

    def push_bytes(self, b: bytes) -> None:
        self._vec.extend(b)

    def push(self, byte: int) -> None:
        self._vec.append(byte)

    # object view.

    def as_str(self) -> str:
        # return self._vec.decode(UTF_8)
        ...

    def as_bytes(self) -> bytes:
        return bytes(self._vec)

    def as_ptr(self) -> memoryview:
        return memoryview(self.as_bytes())

    def __str__(self) -> str:
        return self.as_str()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, String):
            return False

        return self._vec == other._vec

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __index__(self, i: int) -> int:
        return self._vec[i]

    def __getitem__(self, i: int) -> int:
        return self._vec.__getitem__(i)

    def __hash__(self) -> int:
        return self.as_bytes().__hash__()
