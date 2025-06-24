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
"""Composable async iteration."""

from __future__ import annotations

__all__ = ("AsyncIterator", "Stream", "into_stream")

import abc
import typing
from collections import abc as collections

from sain.macros import rustc_diagnostic_item
from sain.macros import unstable
from sain.option import NOTHING
from sain.option import Some

T = typing.TypeVar("T", covariant=True)
Item = typing.TypeVar("Item")

if typing.TYPE_CHECKING:
    from typing_extensions import Self

    from sain.option import Option

    Poller: typing.TypeAlias = collections.AsyncIterable[T] | collections.Iterable[T]


@rustc_diagnostic_item("async_iterator")
@unstable(feature="async_iter", issue="257")
class AsyncIterator(typing.Generic[Item], abc.ABC):
    __slots__ = ()

    # Required methods
    @abc.abstractmethod
    async def poll_next(self) -> Option[Item]: ...
    @abc.abstractmethod
    async def __anext__(self) -> Item: ...

    # Provided methods

    def __aiter__(self) -> Self:
        return self

    async def __await__(self) -> collections.MutableSequence[Item]:
        return [item async for item in self]


@typing.final
@unstable(feature="async_iter", issue="257")
class Stream(AsyncIterator[Item]):
    __slots__ = ("_poller",)

    def __init__(self, iterable: Poller[Item]) -> None:
        self._poller = (
            iterable.__aiter__()
            if isinstance(iterable, collections.AsyncIterable)
            else iterable.__iter__()
        )

    async def poll_next(self) -> Option[Item]:
        try:
            fut = await self.__anext__()
        except (StopAsyncIteration, StopIteration):
            return NOTHING

        return Some(fut)

    async def __anext__(self) -> Item:
        if isinstance(self._poller, collections.AsyncIterable):
            return await anext(self._poller)
        else:
            try:
                return next(self._poller)
            except StopIteration:
                raise StopAsyncIteration


def into_stream(iterable: Poller[Item]) -> Stream[Item]:
    return Stream(iterable)
