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
import collections.abc

from sain.maybe_uninit import MaybeUninit


@pytest.fixture()
def uninit() -> MaybeUninit[None]:
    return MaybeUninit()


class TestMaybeUninit:
    @pytest.fixture()
    def uninit_array(self) -> collections.abc.Sequence[MaybeUninit[None]]:
        return MaybeUninit[None].uninit_array(3)

    def test_uninit_array_basic(self, uninit_array: list[MaybeUninit[None]]) -> None:
        assert len(uninit_array) == 3 and all(not _ for _ in uninit_array)

    def test_uninit_array_write(
        self, uninit_array: tuple[MaybeUninit[None], ...]
    ) -> None:
        for uninit in uninit_array:
            uninit.write(None)

        assert all(uninit.assume_init() is None for uninit in uninit_array)

    def test_uninit_is_uninitialized(self, uninit: MaybeUninit[None]) -> None:
        with pytest.raises(AttributeError):
            uninit.assume_init()

    def test_write(self, uninit: MaybeUninit[None]) -> None:
        uninit.write(None)
        assert uninit.assume_init() is None

    def test___bool__False(self, uninit: MaybeUninit[None]) -> None:
        assert not uninit

    def test___bool_True(self, uninit: MaybeUninit[None]) -> None:
        uninit.write(None)
        assert bool(uninit)

    def test___repr___when_initialized(self, uninit: MaybeUninit[None]) -> None:
        uninit.write(None)
        assert repr(uninit) == "MaybeUninit(value: None)"

    def test___repr___when_uninitialized(self, uninit: MaybeUninit[None]) -> None:
        assert repr(uninit) == "<uninit>"

    def test___eq___True(self, uninit: MaybeUninit[None]) -> None:
        uninit2 = MaybeUninit[None]()
        uninit2.write(None)
        uninit.write(None)
        assert uninit == uninit2

    def test__eq__False(self, uninit: MaybeUninit[None]) -> None:
        assert uninit != MaybeUninit(None)
