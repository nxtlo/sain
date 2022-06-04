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

import sain
import sys as _sys
import pytest
from unittest import mock
from sain.cfg import _AttrCheck


def _name():
    return _sys.platform


def _set(name: str):
    _sys.platform = name


def test_cfg_attr():
    mock_callback = mock.Mock(return_value=_AttrCheck, impl="CPython", python_version=(3, 8, 0))
    attr = sain.cfg_attr(impl="CPython", python_version=(3, 8, 0))(mock_callback)
    assert attr.impl == "CPython"
    assert attr.python_version == (3, 8, 0)


def test_cfg():
    # Hack
    old = _name()
    _set("linux")
    cfg = sain.cfg(target_os="unix")
    assert cfg
    _set(old)


del test_cfg


@sain.cfg_attr(target_os="win32")
def _only_windows():
    return -1


class Test_AttrCheck:
    @pytest.fixture()
    def attr(self):
        def _d():
            return 0
        return _AttrCheck(
            callback=_d,
            requires_modules=["six"],
            impl="CPython",
            target_os="win32",
            python_version=(3, 8, 0)
        )

    def test__check_once(self, attr):
        assert attr._check_once()

    def test__check_platform_when_wrong(self, attr):
        old = _name()
        _set("darwin")
        attr._target_os = "darwin"

        with pytest.raises(RuntimeError, match="requires win32 OS"):
            _only_windows()

        _set(old)

    def test__check_platform_ok(self, attr):
        attr._target_os = "win32"
        assert _only_windows() == -1

    def test__check_modules(self, attr):
        modules = ["xqc", "GAMBA"]
        mock_callback = sain.cfg_attr(requires_modules=modules)(lambda: ...)
        attr._callback = mock_callback
        attr._requires_modules = modules

        with pytest.raises(ModuleNotFoundError, match="xqc, GAMBA"):
            attr._check_once()

    def test__check_modules_ok(self, attr):
        mock_callback = sain.cfg_attr(requires_modules="six")(lambda: ...)
        attr._callback = mock_callback

        assert attr._check_modules()

    def test__check_python_version(self):
        @sain.cfg_attr(python_version=(3, 11, 0))
        def _stub():
            ...

        with pytest.raises(RuntimeError, match="requires Python"):
            _stub()

    def test__check_python_version_ok(self, attr):
        mock_callback = sain.cfg_attr(python_version=(3, 8, 0))(lambda: ...)
        attr._callback = mock_callback

        assert attr._check_py_version()

    def test__check_py_impl(self):
        @sain.cfg_attr(impl="PyPy")
        def _stub():
            ...

        with pytest.raises(RuntimeError):
            _stub()
