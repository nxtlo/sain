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
"""An object that contains a reference to another object. See `AsRef` and `AsMut`."""

from __future__ import annotations

__all__ = ("AsRef", "AsMut", "ref", "ref_mut")

import copy
import dataclasses
import typing

_T_co = typing.TypeVar("_T_co", covariant=True)


def ref(value: _T_co) -> AsRef[_T_co]:
    """Construct an `AsRef` from a value.

    Equivalent to `x = sain.AsRef(value)`
    """
    return AsRef(value)


def ref_mut(value: _T_co) -> AsMut[_T_co]:
    """Construct an `AsMut` from a value.

    Equivalent to `x = sain.AsMut(value)`
    """
    return AsMut(value)


@typing.final
@dataclasses.dataclass(frozen=True, unsafe_hash=True)
class AsRef(typing.Generic[_T_co]):
    """Represents an immutable reference to an object.

    Example
    -------
    ```py
    from dataclasses import dataclass
    from sain import ref

    @dataclass
    class User:
        id: int
        name: str

    same_user = User(0, "sukuna")
    # Both keys point to the same user object.
    cache = {
        0: ref.ref(same_user),
        1: ref.ref(same_user)
    }

    cache[0].object.id = 1
    assert cache[1].object.id == 1  # True

    # Copying the object no longer points to it.
    # Unless the object is a collection.
    copy = cache[0].copy()
    copy.id = 2
    assert copy.id != cache[0].object.id  # True
    ```
    """

    __slots__ = ("object",)

    object: _T_co
    """The object that is being referenced."""

    def copy(self) -> _T_co:
        """Copy the referenced object.

        .. note::
            If the referenced object is a collection or contains a collection,
            Then this will copy its reference.
        """
        return copy.copy(self.object)


@typing.final
@dataclasses.dataclass(frozen=False, unsafe_hash=True)
class AsMut(typing.Generic[_T_co]):
    """Represents a mutable reference to an object."""

    __slots__ = ("object",)

    object: _T_co
    """The object that is being referenced."""

    def copy(self) -> _T_co:
        """Copy the referenced object.

        .. note::
            If the referenced object is a collection or contains a collection,
            Then this will copy its reference.
        """
        return copy.copy(self.object)
