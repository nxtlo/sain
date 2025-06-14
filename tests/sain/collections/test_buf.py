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
import array
import io
from sain.collections.buf import Bytes, BytesMut


def test_bytes_from_empty_and_is_empty():
    b = Bytes()
    assert b.is_empty()
    assert b.len() == 0
    assert b.to_bytes() == b""
    assert list(b) == []


def test_bytes_from_raw_stringio_and_bytesio():
    s = io.StringIO("abc")
    b = Bytes.from_raw(s)
    assert b == b"abc"
    bio = io.BytesIO(b"xyz")
    b2 = Bytes.from_raw(bio)
    assert b2.to_bytes() == b"xyz"


def test_bytes_from_ptr_and_from_ptr_unchecked():
    arr = array.array("B", [10, 20, 30])
    b = Bytes.from_ptr(arr)
    assert b.to_bytes() == b"\x0a\x14\x1e"
    arr2 = array.array("B", [1, 2])
    b2 = Bytes.from_ptr_unchecked(arr2)
    assert b2.to_bytes() == b"\x01\x02"


def test_bytes_as_ptr_and_as_ref():
    b = Bytes.from_bytes([1, 2, 3])
    ptr = b.as_ptr()
    assert isinstance(ptr, memoryview)
    assert ptr.readonly
    ref = b.as_ref()
    assert list(ref) == [1, 2, 3]
    b_empty = Bytes()
    assert not b_empty.as_ref()


def test_bytes_leak_on_empty():
    b = Bytes()
    arr = b.leak()
    assert isinstance(arr, array.array)
    assert arr.tolist() == []


def test_bytes_access_leaked_bytes():
    b = Bytes.from_bytes([])
    arr = b.leak()
    assert len(arr) == 0

    with pytest.raises(AttributeError):
        b.to_bytes()


# FIXME: Remove on deprecation end.
def test_bytes_try_to_str_invalid_utf8():
    b = Bytes.from_bytes([0xFF, 0xFE])
    res = b.try_to_str()
    assert res.is_err()
    assert res.unwrap_err() == b"\xff\xfe"


def test_bytes_repr_and_str_empty():
    b = Bytes()
    assert repr(b) == "[]"
    assert str(b) == "[]"


def test_bytes_eq_and_ne_with_various_types():
    b = Bytes.from_bytes([1, 2, 3])
    assert b == [1, 2, 3]
    assert b == b"\x01\x02\x03"
    assert b != [1, 2]
    assert b != b"\x01\x02"


def test_bytes_ordering():
    b1 = Bytes.from_bytes([1, 2])
    b2 = Bytes.from_bytes([1, 2, 3])
    assert b1 < b2
    assert b2 > b1
    assert b1 <= b2
    assert b2 >= b1
    assert not (b1 > b2)
    assert not (b2 < b1)


def test_bytes_getitem_out_of_range():
    b = Bytes()
    with pytest.raises(IndexError):
        _ = b[0]


def test_bytes_slice_returns_bytes():
    b = Bytes.from_bytes([1, 2, 3, 4])
    s = b[1:3]
    assert isinstance(s, Bytes)
    assert s == [2, 3]


def test_bytes_hash_and_copy_deepcopy():
    import copy

    b = Bytes.from_bytes([1, 2, 3])
    with pytest.raises(TypeError):
        hash(b)

    b2 = copy.copy(b)
    b3 = copy.deepcopy(b)
    assert b2 == b and b3 == b
    assert b2 is not b and b3 is not b


def test_bytes_split_off_empty_and_invalid():
    b = Bytes()
    split = b.split_off(0)
    assert not split
    b2 = Bytes.from_bytes([1])
    with pytest.raises(RuntimeError):
        b2.split_off(2)


def test_bytes_split_first_last_empty():
    b = Bytes()
    assert b.split_first().is_none()
    assert b.split_last().is_none()


def test_bytes_split_at_bounds():
    b = Bytes.from_bytes([1, 2, 3])

    left, right = b.split_at(0)
    assert not left
    assert right == [1, 2, 3]

    left, right = b.split_at(3)
    assert left == [1, 2, 3]
    assert not right


def test_bytes_mut_as_mut_ptr_and_as_mut():
    bm = BytesMut.from_bytes([1, 2, 3])
    ptr = bm.as_mut_ptr()
    assert isinstance(ptr, memoryview)
    assert not ptr.readonly
    mut = bm.as_mut()
    assert list(mut) == [1, 2, 3]


def test_bytes_mut_freeze_and_to_mut_roundtrip():
    bm = BytesMut.from_bytes([1, 2])
    b = bm.freeze()
    assert isinstance(b, Bytes)
    bm2 = b.to_mut()
    assert isinstance(bm2, BytesMut)
    assert bm2 == [1, 2]


def test_bytes_mut_clear_and_is_empty():
    bm = BytesMut.from_bytes([1, 2])
    bm.clear()
    assert bm.is_empty()
    assert bm.to_bytes() == b""


def test_bytes_mut_remove_invalid():
    bm = BytesMut.from_bytes([1, 2])
    with pytest.raises(ValueError):
        bm.remove(99)


def test_bytes_mut_pop_empty():
    bm = BytesMut()
    val = bm.pop()
    assert val.is_none()


def test_bytes_mut_truncate_larger_than_len():
    bm = BytesMut.from_bytes([1, 2])
    bm.truncate(10)
    assert bm == [1, 2]


def test_bytes_mut_split_off_mut_invalid():
    bm = BytesMut.from_bytes([1])
    with pytest.raises(IndexError):
        bm.split_off_mut(2)


def test_bytes_mut_split_first_last_empty():
    bm = BytesMut()
    assert bm.split_first_mut().is_none()
    assert bm.split_last_mut().is_none()


def test_bytes_mut_split_at_mut_bounds():
    bm = BytesMut.from_bytes([1, 2, 3])

    left, right = bm.split_at_mut(0)
    assert not left
    assert right == [1, 2, 3]

    left, right = bm.split_at_mut(3)
    assert left == [1, 2, 3]
    assert not right


def test_bytes_mut_setitem_invalid_index():
    bm = BytesMut()
    with pytest.raises(IndexError):
        bm[0] = 1


def test_bytes_mut_delitem_invalid_index():
    bm = BytesMut()
    with pytest.raises(IndexError):
        del bm[0]


def test_bytes_mut_extend():
    bm = BytesMut()
    bm.extend([1, 2, 3])
    assert bm == [1, 2, 3]


def test_bytes_mut_put():
    bm = BytesMut()
    bm.put(4)
    assert bm == [4]

    with pytest.raises(OverflowError):
        bm.put(256)


def test_bytes_mut_put_float():
    bm = BytesMut()
    bm.put_float(1.2)
    assert bm.to_bytes() == b"\x3f\x99\x99\x9a"

    with pytest.raises(OverflowError):
        bm.put_float(3.5e38)


def test_bytes_mut_put_char():
    bm = BytesMut()
    bm.put_char("a")
    assert bm == b"a"

    with pytest.raises(AssertionError):
        bm.put_char("ab")


def test_bytes_mut_put_bytes_and_str():
    bm = BytesMut()
    bm.put_bytes(b"hello")
    bm.put_str(" world")
    assert bm == b"hello world"


def test_bytes_mut_replace_methods():
    bm = BytesMut.from_bytes([1, 2, 3])
    bm.replace(1, 4)
    assert bm == [1, 4, 3]

    bm.replace_with(1, lambda x: x * 2)
    assert bm == [1, 8, 3]


def test_bytes_mut_offset_and_fill():
    bm = BytesMut.from_bytes([1, 2, 3])
    bm.offset(lambda x: x * 2)
    assert bm == [2, 4, 6]

    bm.fill(0)
    assert bm == [0, 0, 0]

    bm.fill_with(lambda: 1)
    assert bm == [1, 1, 1]


def test_bytes_mut_swap_methods():
    bm = BytesMut.from_bytes([1, 2, 3, 4])
    bm.swap(0, 3)
    assert bm == [4, 2, 3, 1]

    bm.swap_unchecked(1, 2)
    assert bm == [4, 3, 2, 1]


def test_bytes_mut_modifications():
    bm = BytesMut.from_bytes([1, 2, 3, 4])
    bm.insert(1, 5)
    assert bm == [1, 5, 2, 3, 4]

    assert bm.pop().unwrap() == 4
    assert bm == [1, 5, 2, 3]

    bm.remove(5)
    assert bm == [1, 2, 3]


def test_bytes_mut_copy_and_clear():
    bm = BytesMut.from_bytes([1, 2, 3])
    copy = bm.copy()
    assert copy == bm
    assert copy is not bm

    bm.clear()
    assert bm.is_empty()
    assert copy == [1, 2, 3]


def test_bytes_mut_indexing():
    bm = BytesMut.from_bytes([1, 2, 3])
    assert bm[1] == 2

    bm[1] = 4
    assert bm == [1, 4, 3]

    del bm[1]
    assert bm == [1, 3]

    slice = bm[0:1]
    assert isinstance(slice, BytesMut)
    assert slice == [1]
