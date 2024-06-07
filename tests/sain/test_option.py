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
import typing

import pytest
from sain import Some
from sain.option import nothing_unchecked

if typing.TYPE_CHECKING:
    from sain import Option


class TestOption:
    @pytest.fixture()
    def opt(self) -> Option[int]:
        return Some(1)

    @pytest.fixture()
    def opt_none(self) -> Option[int]:
        return nothing_unchecked()

    def test_is_some(self, opt: Option[int]) -> None:
        assert opt.is_some()

    def test_is_none(self, opt: Option[int]) -> None:
        assert not opt.is_none()

    def test_is_some_and(self, opt: Option[int]) -> None:
        assert opt.is_some_and(lambda x: x > 0)

    def test_default(self, opt: Option[int]) -> None:
        assert opt.default() is None

    def test_into_inner(self, opt: Option[int]) -> None:
        assert opt.into_inner() == 1

    def test_unwrap_raises(self, opt_none: Option[int]) -> None:
        with pytest.raises(RuntimeError):
            opt_none.unwrap()

    def test_unwrap(self, opt: Option[int]) -> None:
        assert opt.unwrap() == 1

    def test_unwrap_or(self, opt: Option[int]) -> None:
        assert opt.unwrap_or(2) == 1

    def test_unwrap_or_when_none(self, opt_none: Option[int]) -> None:
        assert opt_none.unwrap_or(2) == 2

    def test_unwrap_or_else(self, opt: Option[int]) -> None:
        assert opt.unwrap_or_else(lambda: 2) == 1

    def test_unwrap_or_else_when_none(self, opt_none: Option[int]) -> None:
        assert opt_none.unwrap_or_else(lambda: 2) == 2

    def test_unwrap_unchecked(self, opt: Option[int]) -> None:
        assert opt.unwrap_unchecked() == 1

    def test_unwrap_unchecked_when_none(self, opt_none: Option[int]) -> None:
        assert not opt_none.unwrap_unchecked()

    def test_map(self, opt: Option[int]) -> None:
        assert opt.map(lambda x: x + 1) == Some(2)

    def test_map_none(self, opt_none: Option[int]) -> None:
        assert opt_none.map(lambda x: x + 1).is_none()

    def test_map_or(self, opt: Option[int]) -> None:
        assert opt.map_or(0, lambda x: x + 1) == 2

    def test_map_or_none(self, opt_none: Option[int]) -> None:
        assert opt_none.map_or(0, lambda x: x + 1) == 0

    def test_map_or_else(self, opt: Option[int]) -> None:
        assert opt.map_or_else(lambda: 0, lambda x: x + 1) == 2

    def test_map_or_else_none(self, opt_none: Option[int]) -> None:
        assert opt_none.map_or_else(lambda: 0, lambda x: x + 1) == 0

    def test_filter(self, opt: Option[int]) -> None:
        assert opt.filter(lambda x: x == 1) == Some(1)

    def test_filter_none(self, opt_none: Option[int]) -> None:
        assert opt_none.filter(lambda x: "0" == str(x)) == Some(None)

    def test_take(self, opt: Option[int]) -> None:
        assert opt.take() == Some(1)

    def test_take_if_when_true(self, opt: Option[int]) -> None:
        assert opt.take_if(lambda x: x == 1).is_some()

    def test_take_if_when_false(self, opt: Option[int]) -> None:
        assert opt.take_if(lambda x: x != 1).is_none()
