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

"""sain is a dependency-free Python library which brings the Rust ecosystem to Python, Allowing its users to write safe, idiomatic Python code just like Rust.

## What sain provides

If you already know what you are looking for, the fastest way is to use the search bar,

otherwise, you may want to jump into one of these useful sections:

* `collections` Implementations of the most common general purpose data structures from Rust's `std::collections` and friends such as `HashMap`, `Vec`.
* Core error-handling types such as `Option` and `Some` variant, `Result` and `Ok`, `Err` variants.
* The `Iterator` trait and its adapters.
* Common traits such as `From`, `Into`.
* Synchronization primitives, includes `LazyLock` and `Once`.
* Support macros such as `#[deprecated]`, `todo!()`, `unimplemented!()` and more.


## A Tour of sain

The next section will include the most general purpose and notable features of Rust implemented in sain.

### Containers and Collections

The [option](https://nxtlo.github.io/sain/sain/option.html) and [result](https://nxtlo.github.io/sain/sain/result.html) modules define optional and error-handling types,
[Option<T>](https://nxtlo.github.io/sain/sain/option.html#Some) and [Result<T, E>](https://nxtlo.github.io/sain/sain/result.html#Result).
The [iter](https://nxtlo.github.io/sain/sain/iter.html) module defines the [Iterator](https://nxtlo.github.io/sain/sain/iter.html#Iterator) trait.

For `std::collections` types, sain exposes `Vec` to the top level, which can be imported directly, as for the rest of the types,
they all exist under `sain.collections`, notable ones are:

* [Vec<T>](https://nxtlo.github.io/sain/sain/collections/vec.html#Vec) - Built on-top of a `list` object, contains all of Rust's `Vec<T>` methods.
* [HashMap<K, V>](https://nxtlo.github.io/sain/sain/collections/hash_map.html#HashMap) - Built on-top of a `dict` object, contains all of Rust's `HashMap<K, V` methods.
* [Bytes](https://nxtlo.github.io/sain/sain/collections/buf.html#Bytes) and [BytesMut](https://nxtlo.github.io/sain/sain/collections/buf.html#BytesMut) -
although these are not part of the standard library, it implements `bytes::Bytes`.
"""

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
