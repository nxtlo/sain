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

"""sain is a set of minimal abstraction that brings Rust's ecosystem to Python. It offers a few of the core Rust types like `Vec<T>` and `Result<T, E>` and more."""

from __future__ import annotations

__all__ = (
    # cfg.py
    "cfg",
    "cfg_attr",
    # default.py
    "default",
    "Default",
    # option.py
    "option",
    "Some",
    "Option",
    "NOTHING",
    # iter.py
    "Iter",
    "Iterator",
    "iter",
    # macros.py
    "macros",
    "todo",
    "deprecated",
    "unimplemented",
    "doc",
    # futures.py
    "futures",
    # result.py
    "result",
    "Ok",
    "Err",
    "Result",
    # vec.py
    "vec",
    "Vec",
    # error.py
    "error",
    "Error",
    # boxed.py
    "boxed",
    "Box",
    # sync
    "sync",
    "MaybeUninit",
)

from . import boxed
from . import default
from . import error
from . import futures
from . import iter
from . import macros
from . import option
from . import result
from . import sync
from . import vec
from .boxed import Box
from .cfg import cfg
from .cfg import cfg_attr
from .default import Default
from .error import Error
from .iter import Iter
from .iter import Iterator
from .macros import deprecated
from .macros import doc
from .macros import todo
from .macros import unimplemented
from .maybe_uninit import MaybeUninit
from .option import NOTHING
from .option import Option
from .option import Some
from .result import Err
from .result import Ok
from .result import Result
from .vec import Vec

__version__: str = "0.0.6"
__url__: str = "https://github.com/nxtlo/sain"
__author__: str = "nxtlo"
__about__: str = (
    "Sain is a dependency-free library that implements some of the Rust core"
    "types which abstracts over common patterns in Rust for Python."
)
__license__: str = "BSD 3-Clause License"
