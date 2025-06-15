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
from sain.collections.hash_map import HashMap, RefMut


class TestHashMap:
    def test_from_keys(self):
        tier_list = [("S", "Top tier"), ("A", "Very Good"), ("B", "Good")]
        mapping = HashMap[str, str].from_keys(*tier_list)
        assert mapping == {"S": "Top tier", "A": "Very Good", "B": "Good"}

    def test_from_keys_mut(self):
        tier_list = [("S", "Top tier"), ("A", "Very Good"), ("B", "Good")]
        mapping = HashMap[str, str].from_keys_mut(*tier_list)
        assert mapping == {"S": "Top tier", "A": "Very Good", "B": "Good"}

    def test_from_mut(self):
        map = HashMap[int, str].from_mut({0: "buh"})
        assert map == {0: "buh"}
        map[0] = "new"
        assert map == {0: "new"}

    def test_from_value(self):
        values = [("a", 1), ("b", 2)]
        map1 = HashMap[str, int].from_value(values)
        assert map1 == {"a": 1, "b": 2}

    def test_default(self):
        map1 = HashMap[int, int].default()
        assert len(map1) == 0

    def test_into(self):
        users = [(0, "user-0"), (1, "user-1")]
        map1 = HashMap[int, str].from_keys(*users)
        assert map1.into() == users

    def test_into_keys(self):
        map1 = HashMap({"a": 1, "b": 2, "c": 3})
        keys = map1.into_keys().collect()
        assert keys == ["a", "b", "c"]

    def test_into_values(self):
        map1 = HashMap({"a": 1, "b": 2, "c": 3})
        values = map1.into_values().collect()
        assert values == [1, 2, 3]

    def test_contains_key(self):
        users = HashMap({0: "user-0"})
        assert users.contains_key(0) is True
        assert 0 in users

    def test_is_empty(self):
        storage: HashMap[int, int] = HashMap()
        assert storage.is_empty()
        assert not storage

    def test_get(self):
        users: HashMap[str, float] = HashMap()
        assert users.get("jack").is_none()
        users = HashMap({"jack": 3.14})
        assert users.get("jack").is_some()

    def test_get_with(self):
        def get_id() -> int:
            return 0

        map = HashMap({0: "buh", 1: "guh", 2: "luh"})
        assert map.get_with(get_id).unwrap() == "buh"

    def test_get_pairs(self):
        users: HashMap[str, int] = HashMap()
        assert users.get_pairs("jack").is_none()
        users = HashMap({"jack": 0})
        assert users.get_pairs("jack").unwrap() == ("jack", 0)

    def test_get_many(self):
        urls = HashMap(
            {
                "google": "www.google.com",
                "github": "www.github.com",
                "facebook": "www.facebook.com",
            }
        )
        assert urls.get_many("google", "github").unwrap() == [
            "www.google.com",
            "www.github.com",
        ]
        assert urls.get_many("google", "missing").is_none()
        assert urls.get_many("google", "google").is_none()

    def test_iter(self):
        map = HashMap({0: "buh", 1: "guh", 2: "luh"})
        assert map.iter().map(lambda x: x[0]).collect() == [0, 1, 2]

    def test_into_iter(self):
        map = HashMap({0: "buh", 1: "guh", 2: "luh"})
        assert map.into_iter().map(lambda x: x[0]).collect() == [0, 1, 2]

        with pytest.raises(AttributeError):
            map.len()

    def test_len(self):
        map = HashMap({0: "buh", 1: "guh", 2: "luh"})
        assert len(map) == 3

    def test_copy(self):
        hashmap = HashMap({"1": None, "2": None})
        copy = hashmap.copy()
        assert hashmap == copy

    def test_leak(self):
        map = HashMap({0: "buh", 1: "guh", 2: "luh"})
        assert map.leak() == {0: "buh", 1: "guh", 2: "luh"}
        with pytest.raises(AttributeError):
            map.len()

    def test_as_mut(self):
        map = HashMap({0: "buh", 1: "guh", 2: "luh"})
        mut = map.as_mut()
        mut.insert(3, "new")
        assert map == {0: "buh", 1: "guh", 2: "luh", 3: "new"}

    def test_immutable(self):
        map1 = HashMap({"test": "value"})

        with pytest.raises(NotImplementedError):
            map1["new"] = "value"  # pyright: ignore

        with pytest.raises(NotImplementedError):
            del map1["test"]  # pyright: ignore

    def test_delitem(self):
        map = HashMap({0: "buh", 1: "guh", 2: "luh"})
        with pytest.raises(NotImplementedError):
            del map[0]  # pyright: ignore

    def test_setitem(self):
        map = HashMap({0: "buh", 1: "guh", 2: "luh"})
        with pytest.raises(NotImplementedError):
            map[0] = "new"  # pyright: ignore

    def test_getitem(self):
        map = HashMap({0: "buh", 1: "guh", 2: "luh"})
        assert map[0] == "buh"

    def test_repr(self):
        map = HashMap({0: "buh", 1: "guh", 2: "luh"})
        assert repr(map) == "{0: 'buh', 1: 'guh', 2: 'luh'}"

    def test_builtin_iter(self):
        map = HashMap({0: "buh", 1: "guh", 2: "luh"})
        assert list(map.__iter__()) == [0, 1, 2]


class TestRefMut:
    @pytest.fixture
    def mut_map(self) -> RefMut[int, str]:
        return HashMap[int, str].from_mut({0: "admin"})

    def test_default(self):
        map1 = RefMut[int, int].default()
        assert len(map1) == 0

    def test_insert(self, mut_map: RefMut[int, str]):
        assert mut_map.insert(1, "user").is_none()
        old = mut_map.insert(0, "normal").unwrap()
        assert old == "admin"

    def test_try_insert(self, mut_map: RefMut[int, str]):
        assert mut_map.try_insert(1, "claudia").is_ok()
        assert mut_map.try_insert(0, "doppler").is_err()

    def test_remove(self, mut_map: RefMut[int, str]):
        assert mut_map.remove(0).unwrap() == "admin"
        assert mut_map.remove(0).is_none()

    def test_remove_entry(self, mut_map: RefMut[int, str]):
        assert mut_map.remove_entry(0).unwrap() == (0, "admin")
        assert mut_map.remove_entry(0).is_none()

    def test_drain(self, mut_map: RefMut[int, str]):
        items = mut_map.drain().collect()
        assert items == [(0, "admin")]
        assert mut_map.is_empty()

    def test_retain(self):
        users = RefMut(
            {"user1": "admin", "user2": "admin", "user3": "regular", "jack": "admin"}
        )
        users.retain(lambda user, role: role == "admin" and user.startswith("user"))
        assert users == {"user1": "admin", "user2": "admin"}

    def test_extract_if(self):
        nums = RefMut({0: 0, 1: 1, 2: 2, 3: 3, 4: 4})
        evens = nums.extract_if(lambda k, _v: k % 2 == 0).collect()
        assert nums == {1: 1, 3: 3}
        assert evens == [(0, 0), (2, 2), (4, 4)]

    def test_setitem(self, mut_map: RefMut[int, str]):
        mut_map[3] = "new"
        assert 3 in mut_map
