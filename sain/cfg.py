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
"""Runtime attr configuration.

Notes
-----
Target OS must be one of the following:
* `linux`
* `win32` | `windows`
* `darwin` | `macos`
* `ios`
* `unix`, which is assumed to be either linux or darwin.

Target architecture must be one of the following:
* `x86`
* `x86_64`
* `arm`
* `arm64`

Target Python implementation must be one of the following:
* `CPython`
* `PyPy`
* `IronPython`
* `Jython`
"""

from __future__ import annotations

__all__ = ("cfg_attr", "cfg")

import collections.abc as collections
import functools
import inspect
import platform
import sys
import typing


F = typing.TypeVar("F", bound=collections.Callable[..., object])

System = typing.Literal["linux", "win32", "darwin", "macos", "unix", "windows", "ios"]
Arch = typing.Literal["x86", "x86_64", "arm", "arm64"]
Python = typing.Literal["CPython", "PyPy", "IronPython", "Jython"]

if typing.TYPE_CHECKING:
    from typing_extensions import Self


_machine = platform.machine()


def _is_arm() -> bool:
    return "arm" in _machine


def _is_arm_64() -> bool:
    return "arm" in _machine and _machine.endswith("64")


def _is_x86_64() -> bool:
    return _machine == "AMD64" or _machine == "x86_64"


def _is_x86() -> bool:
    return _machine == "i386" or _machine == "x86"


def _py_version() -> str:
    return platform.python_version()


def cfg_attr(
    *,
    target_os: System | None = None,
    python_version: tuple[int, int, int] | None = None,
    target_arch: Arch | None = None,
    impl: Python | None = None,
) -> collections.Callable[[F], F]:
    """Conditional runtime object configuration based on passed arguments.

    If the decorated object gets called and one of the attributes returns `False`,
    `RuntimeError` will be raised and the object will not run.

    Example
    -------
    ```py
    import sain

    @cfg_attr(target_os="windows")
    def windows_only():
        # Do stuff with Windows's API.
        ...

    # Mut be PyPy Python implementation or `RuntimeError` will be raised
    # when creating the instance.
    @cfg_attr(impl="PyPy")
    class Zoo:
        @sain.cfg_attr(target_os="linux")
        def bark(self) -> None:
            windows_only()  # RuntimeError("Windows OS only!)

    # An instance will not be created if raised.
    zoo = Zoo()
    # RuntimeError("class Zoo requires PyPy implementation")
    zoo.bark()
    # Whats zoo??
    ```

    Parameters
    ----------
    target_os : `str | None`
        The targeted operating system thats required for the object.
    python_version : `tuple[int, int, int] | None`
        The targeted Python version thats required for the object. Format must be `(3, 9, 5)`.
    target_arch : `str | None`
        The CPU targeted architecture thats required for the object.
    impl : `str | None`
        The Python implementation thats required for the object.

    Raises
    ------
    `RuntimeError`
        This fails if any of the attributes returns `False`.
    `ValueError`
        If the passed Python implementation is unknown.
    """

    def decorator(callback: F) -> F:
        @functools.wraps(callback)
        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> F:
            checker = _AttrCheck(
                callback,
                target_os=target_os,
                python_version=python_version,
                target_arch=target_arch,
                impl=impl,
            )
            return checker(*args, **kwargs)

        return typing.cast(F, wrapper)

    return decorator


def cfg(
    target_os: System | None = None,
    python_version: tuple[int, int, int] | None = None,
    target_arch: Arch | None = None,
    impl: Python | None = None,
) -> bool:
    """A function that will run the code only if all predicate attributes returns `True`.

    The difference between this function and `cfg_attr` is that this function will not raise an exception.
    Instead it will return `False` if any of the attributes fails.

    Example
    -------
    ```py
    import sain

    if cfg(target_os="windows"):
        print("Windows")
    elif cfg(target_os="linux", target_arch="arm64"):
        print("Linux")
    else:
        print("Something else")
    ```

    Parameters
    ----------
    target_os : `str | None`
        The targeted operating system thats required for the object to be ran.
    python_version : `tuple[int, int, int] | None`
        The targeted Python version thats required for the object to be ran. Format must be `(3, 9, 5)``
    target_arch : `str | None`
        The CPU targeted architecture thats required for the object to be ran.
    impl : `str | None`
        The Python implementation thats required for the object to be ran.

    Returns
    -------
    `bool`
        The condition that was checked.
    """
    checker = _AttrCheck(
        lambda: None,
        no_raise=True,
        target_os=target_os,
        python_version=python_version,
        target_arch=target_arch,
        impl=impl,
    )
    return checker.internal_check()


@typing.final
class _AttrCheck(typing.Generic[F]):
    __slots__ = (
        "_target_os",
        "_callback",
        "_py_version",
        "_no_raise",
        "_target_arch",
        "_py_impl",
        "_debugger",
    )

    def __init__(
        self,
        callback: F,
        target_os: System | None = None,
        python_version: tuple[int, int, int] | None = None,
        target_arch: Arch | None = None,
        impl: Python | None = None,
        *,
        no_raise: bool = False,
    ) -> None:
        self._callback = callback
        self._target_os = target_os
        self._py_version = python_version
        self._target_arch = target_arch
        self._no_raise = no_raise
        self._py_impl = impl
        self._debugger = _Debug(callback, no_raise)

    def __call__(self, *args: typing.Any, **kwds: typing.Any) -> F:
        self._check_once()
        return typing.cast(F, self._callback(*args, **kwds))

    def internal_check(self) -> bool:
        return self._check_once()

    # FIXME: Can we impl this differently?
    def _check_once(self) -> bool:
        results: list[bool] = []
        if self._target_os is not None:
            results.append(self._check_platform())

        if self._py_version is not None:
            results.append(self._check_py_version())

        if self._target_arch is not None:
            results.append(self._check_target_arch())

        if self._py_impl is not None:
            results.append(self._check_py_impl())

        # No checks are passed to cfg(), We return False.
        if not results:
            return False

        return all(results)

    def _check_target_arch(self) -> bool:
        match self._target_arch:
            case "arm":
                return _is_arm()
            case "arm64":
                return _is_arm_64()
            case "x86":
                return _is_x86()
            case "x86_64":
                return _is_x86_64()
            case _:
                raise ValueError(f"Unknown target arch: {self._target_arch}")

    def _check_platform(self) -> bool:
        is_unix = sys.platform in {"linux", "darwin", "macos"}

        # If the target os is unix, then we assume that it's either linux or darwin.
        if self._target_os == "unix" and is_unix:
            return True

        # Alias to win32
        if self._target_os == "windows" and sys.platform == "win32":
            return True

        if self._target_os == "macos" and sys.platform == "darwin":
            return True

        if sys.platform == self._target_os:
            return True

        # fmt: off
        return (
            self._debugger
            .exception(RuntimeError)
            .message(f"requires {self._target_os} OS").finish()
        )
        # fmt: on

    def _check_py_version(self) -> bool:
        if self._py_version and self._py_version <= sys.version_info:
            return True

        return (
            self._debugger.exception(RuntimeError)
            .message(f"requires Python >={self._py_version}")
            .and_then(f"But found {_py_version()}")
            .finish()
        )

    def _check_py_impl(self) -> bool:
        if platform.python_implementation() == self._py_impl:
            return True

        # fmt: off
        return (
            self._debugger.exception(RuntimeError)
            .message(f"requires Python implementation {self._py_impl}")
            .finish()
        )
        # fmt: on


class _Debug(typing.Generic[F]):
    def __init__(
        self,
        callback: F,
        no_raise: bool,
        message: str | None = None,
        exception: type[BaseException] | None = None,
    ) -> None:
        self._callback = callback
        self._exception: type[BaseException] | None = exception
        self._no_raise = no_raise
        self._message = message

    def exception(self, exc: type[BaseException]) -> Self:
        self._exception = exc
        return self

    @functools.cached_property
    def _obj_type(self) -> str:
        if inspect.isfunction(self._callback):
            return "function"
        elif inspect.isclass(self._callback):
            return "class"

        return "object"

    def flag(self, cond: bool) -> None:
        self._no_raise = cond

    def message(self, message: str) -> Self:
        """Set a message to be included in the exception that is getting raised."""
        fn_name = (
            "" if self._callback.__name__ == "<lambda>" else self._callback.__name__
        )
        self._message = f"{self._obj_type} {fn_name} {message}"
        return self

    def and_then(self, message: str) -> Self:
        """Append an extra str to the end of this debugger's message."""
        assert self._message is not None
        self._message += ", " + message
        return self

    def finish(self) -> bool:
        """Finish the result, Either returning a bool or raising an exception."""
        if self._no_raise:
            return False

        assert self._exception is not None
        raise self._exception(self._message) from None
