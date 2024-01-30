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

__all__ = ("deprecated", "unimplemented", "todo", "unstable", "doc")

import functools
import inspect
import logging
import typing
import warnings

import urllib3

if typing.TYPE_CHECKING:
    import collections.abc as collections

    import _typeshed

    P = typing.ParamSpec("P")
    T = typing.TypeVar("T", bound=collections.Callable[..., typing.Any])
    U = typing.TypeVar("U")
    Fn = collections.Callable[..., U]
    Read = _typeshed.FileDescriptorOrPath

_LOGGER = logging.getLogger("sain.macros")


@typing.final
class Error(RuntimeWarning):
    """A runtime warning that is raised when the decorated object fails a check."""

    __slots__ = ("message",)

    def __init__(self, message: typing.LiteralString | None = None) -> None:
        self.message = message


def _warn(msg: str, stacklevel: int = 2) -> None:
    warnings.warn(message=msg, stacklevel=stacklevel, category=Error)


def unstable(*, reason: typing.LiteralString) -> collections.Callable[[T], T]:
    """A decorator that marks an internal object explicitly unstable."""

    def decorator(obj: T) -> T:
        @functools.wraps(obj)
        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            obj_type = "class" if inspect.isclass(obj) else "function"
            if not obj.__doc__ == "__intrinsics__":
                # This has been used outside of the lib.
                raise Error(
                    "Stability attributes may not be used outside of the core library"
                )

            name = obj.__name__
            if name.startswith("_"):
                name = obj.__name__.lstrip("_")

            _warn(f"{obj_type} {name} is not stable: {reason}")
            return obj(*args, **kwargs)

        return typing.cast("T", wrapper)

    return decorator


def deprecated(
    *,
    since: typing.LiteralString | None = None,
    use_instead: typing.LiteralString | None = None,
    removed_in: typing.LiteralString | None = None,
    hint: typing.LiteralString | None = None,
) -> collections.Callable[[T], T]:
    """A decorator that marks a function as deprecated.

    An attempt to call the object that's marked will cause a runtime warn.

    Example
    -------
    ```py
    from sain import deprecated

    @deprecated(
        since = "1.0.0",
        removed_in ="3.0.0",
        use_instead = "UserImpl()",
        hint = "..."
    )
    class User:
        ...

    user = User() # This will raise an error at runtime.
    ```

    Parameters
    ----------
    since : `str`
        The version that the function was deprecated.
    removed_in : `str | None`
        If provided, It will log when will the object will be removed in.
    use_instead : `str | None`
        If provided, This should be the alternative object name that should be used instead.
    hint: `str`
        An optional hint for the user.
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

            if removed_in:
                msg += f" Removed in {removed_in}."

            if hint:
                msg += f" Hint: {hint}"

            _warn(msg)
            return func(*args, **kwargs)

        return typing.cast("T", wrapper)

    return decorator


def todo(message: typing.LiteralString | None = None) -> typing.NoReturn:
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


def unimplemented(
    *,
    message: typing.LiteralString | None = None,
    available_in: typing.LiteralString | None = None,
) -> collections.Callable[[T], T]:
    """A decorator that marks an object as unimplemented.

    An attempt to call the object that's marked will cause a runtime warn.

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
            msg = (
                message
                or f"{obj_type} {obj.__module__}.{obj.__name__} is not yet implemented."
            )  # noqa: W503

            if available_in:
                msg += f" Available in {available_in}."

            _warn(msg)
            return obj(*args, **kwargs)

        return typing.cast("T", wrapper)

    return decorator


def doc(path: Read) -> Fn[Fn[Fn[T]]]:
    """Set `path` to be the object's documentation.

    Example
    -------
    ```py
    from sain import doc
    from pathlib import Path

    @doc(Path("../README.md"))
    class User:

        # Raw HTTP text documentation.
        @doc("https://raw.githubusercontent.com/nxtlo/sain/master/README.md")
        def insane(x: float) -> float:
            ...
    ```

    path: `type[int] | type[str] | type[bytes] | type[PathLike[str]] | type[PathLike[bytes]]`
        The path to read the content from.
    """

    def decorator(f: Fn[T]) -> Fn[T]:
        if isinstance(path, str) and path.startswith("https://"):
            try:
                response = urllib3.request("GET", path)
                f.__doc__ = response.data.decode("UTF-8")

            except urllib3.exceptions.HTTPError as e:
                _LOGGER.exception(
                    "An error occurred while trying to fetch the docs form %s, cause %s",
                    path,
                    e,
                )
                pass

        else:
            with open(path, "r") as file:
                f.__doc__ = file.read()

        @functools.wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return f(*args, **kwargs)

        return wrapper

    return decorator
