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
"""Interfaces for working with Errors.

This exposes one abstract interface, `Error` that other errors can implement and use as an argument to match upon.

Usually this error is returned from a `Result[T, Error]` object.

Those errors can be converted into `RuntimeError`s by calling `sain.Err.unwrap` and `sain.Option.unwrap`.

For an example
```py
# Read the env variable, raises RuntimeError if it is not present.
path: Option[str] = Some(os.environ.get('SOME_PATH')).unwrap()

# Implementing an environment getter with `Error`.

TODO
```
"""
from __future__ import annotations

__all__ = ("Error",)

import typing

from . import option as _option


@typing.runtime_checkable
class Error(typing.Protocol):
    """`Error` is an interface usually used for values that returns `sain.Result[T, E]` where `E` is an implementation of this interface."""

    __slots__ = ()

    def source(self) -> _option.Option[type[Error]]:
        """The source of this error, if any.

        Example
        -------
        ```py
        TODO
        ```
        """
        return _option.nothing_unchecked()

    def description(self) -> str:
        """Context for this error."""
        return ""
