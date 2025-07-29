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
"""Dynamically growable collections and containers.

These collections are basic implementations of Rust's standard collections crate. from under the hood, they're an extended
and more rich implementations of the built-in sequences such as `list`, `dict` and `array.array`.

### When Should You Use Which Collection?
This question's answer should be pretty straightforward.

* Use `Vec` when you want to replace `list`.
* Use `Bytes` when you want to store read-only bytes. The underlying sequence is an `array` of type `u8`.
* Use `BytesMut` when you want a mutable version of `Bytes`.
* Use `HashMap` when you want to replace `dict`.
"""

from __future__ import annotations

__all__ = ("Vec", "Bytes", "BytesMut", "vec", "buf", "slice", "hash_map", "HashMap")

from . import buf
from . import hash_map
from . import slice
from . import vec
from .buf import Bytes
from .buf import BytesMut
from .hash_map import HashMap
from .vec import Vec
