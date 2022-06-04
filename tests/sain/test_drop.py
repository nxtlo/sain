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

import pytest
import sain


class ImplDropMock(sain.Drop):
    def __init__(self) -> None:
        self.y = 100
        self.drop_state = False

    def drop(self) -> None:
        print("Dropping.")
        self.y = 0
        del self.y
        self.drop_state = True

    def on_drop(self) -> None:
        print("Dropped.")


def test_drop():
    d = ImplDropMock()
    d.drop()


class TestDrop:

    @pytest.fixture()
    def obj(self) -> ImplDropMock:
        return ImplDropMock()

    def test_drop(self, obj: ImplDropMock):
        assert obj.y == 100
        with pytest.raises(AttributeError):
            sain.drop(obj)
            assert obj.y

    def test_on_drop(self, obj: ImplDropMock):
        assert not obj.drop_state
        sain.drop(obj)
        assert obj.drop_state

    def test_isinstance_drop(self, obj: ImplDropMock):
        assert isinstance(obj, sain.Drop)
