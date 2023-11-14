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
"""Referenced objects to a value. This can be used to store an object in the same place multiple times.

Example
-------
```py
from sain import Ref
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str

cache: dict[int, Ref[User]] = {}

# Point the user ID to multiple references for this user.
# This is usefull when you want to store the object multiple times in the map.
user_once = User(0, "some_name")
cache[user_once.id] = Ref(user_once)

ref = cache[user_once.id]
ref.object.id = 1

# Clone the referenced object.
cloned = ref.copy()
cloned.id != 1
```
"""

from __future__ import annotations

__all__ = ("Ref", "RefMut")

import copy
import dataclasses
import typing

_T_co = typing.TypeVar("_T_co", covariant=True)


@dataclasses.dataclass(frozen=True, unsafe_hash=True)
class Ref(typing.Generic[_T_co]):
    """Represents an immutable reference to an object."""

    __slots__ = ("object",)

    object: _T_co
    """The object that is being referenced."""

    def copy(self) -> _T_co:
        """Copy of the referenced object."""
        return copy.copy(self.object)


@dataclasses.dataclass(frozen=False, unsafe_hash=True)
class RefMut(typing.Generic[_T_co]):
    """Represents a mutable reference to an object."""

    __slots__ = ("object",)

    object: _T_co
    """The object that is being referenced."""

    def copy(self) -> _T_co:
        """Copy of the referenced object."""
        return copy.copy(self.object)
