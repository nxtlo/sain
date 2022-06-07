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
"""Runtime attr confuguration."""

from __future__ import annotations

__all__: typing.Tuple[str, ...] = ("cfg_attr", "cfg")

import functools
import inspect
import platform
import sys
import typing

import pkg_resources

SigT = typing.Callable[..., object]
Signature = typing.TypeVar("Signature", bound=SigT)
"""A type var hint for the decorated object signature."""

TARGET_OS = typing.Literal["linux", "win32", "darwin", "unix", "windows"]
TARGET_ARCH = typing.Literal["x86", "x64", "arm", "arm64"]
PY_IMPL = typing.Literal["CPython", "PyPy", "IronPython", "Jython"]


def _machine() -> str:
    return platform.machine()


def _is_arm() -> bool:
    return _machine().startswith("arm")


def _is_arm_64() -> bool:
    return _is_arm() and _is_x64()


def _is_x64() -> bool:
    return _machine().endswith("64")


def cfg_attr(
    *,
    requires_modules: typing.Optional[typing.Union[str, typing.Sequence[str]]] = None,
    target_os: typing.Optional[TARGET_OS] = None,
    python_version: typing.Optional[typing.Tuple[int, int, int]] = None,
    target_arch: typing.Optional[TARGET_ARCH] = None,
    impl: typing.Optional[PY_IMPL] = None,
) -> typing.Callable[[Signature], Signature]:
    """Conditional runtime object configuration based on passed arguments.

    If the decorated object gets called and one of the attributes returns `False`,
    `RuntimeError` will be raised and the object will not run.

    Example
    -------
    ```py
    import sain

    @sain.cfg_attr(target_os = "windows")
    def windows_only():
        # Do stuff with Windows's API.
        ...

    # Mut be PyPy Python implementation or `RuntimeError` will be raised
    # when creating the instance.
    @sain.cfg_attr(impl="PyPy")
    class Zoo:
        @sain.cfg_attr(target_os = "linux")
        def bark(self) -> None:
            windows_only()  # RuntimeError("Windows OS only!)

    # An instance will not be created if raised.
    zoo = Zoo()
    # RuntimError("class Zoo requires PyPy implementation")
    zoo.bark()
    # Whats zoo??
    ```

    Parameters
    ----------
    requires_modules : `str | Sequence[str] | None`
        A string or sequence of the required modules for the object to be ran.
    target_os : `str | None`
        The targeted operating system thats required for the object to be ran.
    python_version : `tuple[int, int, int] | None`
        The targeted Python version thats required for the object to be ran.

        Format must be `(3, 9, 5)`.
    target_arch : `str | None`
        The CPU targeted architecture thats required for the object to be ran.
    impl : `str | None`
        The Python implementation thats required for the object to be ran.

    Raises
    ------
    `RuntimeError`
        This fails if any of the attributes returns `False`. `required_modules` is not included.
    `ModuleNotFoundError`
        If the module check fails. i.e., if `required_modules` was provided and it returns `False`.
    `ValueError`
        If the passed Python implementation is unknown.
    """

    def decorator(callback: Signature) -> Signature:
        @functools.wraps(callback)
        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> Signature:
            checker = _AttrCheck[Signature](
                callback,
                requires_modules=requires_modules,
                target_os=target_os,
                python_version=python_version,
                target_arch=target_arch,
                impl=impl,
            )
            return checker(*args, **kwargs)

        return typing.cast(Signature, wrapper)

    return decorator


def cfg(
    target_os: typing.Optional[TARGET_OS] = None,
    requires_modules: typing.Optional[typing.Union[str, typing.Sequence[str]]] = None,
    python_version: typing.Optional[typing.Tuple[int, int, int]] = None,
    target_arch: typing.Optional[TARGET_ARCH] = None,
    impl: typing.Optional[PY_IMPL] = None,
) -> bool:
    """A function that will run the code only if all predicate attributes returns `True`.

    The difference between this function and `cfg_attr` is that this function will not raise an exception.
    Instead it will return `False` if any of the attributes fails.

    Example
    -------
    ```py
    import sain

    if sain.cfg(target_os = "windows"):
        print("Windows")
    elif sain.cfg(target_os = "linux"):
        print("Linux")
    else:
        print("Something else")
    ```

    Parameters
    ----------
    requires_modules : `str | Sequence[str] | None`
        A string or sequence of the required module names for the object to be ran.
    target_os : `str | None`
        The targeted operating system thats required for the object to be ran.
    python_version : `tuple[int, int, int] | None`
        The targeted Python version thats required for the object to be ran.

        Format must be `(3, 9, 5)`.
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
        requires_modules=requires_modules,
        target_os=target_os,
        python_version=python_version,
        target_arch=target_arch,
        impl=impl,
    )
    return checker.internal_check()


class _AttrCheck(typing.Generic[Signature]):
    __slots__ = (
        "_requires_modules",
        "_target_os",
        "_callback",
        "_py_version",
        "_no_raise",
        "_target_arch",
        "_py_impl",
    )

    def __init__(
        self,
        callback: Signature,
        requires_modules: typing.Optional[typing.Union[str, typing.Sequence[str]]] = None,
        target_os: typing.Optional[TARGET_OS] = None,
        python_version: typing.Optional[typing.Tuple[int, int, int]] = None,
        target_arch: typing.Optional[TARGET_ARCH] = None,
        impl: typing.Optional[PY_IMPL] = None,
        *,
        no_raise: bool = False,
    ) -> None:
        self._callback = callback
        self._requires_modules = requires_modules
        self._target_os = target_os
        self._py_version = python_version
        self._target_arch = target_arch
        self._no_raise = no_raise
        self._py_impl = impl

    def __call__(self, *args: typing.Any, **kwds: typing.Any) -> Signature:
        self._check_once()
        return typing.cast(Signature, self._callback(*args, **kwds))

    def internal_check(self) -> bool:
        return self._check_once()

    def _check_once(self) -> bool:
        results: list[bool] = []
        if self._target_os is not None:
            results.append(self._check_platform())

        if self._py_version is not None:
            results.append(self._check_py_version())

        if self._requires_modules is not None:
            results.append(self._check_modules())

        if self._target_arch is not None:
            results.append(self._check_target_arch())

        if self._py_impl is not None:
            results.append(self._check_py_impl())

        # No checks are passed to cfg(), We return False.
        if not results:
            return False

        return all(results)

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
                    return self._raise_or_else(
                        ModuleNotFoundError(self._output_str(f"requires modules {', '.join(needed)} to be installed"))
                    )
        return True

    def _check_platform(self) -> bool:
        is_unix = sys.platform in {"linux", "darwin"}

        # If the target os is unix, then we assume that it's either linux or darwin.
        if self._target_os == "unix" and is_unix:
            return True

        # Alias to win32
        if self._target_os == "windows" and sys.platform == "win32":
            return True

        if sys.platform == self._target_os:
            return True

        return self._raise_or_else(RuntimeError(self._output_str(f"requires {self._target_os} OS")))

    def _check_py_version(self) -> bool:
        if self._py_version and self._py_version <= sys.version_info:
            return True

        return self._raise_or_else(
            RuntimeError(
                self._output_str(f"requires Python >={self._py_version}. But found {platform.python_version()}")
            )
        )

    def _check_target_arch(self) -> bool:
        if self._target_arch:
            if self._target_arch == "arm":
                return _is_arm()
            elif self._target_arch == "arm64":
                return _is_arm_64()
            elif self._target_arch == "x86":
                return not _is_x64()
            elif self._target_arch == "x64":
                return _is_x64()
            else:
                raise ValueError(f"Unknown target arch: {self._target_arch}")

        return False

    def _check_py_impl(self) -> bool:
        if platform.python_implementation() == self._py_impl:
            return True

        return self._raise_or_else(RuntimeError(self._output_str(f"requires Python implementation {self._py_impl}")))

    @property
    def _obj_type(self) -> str:
        if inspect.isfunction(self._callback):
            return "function"
        elif inspect.isclass(self._callback):
            return "class"

        return "object"

    def _output_str(self, message: str, /) -> str:
        fn_name = "" if self._callback.__name__ == "<lambda>" else self._callback.__name__
        return f"{self._obj_type} {fn_name} {message}."

    def _raise_or_else(self, exception: BaseException, /) -> bool:
        if self._no_raise:
            return False
        else:
            raise exception from None
