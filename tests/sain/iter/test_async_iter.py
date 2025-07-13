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

from __future__ import annotations
from types import FunctionType

import pytest
from sain.async_iter import AsyncIterator, Stream, into_stream
from sain.option import Some


# FIXME: unstable API


def assert_warns_unstable(f: FunctionType):
    async def inner() -> None:
        with pytest.warns(RuntimeWarning):
            return await f()

    return inner


@pytest.mark.asyncio
@assert_warns_unstable
async def test_anext() -> None:
    it = Stream((1, 2, 3))
    assert await anext(it) == 1
    assert await anext(it) == 2
    assert await anext(it) == 3
    with pytest.raises(StopAsyncIteration):
        await anext(it)


@pytest.mark.asyncio
@assert_warns_unstable
async def test_poll_next() -> None:
    it = Stream({1.2, 2.3, 3.4, 4.5})

    while True:
        match await it.poll_next():
            case Some(x) if x:  # pyright: ignore - pyright cannot infer this ig.
                assert x in {1.2, 2.3, 3.4, 4.5}
            case _:
                break


@pytest.mark.asyncio
@assert_warns_unstable
async def test_aiter() -> None:
    async for i in into_stream((1, 2, 3)):
        assert i >= 1


@pytest.mark.asyncio
@assert_warns_unstable
async def test_await() -> None:
    items = into_stream(["a", "b", "c"])
    assert await items.__await__() == ["a", "b", "c"]


@pytest.mark.asyncio
@assert_warns_unstable
async def test_stream() -> None:
    stream: Stream[tuple[()]] = Stream(())
    assert isinstance(stream, AsyncIterator)

    async for _ in stream:
        pass

    assert (await stream.poll_next()).is_none()


@pytest.mark.asyncio
@assert_warns_unstable
async def test_into_stream() -> None:
    seq = [1, 2, 3]
    it = into_stream(seq)

    assert (await it.poll_next()).is_some_and(lambda x: x >= 1)
