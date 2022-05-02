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

__all__: typing.Tuple[str, ...] = ("cfg_attr", "cfg")

import functools
import inspect
import platform
import sys
import typing

# apperantly there're no stubs for this module?
import pkg_resources  # type: ignore[import]

_T_a = typing.TypeVar("_T_a", bound=typing.Callable[..., typing.Any])

_TARGET_OS = typing.Literal["linux", "win32", "darwin", "unix"]


def cfg_attr(
    *,
    requires_modules: typing.Optional[typing.Union[str, typing.Tuple[str, ...]]] = None,
    target_os: typing.Optional[_TARGET_OS] = None,
    python_version: typing.Optional[typing.Tuple[int, int, int]] = None,
) -> typing.Callable[[_T_a], _T_a]:
    """Configure a class, method or function to be checked for the given attributes.

    If one of the attributes returns False, An exception will be raised.

    Notes
    -----
    Target OS must be one of the following:
    * `linux`
    * `win32`
    * `darwin`
    * `unix`, which is assumed to be either linux or darwin.

    Examples
    --------
    ```py
    import sain

    @sain.cfg_attr(target_os = "win32")
    def windows_only():
        # Do stuff with Windows's API.
        ...

    @sain.cfg_attr(python_version = "3.10.0")
    class MyClass:

        @staticmethod
        @sain.cfg_attr(requires_modules = ("numpy", "pandas"))
        async def with_match() -> None:
            import numpy
            match numpy.random.rand(10):
                case ...:
                    ...
    ```

    Parameters
    ----------
    requires_modules : `str | tuple[str] | None`
        A string or tuple of strings of the required modules for the object to be ran.
    target_os : `str | None`
        The targeted operating system thats required for the object to be ran.
    python_version : `tuple[int, int, int] | None`
        The targeted Python version thats required for the object to be ran.

        Format must be `(3, 9, 5)`.

    Raises
    ------
    `RuntimeError`
        If either the target OS or Python version check fails.
    `ModuleNotFoundError`
        If the module check fails.
    """

    def decorator(callback: _T_a) -> _T_a:
        @functools.wraps(callback)
        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            checker = _AttrCheck(
                callback,
                requires_modules=requires_modules,
                target_os=target_os,
                python_version=python_version,
            )
            return checker(*args, **kwargs)

        return typing.cast(_T_a, wrapper)

    return decorator


def cfg(
    target_os: typing.Optional[_TARGET_OS] = None,
    requires_modules: typing.Optional[typing.Union[str, typing.Tuple[str, ...]]] = None,
    python_version: typing.Optional[typing.Tuple[int, int, int]] = None,
) -> bool:
    """A function that will run the code only if all predicate attributes returns `True`.

    The difference between this function and `cfg_attr` is that this function will not raise an exception.
    Instead it will return `False` if any of the attributes fails.

    Notes
    -----
    Target OS must be one of the following:
    * `linux`
    * `win32`
    * `darwin`
    * `unix`, which is assumed to be either linux or darwin.

    Example
    -------
    ```py
    import sain

    if sain.cfg(target_os = "win32"):
        print("Windows")
    elif sain.cfg(target_os = "linux", python_verion = (3, 8, 5)):
        print("Linux")
    else:
        print("MacOS")

    while sain.cfg(requires_modules=("hikari", "hikari-tanjun"), python_version = (3, 9, 0)):
        ...
    ```

    Parameters
    ----------
    requires_modules : `str | tuple[str] | None`
        A string or tuple of strings of the required modules for the object to be ran.
    target_os : `str | None`
        The targeted operating system thats required for the object to be ran.
    python_version : `tuple[int, int, int] | None`
        The targeted Python version thats required for the object to be ran.

        Format must be `(3, 9, 5)`.

    Returns
    -------
    `bool`
        The condition that was checked.
    """
    checker = _AttrCheck(
        lambda: None,
        requires_modules=requires_modules,
        target_os=target_os,
        python_version=python_version,
        no_raise=True,
    )
    return checker.cfg_check(requires_modules=requires_modules, target_os=target_os, python_version=python_version)


class _AttrCheck(typing.Generic[_T_a]):
    __slots__ = ("_requires_modules", "_target_os", "_callback", "_py_version", "_no_raise")

    def __init__(
        self,
        callback: _T_a,
        requires_modules: typing.Optional[typing.Union[str, typing.Tuple[str, ...]]] = None,
        target_os: typing.Optional[_TARGET_OS] = None,
        python_version: typing.Optional[typing.Tuple[int, int, int]] = None,
        *,
        no_raise: bool = False,
    ) -> None:
        self._callback = callback
        self._requires_modules = requires_modules
        self._target_os = target_os
        self._py_version = python_version
        self._no_raise = no_raise

    def __call__(self, *args: typing.Any, **kwds: typing.Any) -> _T_a:
        self._check_once()
        return typing.cast(_T_a, self._callback(*args, **kwds))

    def cfg_check(
        self,
        *,
        requires_modules: typing.Optional[typing.Union[str, typing.Tuple[str, ...]]] = None,
        target_os: typing.Optional[_TARGET_OS] = None,
        python_version: typing.Optional[typing.Tuple[int, int, int]] = None,
    ) -> bool:
        self._target_os = target_os
        self._py_version = python_version
        self._requires_modules = requires_modules

        return self._check_once()

    def _check_once(self) -> bool:
        if self._target_os is not None:
            self._check_platform()

        if self._py_version is not None:
            self._check_py_version()

        if self._requires_modules is not None:
            self._check_modules()

        return False

    def _check_modules(self) -> bool:
        required_modules: set[str] = set()

        assert self._requires_modules
        if isinstance(modules := self._requires_modules, str):
            modules = (modules,)

        for module in modules:
            try:
                pkg_resources.get_distribution(module)
                required_modules.add(module)
            except pkg_resources.DistributionNotFound:
                if self._no_raise:
                    return False
                else:
                    needed = (mod for mod in modules if mod not in required_modules)
                    raise ModuleNotFoundError(
                        self._output_str(
                            f"requires modules {', '.join(needed)} to be installed"
                        )
                    ) from None
        return True

    def _check_platform(self) -> bool:
        is_unix = sys.platform in {"linux", "darwin"}

        # If the target os is unix, then we assume that it's either linux or darwin.
        if self._target_os == "unix" and is_unix:
            return True

        if sys.platform == self._target_os:
            return True
        else:
            if self._no_raise:
                return False
            else:
                raise RuntimeError(self._output_str(f"requires {self._target_os} OS")) from None

    def _check_py_version(self) -> bool:
        if self._py_version and self._py_version <= sys.version_info:
            return True

        else:
            if self._no_raise:
                return False
            else:
                raise RuntimeError(
                    self._output_str(f"requires Python >={self._py_version}. But found {platform.python_version()}")
                ) from None

    def _obj_type(self) -> str:
        if inspect.isfunction(self._callback):
            return "function"
        elif inspect.isclass(self._callback):
            return "class"

        return "object"

    def _output_str(self, message: str, /) -> str:
        fn_name = "" if self._callback.__name__ == "<lambda>" else f"{self._callback.__name__} "
        return f"{self._obj_type()} {fn_name}{message}."
