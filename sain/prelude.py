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

"""Exports a list of important types that almost every program using sain needs.

You then simply `from sain.prelude import *` and it will import all the necessary types.

Unlike `from sain import *` which imports all of the submodules as well, this will only import the following.

Prelude Contents
----------------
* `sain.collections.Vec`: A growable, extension of the builtin list type, Called a vector in Rust.
* `sain.collections.Slice`: A view into a contiguous sequence of elements.
* `sain.collections.SliceMut`: A mutable view into a contiguous sequence of elements.
* `sain.option.Option`, `sain.option.Some`: A type which expresses the absence or presence of a value.
* `sain.result.Result`, `sain.result.Err`, `sain.result.Ok`: a type for functions that may succeed or fail.
* `sain.default.Default`: A trait for types that have a default value.
* `sain.convert.Into`, `sain.convert.From`, `sain.convert.TryInto`, `sain.convert.TryFrom`, `sain.convert.ToString`: generic conversions.
* `sain.iter.Iterator`, `sain.iter.ExactSizeIterator`, `sain.iter.into_iter`: composable iteration.
* `sain.macros`: including `assert_eq`, `assert_ne`, `include_str`, `include_bytes`, `unimplemented`, `deprecated` and `todo`.
"""

from __future__ import annotations

__all__ = (
    "Vec",
    "Slice",
    "SliceMut",
    "Option",
    "Some",
    "Result",
    "Ok",
    "Err",
    "Default",
    "Into",
    "From",
    "TryInto",
    "TryFrom",
    "ToString",
    "Iterator",
    "ExactSizeIterator",
    "into_iter",
    "assert_eq",
    "assert_ne",
    "include_str",
    "include_bytes",
    "todo",
    "deprecated",
    "unimplemented",
)

# slice
from sain.collections.slice import Slice
from sain.collections.slice import SliceMut

# vec
from sain.collections.vec import Vec

# convert
from sain.convert import From
from sain.convert import Into
from sain.convert import ToString
from sain.convert import TryFrom
from sain.convert import TryInto

# default
from sain.default import Default

# iter
from sain.iter import ExactSizeIterator
from sain.iter import Iterator
from sain.iter import into_iter

# macros
from sain.macros import assert_eq
from sain.macros import assert_ne
from sain.macros import deprecated
from sain.macros import include_bytes
from sain.macros import include_str
from sain.macros import todo
from sain.macros import unimplemented

# option
from sain.option import Option
from sain.option import Some

# result
from sain.result import Err
from sain.result import Ok
from sain.result import Result
