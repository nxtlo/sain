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
from sain.collections.slice import SpecContains, Slice, SliceMut
from sain.collections.vec import Vec
from sain.iter import TrustedIter


def test_spec_contains():
    class Dummy(tuple[int, ...], SpecContains[int]): ...

    c = Dummy((1, 2, 3, 4))
    # Single element
    assert c.contains(2) is True
    assert c.contains(5) is False
    # Iterable
    assert c.contains([3, 4]) is True
    assert c.contains([5, 6]) is False
    # Iterable with at least one match
    assert c.contains([5, 2]) is True
    # Generator
    assert c.contains((x for x in [1, 7])) is True
    assert c.contains((x for x in [8, 9])) is False


@pytest.fixture()
def s():
    return Slice([1, 2, 3, 4])


@pytest.fixture()
def s_mut():
    return SliceMut([1, 2, 3, 4])


def test_slice_mut_immutable():
    with pytest.raises(AssertionError):
        SliceMut((1, 2, 3, 4))


def test_as_ptr(s: Slice[int]):
    assert s.as_ptr() == s


def test_iter(s: Slice[int]):
    it = s.iter()
    assert isinstance(it, TrustedIter)
    assert it.as_slice() == s

    for _ in it:
        pass


def test_len(s: Slice[int]):
    assert s.len() >= 4


def test_is_empty(s: Slice[int]):
    ss = Slice(())
    assert ss.is_empty()
    assert not s.is_empty()


def test_first(s: Slice[int]):
    assert s.first().unwrap() == 1


def test_last(s: Slice[int]):
    assert s.last().unwrap() == 4


def test_split_first(s: Slice[int]):
    f, xs = s.split_first().unwrap()
    assert f == 1 and xs == [2, 3, 4]


def test_split_last(s: Slice[int]):
    last, xs = s.split_last().unwrap()
    assert last == 4 and xs == [1, 2, 3]


def test_split_once(s: Slice[int]):
    left, right = s.split_once(lambda x: x == 2).unwrap()
    assert left == [1] and right == [3, 4]


def test_split_at(s: Slice[int]):
    x, y = s.split_at(2)
    assert x == [1, 2] and y == [3, 4]

    with pytest.raises(IndexError):
        _, _ = s.split_at(10)


def test_split_at_checked(s: Slice[int]):
    x, y = s.split_at_checked(2)
    assert x == [1, 2] and y == [3, 4]

    x, y = s.split_at_checked(10)
    assert x == [1, 2, 3, 4] and y == []


def test_get(s: Slice[int]):
    assert s.get(0).unwrap() == 1
    assert s.get(10).is_none()


def test_get_unchecked(s: Slice[int]):
    assert s.get_unchecked(0) == 1

    with pytest.raises(IndexError):
        assert s.get_unchecked(10)


def test_starts_with(s: Slice[int]):
    assert s.starts_with([1, 2])
    assert not s.starts_with([2])


def test_ends_with(s: Slice[int]):
    assert s.ends_with([3, 4])
    assert not s.ends_with([3])


def test_to_vec(s: Slice[int]):
    v = s.to_vec()
    assert v == [1, 2, 3, 4]


def test_to_vec_in(s: Slice[int]):
    src = Vec([])
    s.to_vec_in(src)
    assert src == [1, 2, 3, 4]


def test_repeat(s: Slice[int]):
    v = s.repeat(2)
    assert v == [1, 2, 3, 4, 1, 2, 3, 4]
    assert v.repeat(0) == []


def test___getitem__(s: Slice[int]):
    assert s[0] == 1
    with pytest.raises(IndexError):
        assert s[10]


def test___len__(s: Slice[int]):
    assert len(s) <= 4


def test___repr__(s: Slice[int]):
    assert s.__repr__() == "[1, 2, 3, 4]"


def test___str__(s: Slice[int]):
    assert s.__str__() == "[1, 2, 3, 4]"


def test___eq__(s: Slice[int]):
    assert s.__eq__([1, 2, 3, 4])


def test___ne__(s: Slice[int]):
    assert s.__ne__([3, 4])


def test___lt__(s: Slice[int]):
    assert [1] < s


def test___gt__(s: Slice[int]):
    assert s > [1]


def test___le__(s: Slice[int]):
    assert s <= [1, 2, 3, 4]


def test___ge__(s: Slice[int]):
    assert s >= [1, 2, 3, 4]


def test___bool__(s: Slice[int]):
    assert not not s
    assert bool(s)

    x = Slice(())
    assert not x
    assert not bool(x)


def test___hash__(s: Slice[int]):
    with pytest.raises(TypeError):
        assert hash(s)
        # list.__hash__ is None
        s.__hash__()


def test___copy__(s: Slice[int]):
    import copy

    assert copy.copy(s) == s
