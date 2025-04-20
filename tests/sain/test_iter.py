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
    def test___next__(self):
        it = iter.Iter(("a", "b"))
        assert next(it) == "a"
        assert next(it) == "b"
        with pytest.raises(StopIteration):
            assert next(it)

    def test_next(self):
        it = iter.Iter(("a", "b"))
        assert it.next().is_some_and(lambda x: x == "a")
        assert it.next().is_some_and(lambda x: x == "b")
        assert it.next().is_none()

    def test_default(self, default_iterator: iter.Iterator[str]):
        assert default_iterator.next().is_none()

    def test_collect_cast(self):
        it = iter.Iter(("a", "b", "c", "d"))
        assert it.collect(cast=str.encode) == (b"a", b"b", b"c", b"d")

    def test_collect(self):
        it = iter.Iter(("a", "b", "c", "d"))
        assert ("a", "b", "c", "d") == it.collect()

    def test_collect_into(self):
        values = iter.Iter([1, 2, 3, 3, 4, 5, 6, 7, 8, 4])
        uniques: set[int] = set()
        values.collect_into(uniques)
        assert uniques == {1, 2, 3, 4, 5, 6, 7, 8}

    def test_to_vec(self):
        it = iter.Iter(("a", "b"))
        assert it.to_vec() == ["a", "b"]

    def test_for_iter(self):
        it = iter.Iter(("a", "b", "c", "d"))
        for _ in it:
            pass

        assert it.next().is_none()

    def test_sink(self):
        it = iter.Iter(("a", "b", "c", "d"))
        assert it.sink() is None
        assert it.next().is_none()

    def test_raw_parts(self):
        it = iter.Iter(("b", "a", "w", "z"))
        raw = it.raw_parts()
        assert sorted(raw) == ["a", "b", "w", "z"]
        assert it.count() == 0

    def test_cloned(self):
        ref = [1, 2, 3]
        xs = iter.Iter([ref])
        # copies the reference to the list.
        it = xs.cloned()

        def _do(list_: list[int]) -> bool:
            list_.append(4)
            return list_[3] == 4

        assert it.next().is_some_and(_do)

    def test_copied(self):
        ref = [1, 2, 3]
        xs = iter.Iter([ref])
        # deep copies the list.
        it = xs.copied()
        it.first().unwrap().append(4)
        assert ref == [1, 2, 3]

    def test_map(self):
        it = iter.Iter([1, 2, 3])
        assert it.map(lambda x: x + 1).collect() == (2, 3, 4)

    def test_filter(self):
        it = iter.Iter([1, 2, 3, 4, 5])
        filtered = it.filter(lambda x: x % 2 == 0)
        assert filtered.collect() == (2, 4)

    def test_take(self):
        it = iter.Iter([1, 2, 3, 4, 5])
        taken = it.take(3)
        assert taken.collect() == (1, 2, 3)

    def test_skip(self):
        it = iter.Iter([1, 2, 3, 4, 5])
        skipped = it.skip(2)
        assert skipped.collect() == (3, 4, 5)

    def test_enumerate(self):
        it = iter.Iter(["a", "b", "c"])
        enumerated = it.enumerate(start=1)
        assert enumerated.collect() == ((1, "a"), (2, "b"), (3, "c"))

    def test_take_while(self):
        it = iter.Iter([1, 2, 3, 4, 5])
        taken = it.take_while(lambda x: x < 4)
        assert taken.collect() == (1, 2, 3)

    def test_drop_while(self):
        it = iter.Iter([1, 2, 3, 4, 5])
        dropped = it.drop_while(lambda x: x < 3)
        assert dropped.collect() == (1,)

    def test_chunks(self):
        it = iter.Iter([1, 2, 3, 4, 5])
        chunks = it.chunks(2)
        assert chunks.collect() == ([1, 2], [3, 4], [5])

    def test_all(self):
        it = iter.Iter([2, 4, 6])
        assert it.all(lambda x: x % 2 == 0)

    def test_any(self):
        it = iter.Iter([1, 3, 5])
        assert it.any(lambda x: x % 2 == 0) is False

    def test_zip(self):
        it1 = iter.Iter([1, 2, 3])
        it2 = [4, 5, 6]
        zipped = it1.zip(it2)
        assert zipped.collect() == ((1, 4), (2, 5), (3, 6))

    def test_sort(self):
        it = iter.Iter([3, 1, 4, 2])
        sorted_it = it.sort(key=lambda x: x)
        assert sorted_it.collect() == (1, 2, 3, 4)

    def test_reversed(self):
        it = iter.Iter([1, 2, 3])
        reversed_it = it.reversed()
        assert reversed_it.collect() == (3, 2, 1)

    def test_union(self):
        it1 = iter.Iter([1, 2, 3])
        it2 = [4, 5, 6]
        union_it = it1.union(it2)
        assert union_it.collect() == (1, 2, 3, 4, 5, 6)

    def test_first(self):
        it = iter.Iter([1, 2, 3])
        assert it.first().unwrap() == 1

    def test_last(self):
        it = iter.Iter([1, 2, 3])
        assert it.last().unwrap() == 3

    def test_count(self):
        it = iter.Iter([1, 2, 3])
        assert it.count() == 3

    def test_find(self):
        it = iter.Iter([1, 2, 3, 4])
        assert it.find(lambda x: x > 2).unwrap() == 3

    def test_position(self):
        it = iter.Iter([1, 2, 3, 4])
        assert it.position(lambda x: x > 2).unwrap() == 2

    def test_fold(self):
        it = iter.Iter([1, 2, 3, 4])
        result = it.fold(0, lambda acc, x: acc + x)
        assert result == 10

    def test_sum(self):
        it = iter.Iter(["1", "2", "3"])
        assert it.sum() == 6

    def test_for_each(self):
        it = iter.Iter([1, 2, 3])
        result = []
        it.for_each(lambda x: result.append(x))
        assert result == [1, 2, 3]

    def test__copy__(self):
        import copy

        it = iter.Iter([1, 2, 3])
        it2 = copy.copy(it)
        assert isinstance(it2, iter.Cloned)

    def test__deepcopy__(self):
        import copy

        it = iter.Iter([1, 2, 3])
        it2 = copy.deepcopy(it)
        assert isinstance(it2, iter.Copied)

    def test___reversed__(self):
        it = iter.Iter([1, 2, 3])
        x = reversed(it)
        assert isinstance(x, iter.Iter) and x.collect() == (3, 2, 1)

    def test___len__(self):
        it = iter.Iter([1, 2, 3])
        assert len(it) == 3
        assert len(it) == 0


def test_empty_iter():
    it = iter.empty()
    assert it.next().is_none()
    assert it.len() == 0
    assert it.collect() == ()


def test_repeat_iter():
    it = iter.repeat(1, 3)
    assert it.next().is_some_and(lambda x: x == 1)
    assert it.next().is_some_and(lambda x: x == 1)
    assert it.next().is_some_and(lambda x: x == 1)
    assert it.next().is_none()
    assert it.len() == 0
    assert it.collect() == ()


def test_repeat_iter_spec():
    ref = [1, 2, 3]
    it = iter.repeat(ref, 3)
    assert it.next().is_some_and(lambda x: len(x) == len(ref))
    it.next()
    last = it.next().unwrap()
    last.append(4)
    assert last == ref
    assert it.next().is_none()


def test_once_iter():
    it = iter.once(1)
    assert it.len() == 1
    assert it.next().is_some_and(lambda x: x == 1)
    assert it.len() == 0


def test_into_iter_trusted():
    it = iter.into_iter([1, 2, 3])
    assert isinstance(it, iter.TrustedIter)
    assert it.next().is_some_and(lambda x: x == 1)
    assert it.next().is_some_and(lambda x: x == 2)
    assert it.next().is_some_and(lambda x: x == 3)
    assert it.next().is_none()
    assert it.collect() == ()


def test_into_iter():
    it = iter.into_iter(_ for _ in (0, 1, 2, 3))
    assert it.next().is_some_and(lambda x: x == 0)
    assert it.next().is_some_and(lambda x: x == 1)
    assert it.next().is_some_and(lambda x: x == 2)
    assert it.next().is_some_and(lambda x: x == 3)
    assert it.next().is_none()
    assert it.collect() == ()
