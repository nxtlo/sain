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

from collections.abc import MutableSequence, Sequence
from sain.collections.slice import Slice, SliceMut
from sain.collections.vec import Vec


def test_vec_init_empty():
    v = Vec()
    assert v.len() == 0
    assert v.is_empty()


def test_vec_init_from_list():
    data = [1, 2, 3]
    v = Vec(data)
    assert v.len() == 3
    assert v == data
    data.append(4)
    assert v[-1] == 4


def test_vec_init_from_iterable():
    v = Vec((1, 2, 3))
    assert v.len() == 3
    assert v == [1, 2, 3]


def test_vec_push_and_append():
    v = Vec()
    v.push(10)
    v.append(20)
    assert v == [10, 20]


def test_vec_with_capacity_and_push_within_capacity():
    v = Vec.with_capacity(2)
    assert v.capacity() == 2
    assert v.push_within_capacity(1).is_ok()
    assert v.push_within_capacity(2).is_ok()
    res = v.push_within_capacity(3)
    assert res.is_err()
    assert v.len() == 2


def test_vec_extend_and_clear():
    v = Vec([1])
    v.extend([2, 3])
    assert v == [1, 2, 3]
    v.clear()
    assert v.len() == 0
    assert v.is_empty()


def test_vec_as_slice():
    v = Vec([1, 2, 3])
    ref = v.as_slice()
    assert ref == [1, 2, 3]

    v2 = v.copy()
    v2.push(4)
    assert v.len() == 3
    assert v2.len() == 4


def test_vec_first_last_get():
    v = Vec([10, 20, 30])
    assert v.first().unwrap() == 10
    assert v.last().unwrap() == 30
    assert v.get(1).unwrap() == 20
    assert v.get(10).is_none()


def test_vec_pop_and_pop_if():
    v = Vec([1, 2, 3])
    assert v.pop().unwrap() == 3
    assert v.pop_if(lambda x: x == 2).unwrap() == 2
    assert v.pop_if(lambda x: False).is_none()
    v.clear()
    assert v.pop().is_none()


def test_vec_remove_and_swap_remove():
    v = Vec(["a", "b", "c"])
    v.remove("b")
    assert v == ["a", "c"]
    v.push("d")
    removed = v.swap_remove("a")
    assert removed == "a"
    assert "a" not in v


def test_vec_truncate_and_fill():
    v = Vec([1, 2, 3, 4])
    v.truncate(2)
    assert v == [1, 2]
    v.fill(9)
    assert v == [9, 9]


def test_vec_split_off():
    v = Vec([1, 2, 3, 4])
    split = v.split_off(2)
    assert v == [1, 2]
    assert split == [3, 4]


def test_vec_split_first_last():
    v = Vec([1, 2, 3])
    first, rest = v.split_first().unwrap()
    assert first == 1
    assert rest == [2, 3]
    last, rest = v.split_last().unwrap()
    assert last == 3
    assert rest == [1, 2]
    empty = Vec()
    assert empty.split_first().is_none()
    assert empty.split_last().is_none()


def test_vec_split_at():
    v = Vec([1, 2, 3, 4])
    left, right = v.split_at(2)
    assert left == [1, 2]
    assert right == [3, 4]


def test_vec_swap_and_swap_unchecked():
    v = Vec([1, 2, 3, 4])
    v.swap(0, 3)
    assert v == [4, 2, 3, 1]
    v.swap_unchecked(1, 2)
    assert v == [4, 3, 2, 1]


def test_vec_retain():
    v = Vec([1, 2, 3, 4])
    v.retain(lambda x: x % 2 == 0)
    # Should keep only even numbers
    assert v == [2, 4]


def test_vec_dedup():
    v = Vec([1, 2, 2, 3, 1])
    v.dedup()
    assert v == [1, 2, 3, 1]


def test_vec_sort():
    v = Vec([3, 1, 2])
    v.sort()
    assert v == [1, 2, 3]
    v.sort(reverse=True)
    assert v == [3, 2, 1]


def test_vec_capacity_reserve_shrink():
    v = Vec.with_capacity(5)
    assert v.capacity() == 5
    v.reserve(3)
    assert v.capacity() == 8
    v.shrink_to_fit()
    assert v.capacity() == 0 or v.capacity() == v.len()


def test_vec_comparison():
    v = Vec([1, 2, 3])
    assert v == [1, 2, 3]
    assert not (v == (1, 2, 3))


def test_vec_isinstance():
    v = Vec([1, 2, 3])
    assert isinstance(v.as_ptr(), list)
    assert isinstance(
        v,
        (
            Sequence,
            MutableSequence,
            Slice,
            SliceMut,
        ),
    )
