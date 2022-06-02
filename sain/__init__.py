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

Equavilant types
----------------
- `Option<T>` -> `sain.Some[T]`
- `Result<T, E>` -> `sain.Result[T, E`. Not implemented yet.
- Default<T> -> `sain.Default[T]`
- AsRef<T> -> `sain.Ref[T]`. kinda...
- Iter<Item> -> `sain.

Equavilant macros
-----------------
- `cfg!()` -> `sain.cfg`.
- `#[cfg_attr]` -> `sain.cfg_attr`.

Examples
--------
```py
import sain

# If a non windows machine runs this function, it will raise an error.
@sain.cfg_attr(target_os = "win32")
def windows_only() -> sain.Some[int]:
    return sain.Some(1)

@sain.cfg_attr(requires_modules="uvloop", target_os = "unix")
def run_uvloop() -> None:
    windows_only().expect("Never.)  # RuntimeError("Never")

    import uvloop
    uvloop.install()

@sain.cfg_attr(python_version = (3, 5, 0))
class Foo:
    @staticmethod
    @sain.cfg_attr(requires_modules = ("numpy", "pandas"))
    async def bar() -> None:
        import numpy
        print(numpy.random.rand(10))
```

Notes
-----
Target OS must be one of the following:
* `linux`
* `win32`
* `darwin`
* `unix`, which is assumed to be either linux or darwin.

Target architecture must be one of the following:
* `x86`
* `x64`
* `arm`
* `arm64`

Target Python implementation must be one of the following:
* `CPython`
* `PyPy`
* `IronPython`
* `Jython`
"""
from __future__ import annotations

__all__ = ("cfg", "cfg_attr", "Default", "Ref", "Some", "into_iter", "Iter")

from .cfg import cfg
from .cfg import cfg_attr
from .deafult import Default
from .iter import Iter
from .iter import into_iter
from .option import Some
from .ref import Ref

__version__: str = "0.0.1"
__url__: str = "https://github.com/nxtlo/sain"
__author__: str = "nxtlo"
__about__: str = "A Rust like cfg attribs checking for Python."
__docs__: str = ""
__license__: str = "BSD 3-Clause License"
