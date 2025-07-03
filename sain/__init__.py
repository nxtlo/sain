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
.. include:: ../DOCS.md
"""

from __future__ import annotations

__all__ = (
    # async_iter.py
    "async_iter",
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
    "include_str",
    "include_bytes",
    "assert_eq",
    "assert_ne",
    # futures.py
    "futures",
    # result.py
    "result",
    "Ok",
    "Err",
    "Result",
    # collections
    "collections",
    "Vec",
    # error.py
    "error",
    "Error",
    # boxed.py
    "boxed",
    "Box",
    # sync
    "sync",
    # maybe_uninit.py
    "maybe_uninit",
    # convert
    "convert",
    "From",
    "TryFrom",
    "Into",
    "TryInto",
    "ToString",
    # time
    "time",
    # misc
    "__version__",
    "__url__",
    "__author__",
    "__about__",
    "__license__",
)

from . import async_iter
from . import boxed
from . import collections
from . import convert
from . import default
from . import error
from . import futures
from . import iter
from . import macros
from . import maybe_uninit
from . import option
from . import result
from . import sync
from . import time
from ._misc import __about__
from ._misc import __author__
from ._misc import __license__
from ._misc import __url__
from ._misc import __version__
from .boxed import Box
from .cfg import cfg
from .cfg import cfg_attr
from .collections import Vec
from .convert import From
from .convert import Into
from .convert import ToString
from .convert import TryFrom
from .convert import TryInto
from .default import Default
from .error import Error
from .iter import Iter
from .iter import Iterator
from .macros import assert_eq
from .macros import assert_ne
from .macros import deprecated
from .macros import doc
from .macros import include_bytes
from .macros import include_str
from .macros import todo
from .macros import unimplemented
from .option import NOTHING
from .option import Option
from .option import Some
from .result import Err
from .result import Ok
from .result import Result
