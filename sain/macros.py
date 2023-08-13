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

"""A module that contains useful decorators"""

from __future__ import annotations

__all__ = ("deprecated", "unimplemented", "todo", "unstable")

import functools
import inspect
import typing
import warnings

if typing.TYPE_CHECKING:
    import collections.abc as collections

    T = typing.TypeVar("T", bound=collections.Callable[..., typing.Any])


class Error(RuntimeWarning):
    """A runtime error that is raised when the decorated object fails a check."""

    __slots__ = ("message",)

    def __init__(self, message: str | None = None, *args: typing.Any) -> None:
        super().__init__(message, *args)
        self.message = message


def _warn(msg: str, stacklevel: int = 2) -> None:
    warnings.warn(message=msg, stacklevel=stacklevel, category=Error)


def unstable(*, reason: str) -> collections.Callable[[T], T]:
    """A decorator that marks an internal object explicitly unstable."""

    def decorator(obj: T) -> T:
        @functools.wraps(obj)
        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            obj_type = "class" if inspect.isclass(obj) else "function"
            if not obj.__doc__ == "__intrinsics__":
                # This has been used outside of the lib.
                raise Error("Stability attributes may not be used outside of the core library")

            name = obj.__name__
            if name.startswith("_"):
                name = obj.__name__.lstrip("_")

            _warn(f"{obj_type} {name} is not stable: {reason}")
            return obj(*args, **kwargs)

        return typing.cast("T", wrapper)

    return decorator


def deprecated(
    *,
    since: str | None = None,
    use_instead: str | None = None,
) -> collections.Callable[[T], T]:
    """A decorator that marks a function as deprecated.

    An attemp to call the object that's marked will raise an `sain.macros.Error` exception.

    Example
    -------
    ```py
    from sain import deprecated

    @deprecated(since = "1.0.0", use_instead = "UserImpl()")
    class User:
        ...

    user = User() # This will raise an error at runtime.
    ```

    Parameters
    ----------
    since : `str`
        The version that the function was deprecated.
    removed_int : `str | None`
        If provided, It will log when will the object will be removed in.
    use_instead : `str | None`
        If provided, This should be the alternaviate object name that should be used instead.
    """

    def decorator(func: T) -> T:
        @functools.wraps(func)
        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            obj_type = "class" if inspect.isclass(func) else "function"
            msg = f"{obj_type} {func.__module__}.{func.__name__} is deprecated."

            if since is not None:
                msg += f" since {since}."

            if use_instead is not None:
                msg += f" Use {use_instead} instead."

            _warn(msg)
            return func(*args, **kwargs)

        return typing.cast("T", wrapper)

    return decorator


def todo(message: str | None = None) -> typing.NoReturn:
    """A place holder that indicates unfinished code.

    This is not a decorator. See example.

    Example
    -------
    ```py

    @dataclass
    class User:
        name: str
        id: int

        @classmethod
        def from_json(cls, payload: dict[str, Any]) -> Self:
            # Calling this method will raise `Error`.
            todo()
    ```

    Parameters
    ----------
    *args : object | None
        Multiple optional arguments to pass if the error was raised.
    """
    raise Error(f"not yet implemented: {message}" if message else "not yet implemented")


def unimplemented(*, message: str | None = None, available_in: str | None = None) -> collections.Callable[[T], T]:
    """A decorator that marks an object as unimplemented.

    An attemp to call the object that's marked will cause a warn.

    Example
    -------
    ```py
    from sain import unimplemented

    @unimplemented("User object is not implemented yet.")
    class User:
        ...
    ```

    Parameters
    ----------
    message : `str | None`
        An optional message to be displayed when the function is called. Otherwise default message will be used.
    available_in : `str | None`
        If provided, This will be shown as what release this object be implemented.
    """

    def decorator(obj: T) -> T:
        @functools.wraps(obj)
        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            obj_type = "class" if inspect.isclass(obj) else "function"
            msg = message or f"{obj_type} {obj.__module__}.{obj.__name__} is not yet implemented."  # noqa: W503

            if available_in:
                msg += f" Avaliable in {available_in}."

            _warn(msg)
            return obj(*args, **kwargs)

        return typing.cast("T", wrapper)

    return decorator
