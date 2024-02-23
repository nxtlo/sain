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

"""Standard Rust core types implementations for Python.

Equivalent types
----------------
- `Option<T>` -> `Option[T]` | `Some[T]`
- `Result<T, E>` -> `Result[T, E]`
- `Error` -> `Error`
- `Vec<T>` -> `Vec[T]`
- `Default<T>` -> `Default[T]`
- `AsRef<T>` -> `AsRef[T]`
- `AsMut<T>` -> `AsMut[T]`
- `Iter<Item>` -> `Iter[Item]`
- `OnceLock<T>` -> `Once[T]`

Equivalent macros
-----------------
As decorators.

- `cfg!()` -> `sain.cfg`
- `todo!()` -> `sain.todo`. This is not a decorator.
- `deprecated!()` -> `sain.deprecated`
- `unimplemented!()` -> `sain.unimplemented`
- `#[cfg_attr]` -> `sain.cfg_attr`
- `#[doc(...)]` -> `sain.doc(...)`
"""
from __future__ import annotations

__all__ = (
    # cfg.py
    "cfg",
    "cfg_attr",
    # default.py
    "Default",
    # ref.py
    "AsRef",
    "AsMut",
    # option.py
    "Some",
    "Option",
    "NOTHING",
    # iter.py
    "Iter",
    "iter",
    # macros.py
    "todo",
    "deprecated",
    "unimplemented",
    "doc",
    # futures.py
    "futures",
    # once.py
    "Once",
    # result.py
    "Ok",
    "Err",
    "Result",
    # vec.py
    "vec",
    "Vec",
    # error.py
    "Error",
    # boxed.py
    "Box",
)

from . import futures
from . import iter
from .boxed import Box
from .cfg import cfg
from .cfg import cfg_attr
from .default import Default
from .error import Error
from .iter import Iter
from .macros import deprecated
from .macros import doc
from .macros import todo
from .macros import unimplemented
from .once import Once
from .option import NOTHING
from .option import Option
from .option import Some
from .ref import AsMut
from .ref import AsRef
from .result import Err
from .result import Ok
from .result import Result
from .vec import Vec
from .vec import vec

__version__: str = "0.0.5"
__url__: str = "https://github.com/nxtlo/sain"
__author__: str = "nxtlo"
__about__: str = (
    "Sain is a dependency-free library that implements some of the Rust core"
    "types which abstracts over common patterns in Rust for Python."
)
__license__: str = "BSD 3-Clause License"
