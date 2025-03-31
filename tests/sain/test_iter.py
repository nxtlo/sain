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

import pytest

from sain import iter


@pytest.fixture()
def default_iterator() -> iter.Iterator[str]:
    return iter.Iter[str].default()


class TestIterator:
    def test_default(self, default_iterator: iter.Iterator[str]):
        assert default_iterator.next().is_none()

    def test_collect_cast(self):
        it = iter.Iter(("a", "b", "c", "d"))
        assert it.collect(cast=str.encode) == (b"a", b"b", b"c", b"d")

    def test_collect(self):
        it = iter.Iter(("a", "b", "c", "d"))
        assert "a" in it.collect()

    def test_for_iter(self):
        it = iter.Iter(("a", "b", "c", "d"))
        for _ in it:
            pass

        assert it.next().is_none()

    def test_next(self):
        it = iter.Iter(("a", "b"))
        assert it.next().is_some_and(lambda x: x == "a")
        assert it.next().is_some_and(lambda x: x == "b")
        assert it.next().is_none()

    def test_to_vec(self):
        it = iter.Iter(("a", "b"))
        assert it.to_vec() == ["a", "b"]
