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

"""A module that contains useful functions and decorators for marking objects."""

from __future__ import annotations

__all__ = (
    "deprecated",
    "unimplemented",
    "todo",
    "doc",
    "assert_eq",
    "assert_ne",
    "include_str",
    "include_bytes",
)

import functools
import inspect
import typing
import warnings

if typing.TYPE_CHECKING:
    T = typing.TypeVar("T", covariant=True)
    import collections.abc as collections

    import _typeshed

    P = typing.ParamSpec("P")
    U = typing.TypeVar("U")
    Read = _typeshed.FileDescriptorOrPath
    # fmt: off
    RustItem = typing.Literal[
        # mem
        "MaybeUninit",
        # option
        "Option", "Some", "None",
        # result
        "Result", "Ok", "Err",
        # macros
        "unimplemented", "todo",
        "deprecated", "doc",
        "cfg", "cfg_attr",
        "assert_eq", "assert_ne",
        "include_bytes", "include_str",
        # std::iter::*
        "Iterator", "Iter", "empty",
        "once", "repeat", "into_iter",
        # errors
        "Error", "catch_unwind",
        # sync
        "Lazy",
        "Once",
        # convert
        "From", "TryFrom",
        "Into", "TryInto",
        # default
        "Default", "default_fn",
        # std::collections::*
        "HashMap",
        "Vec", "vec!",
        # alloc
        "String", "ToString",
        # keywords
        "unsafe",
        # primitives
        "&[u8]",
        "&mut [u8]",
        # time
        "Duration"
    ]
    # fmt: on

_MAP_TO_PATH: dict[RustItem, typing.LiteralString] = {
    # mem
    "MaybeUninit": "std/mem/union.MaybeUninit.html",
    # option
    "Option": "std/option/enum.Option.html",
    "Some": "std/option/enum.Option.html#variant.Some",
    "None": "std/option/enum.Option.html#variant.None",
    # result,
    "Result": "std/result/enum.Result.html",
    "Ok": "std/result/enum.Result.html#variant.Ok",
    "Err": "std/result/enum.Result.html#variant.Err",
    # macros
    "unimplemented": "std/macro.unimplemented.html",
    "todo": "std/macro.todo.html",
    "deprecated": "reference/attributes/diagnostics.html#the-deprecated-attribute",
    "cfg": "std/macro.cfg.html",
    "cfg_attr": "reference/conditional-compilation.html#the-cfg_attr-attribute",
    "doc": "rustdoc/write-documentation/the-doc-attribute.html",
    "assert_eq": "std/macro.assert_eq.html",
    "assert_ne": "std/macro.assert_ne.html",
    "include_bytes": "std/macro.include_bytes.html",
    "include_str": "std/macro.include_str.html",
    # "iter"
    "Iterator": "std/iter/trait.Iterator.html",
    "Iter": "std/slice/struct.Iter.html",
    "empty": "std/iter/fn.empty.html",
    "repeat": "std/iter/fn.repeat.html",
    "once": "std/iter/fn.once.html",
    "into_iter": "std/iter/trait.IntoIterator.html#tymethod.into_iter",
    # errors
    "Error": "std/error/trait.Error.html",
    "catch_unwind": "std/panic/fn.catch_unwind.html",
    # sync
    "Lazy": "std/sync/struct.LazyLock.html",
    "Once": "std/sync/struct.OnceLock.html",
    # convert
    "From": "std/convert/trait.From.html",
    "TryFrom": "std/convert/trait.TryFrom.html",
    "Into": "std/convert/trait.Into.html",
    "TryInto": "std/convert/trait.TryInto.html",
    # default
    "Default": "std/default/trait.Default.html",
    "default_fn": "std/default/trait.Default.html#tymethod.default",
    # collections
    "HashMap": "std/collections/struct.HashMap.html",
    "Vec": "std/vec/struct.Vec.html",
    "vec!": "std/macro.vec.html",
    # alloc
    "String": "alloc/string/struct.String.html",
    "ToString": "alloc/string/trait.ToString.html",
    # keywords
    "unsafe": "std/keyword.unsafe.html",
    # primitives
    "&[u8]": "std/primitive.slice.html",
    "&mut [u8]": "std/primitive.slice.html",
    # time
    "Duration": "std/time/struct.Duration.html",
}

_RUSTC_DOCS = "https://doc.rust-lang.org"


def _warn(msg: str, stacklevel: int = 2, warn_ty: type[Warning] = Warning) -> None:
    warnings.warn(message=msg, stacklevel=stacklevel, category=warn_ty)


@functools.cache
def _obj_type(obj: type[typing.Any]) -> typing.Literal["class", "function"]:
    return "class" if inspect.isclass(obj) else "function"


def rustc_diagnostic_item(item: RustItem, /) -> collections.Callable[[T], T]:
    '''Expands a Python callable object's documentation, generating the corresponding Rust implementation of the marked object.

    This is a decorator that applies on both classes, methods and functions.

    Assuming we're implementing the `FnOnce` trait from Rust, the object in Python may be marked with this decorator like this.
    ```py
    from sain.macros import rustc_diagnostic_item

    @rustc_diagnostic_item("FnOnce")
    class FnOnce[Output, *Args]:
        """The version of the call operator that takes a by-value receiver."""

        def __init__(self, fn: Callable[[*Args], Output]) -> None:
            self._call = fn

        @rustc_diagnostic_item("rust-call")
        def call_once(self, *args: *Args) -> Output:
            return self._call(*args)
    ```

    Now that the class is marked,
    It will generate documentation that links to the Rust object that we implemented in Python.
    '''

    def decorator(obj: T) -> T:
        additional_doc = f"\n\n# Implementations\nThis {_obj_type(obj)} implements [{item}]({_RUSTC_DOCS}/{_MAP_TO_PATH[item]}) in Rust."
        obj.__doc__ = inspect.cleandoc(obj.__doc__ or "") + additional_doc
        return obj

    return decorator


def assert_precondition(
    condition: bool,
    message: str = "",
    exception: type[BaseException] = Exception,
) -> None:
    """Checks if `condition` is true, raising an exception if not.

    This is used to inline check preconditions for functions and methods.

    Example
    -------
    ```py
    from sain.macros import assert_precondition

    def divide(a: int, b: int) -> float:
        assert_precondition(
            b != 0,
            "b must not be zero",
            ZeroDivisionError
        )
        return a / b
    ```

    An inlined version would be:
    ```py
    if not condition:
        raise Exception(
        f"precondition check violated: {message}"
    ) from None
    ```

    Parameters
    ----------
    condition : `bool`
        The condition to check.
    message : `LiteralString`
        The message to display if the condition is false.
        Defaults to an empty string.
    exception : `type[BaseException]`
        The exception to raise if the condition is false.
        Defaults to `Exception`.
    """
    if not condition:
        raise exception(f"precondition check violated: {message}") from None


@typing.final
class ub_checks(RuntimeWarning):
    """A special type of runtime warning that is only invoked on objects using `unsafe`."""


@rustc_diagnostic_item("unsafe")
def unsafe(fn: collections.Callable[P, U]) -> collections.Callable[P, U]:
    """Mark a function as unsafe.

    ## What this marker does
    * Generates an unsafe warning to the docstring of the decorated object.
    * Warn callers of unsafe usage of an object.
    * Never crashes your code, only warns the user, the programmer is responsible
    for the code they've written, this is a utility decorator only.

    however, ignoring these warnings is possible (*not recommended*), see he listed examples.

    Example
    -------

    Using warnings lib:
    ```py
    import warnings
    from sain.macros import unsafe, ub_checks

    # globally ignore all `ub_checks` warns, not recommended.
    warnings.filterwarnings("ignore", category=ub_checks)

    @unsafe
    def from_str_unchecked(val: str) -> float:
        return float(val)

    # This is a function that calls `from_str_unchecked`
    # but we know it will never fails.
    def infallible() -> float:
        with warnings.catch_warnings():
            # ignore `ub_checks` specific warnings from `from_str_unchecked`.
            warnings.simplefilter("ignore", category=ub_checks)
            return from_str_unchecked("3.14")
    ```

    Another way is to simply run your program with `-O` opt flag.

    This won't generate the code needed to execute the warning,
    this will also disable all `assert` calls.

    ```sh
    # This enable optimization level 1, which will opt-out of `ub_checks` warnings.
    python script.py -O
    # This will ignore all the warnings.
    python -W ignore script.py
    ```

    The caller of the decorated function is responsible for the undefined behavior if occurred.
    """
    m = "\n# Safety ⚠️\nCalling this method is considered [undefined behavior](https://en.wikipedia.org/wiki/Undefined_behavior).\n"
    if fn.__doc__ is not None:
        # append this message to an existing document.
        fn.__doc__ = inspect.cleandoc(fn.__doc__) + m
    else:
        fn.__doc__ = m

    if __debug__:

        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> U:
            call_once = fn(*args, **kwargs)
            _warn(
                f"calling `{wrapper.__qualname__}` "
                "is considered unsafe and may lead to undefined behavior.\n"
                "you can disable this warning by using `-O` opt level if you know what you're doing.",
                warn_ty=ub_checks,
            )
            return call_once

        return wrapper
    else:
        return fn


@rustc_diagnostic_item("assert_eq")
def assert_eq(left: T, right: T) -> None:
    """Asserts that two expressions are equal to each other.

    This exactly as `assert left == right`, but includes a useful message in case of failure.

    Example
    -------
    ```py
    from sain.macros import assert_eq
    a = 3
    b = 1 + 2
    assert_eq(a, b)
    ```
    """
    assert left == right, (
        f'assertion `left == right` failed\nleft: "{left!r}"\nright: "{right!r}"'
    )


@rustc_diagnostic_item("assert_ne")
def assert_ne(left: T, right: T) -> None:
    """Asserts that two expressions are not equal to each other.

    This exactly as `assert left == right`, but includes a useful message in case of failure.

    Example
    -------
    ```py
    from sain.macros import assert_ne
    a = 3
    b = 2 + 2
    assert_ne(a, b)
    ```
    """
    assert left != right, (
        f'assertion `left != right` failed\nleft: "{left!r}"\nright: "{right!r}"'
    )


@rustc_diagnostic_item("include_bytes")
def include_bytes(file: typing.LiteralString) -> bytes:
    """Includes a file as `bytes`.

    This function is not magic, It is literally defined as

    ```py
    with open(file, "rb") as f:
        return f.read()
    ```

    The file name can may be either a relative to the current file or a complete path.

    Example
    -------
    File "spanish.in":
    ```text
    adiós
    ```
    File "main.py":
    ```py
    from sain.macros import include_bytes
    buffer = include_bytes("spanish.in")
    assert buffer.decode() == "adiós"
    ```
    """
    with open(file, "rb") as buf:
        return buf.read()


@rustc_diagnostic_item("include_str")
def include_str(file: typing.LiteralString) -> typing.LiteralString:
    """Includes a file as literal `str`.

    This function is not magic, It is literally defined as

    ```py
    with open(file, "r") as f:
        return f.read()
    ```

    The file name can may be either a relative to the current file or a complete path.

    Example
    -------
    ```py
    from sain.macros import include_str

    def entry() -> None:
        ...

    entry.__doc__ = include_str("README.md")

    ```
    """
    with open(file, "r") as buf:
        return buf.read()  # pyright: ignore - simulates a `&'static str` slice.


def unstable(
    *, reason: typing.LiteralString = "none"
) -> collections.Callable[
    [collections.Callable[P, typing.Any]],
    collections.Callable[P, typing.NoReturn],
]:
    """A decorator that marks an internal object explicitly unstable.

    Unstable objects never ran, even inside the library.

    Calling any object that is unstable will raise an `RuntimeError` exception.
    Also using this outside the library isn't allowed.

    Example
    -------
    ```py

    from sain.macros import unstable

    @unstable(reason = "none")
    def unstable_function() -> int:
        return -1

    if unstable_function():
        # never reachable

    ```
    """

    def decorator(
        obj: collections.Callable[P, U],
    ) -> collections.Callable[P, typing.NoReturn]:
        @functools.wraps(obj)
        def wrapper(*_args: P.args, **_kwargs: P.kwargs) -> typing.NoReturn:
            raise RuntimeError(
                f"{_obj_type(obj)} `{obj.__name__}` is not stable: {reason}. "
                "Stability attributes are intended for use only within the core library and should not be applied in external modules or scripts."
            )

        m = (
            f"\n# Stability ⚠️\nThis {_obj_type(obj)} is unstable, "
            "Calling it may result in failure or [undefined behavior](https://en.wikipedia.org/wiki/Undefined_behavior)."
        )
        # Append the formatted string to the existing documentation if it exists, otherwise set it as the documentation.
        wrapper.__doc__ = (
            (inspect.cleandoc(wrapper.__doc__) + m) if wrapper.__doc__ else m
        )
        return wrapper

    return decorator


@typing.overload
def deprecated(
    *,
    obj: collections.Callable[P, U] | None = None,
) -> collections.Callable[P, U]: ...


@typing.overload
def deprecated(
    *,
    since: typing.Literal["CURRENT_VERSION"] | typing.LiteralString | None = None,
    removed_in: typing.LiteralString | None = None,
    use_instead: typing.LiteralString | None = None,
    hint: typing.LiteralString | None = None,
) -> collections.Callable[
    [collections.Callable[P, U]],
    collections.Callable[P, U],
]: ...


@rustc_diagnostic_item("deprecated")
def deprecated(
    *,
    obj: collections.Callable[P, U] | None = None,
    since: typing.Literal["CURRENT_VERSION"] | typing.LiteralString | None = None,
    removed_in: typing.LiteralString | None = None,
    use_instead: typing.LiteralString | None = None,
    hint: typing.LiteralString | None = None,
) -> (
    collections.Callable[P, U]
    | collections.Callable[
        [collections.Callable[P, U]],
        collections.Callable[P, U],
    ]
):
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
        hint = "Hint for ux."
    )
    class User:
        # calling the decorator is not necessary.
        @deprecated
        def username(self) -> str:
            ...

    user = User() # This will cause a warning at runtime.

    ```

    Parameters
    ----------
    since : `str`
        The version that the function was deprecated. the `CURRENT_VERSION` is used internally only.
    removed_in : `str | None`
        If provided, It will log when will the object will be removed in.
    use_instead : `str | None`
        If provided, This should be the alternative object name that should be used instead.
    hint: `str`
        An optional hint for the user.
    """

    def _create_message(
        f: typing.Any,
    ) -> str:
        msg = f"{_obj_type(f)} `{f.__module__}.{f.__name__}` is deprecated."

        if since is not None:
            if since == "CURRENT_VERSION":
                from ._misc import __version__

                msg += " since " + __version__
            else:
                msg += " since " + since

        if removed_in:
            msg += f" Scheduled for removal in `{removed_in}`."

        if use_instead is not None:
            msg += f" Use `{use_instead}` instead."

        if hint:
            msg += f" Hint: {hint}"
        return msg

    def decorator(func: collections.Callable[P, U]) -> collections.Callable[P, U]:
        message = _create_message(func)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> U:
            _warn(message, warn_ty=DeprecationWarning)
            return func(*args, **kwargs)

        # idk why pyright doesn't know the type of wrapper.
        m = f"\n# Warning ⚠️\n{message}."
        if wrapper.__doc__:
            # append this message to an existing document.
            wrapper.__doc__ = inspect.cleandoc(wrapper.__doc__) + f"{m}"
        else:
            wrapper.__doc__ = m

        return wrapper

    # marked only.
    if obj is not None:
        return decorator(obj)

    return decorator


@rustc_diagnostic_item("todo")
def todo(message: typing.LiteralString | None = None) -> typing.NoReturn:
    """A place holder that indicates unfinished code.

    Example
    -------
    ```py
    from sain import todo

    def from_json(payload: dict[str, int]) -> int:
        # Calling this function will raise `Error`.
        todo()
    ```

    Parameters
    ----------
    message : `str | None`
        Multiple optional arguments to pass if the error was raised.
    """
    raise RuntimeWarning(
        f"not yet implemented: {message}" if message else "not yet implemented"
    )


@typing.overload
def unimplemented(
    *,
    obj: collections.Callable[P, U] | None = None,
) -> collections.Callable[P, U]: ...


@typing.overload
def unimplemented(
    *,
    message: typing.LiteralString | None = None,
    available_in: typing.LiteralString | None = None,
) -> collections.Callable[
    [collections.Callable[P, U]],
    collections.Callable[P, U],
]: ...


@rustc_diagnostic_item("unimplemented")
def unimplemented(
    *,
    obj: collections.Callable[P, U] | None = None,
    message: typing.LiteralString | None = None,
    available_in: typing.LiteralString | None = None,
) -> (
    collections.Callable[P, U]
    | collections.Callable[
        [collections.Callable[P, U]],
        collections.Callable[P, U],
    ]
):
    """A decorator that marks an object as unimplemented.

    An attempt to call the object that's marked will cause a runtime warn.

    Example
    -------
    ```py
    from sain import unimplemented

    @unimplemented  # Can be used without calling
    class User:
        ...

    @unimplemented(message="Not ready", available_in="2.0.0")  # Or with parameters
    class Config:
        ...
    ```

    Parameters
    ----------
    message : `str | None`
        An optional message to be displayed when the function is called. Otherwise default message will be used.
    available_in : `str | None`
        If provided, This will be shown as what release this object be implemented.
    """

    def _create_message(f: typing.Any) -> str:
        msg = (
            message
            or f"{_obj_type(f)} `{f.__module__}.{f.__name__}` is not yet implemented."
        )

        if available_in:
            msg += f" Available in `{available_in}`."
        return msg

    def decorator(func: collections.Callable[P, U]) -> collections.Callable[P, U]:
        msg = _create_message(func)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> U:
            _warn(msg, warn_ty=RuntimeWarning)
            return func(*args, **kwargs)

        m = f"\n# Warning ⚠️\n{msg}."
        if wrapper.__doc__:
            # Append the new documentation string to the existing docstring.
            wrapper.__doc__ = inspect.cleandoc(wrapper.__doc__) + m
        else:
            # Assign the new documentation string as the docstring when no existing docstring is present.
            wrapper.__doc__ = m
        return wrapper

    if obj is not None:
        return decorator(obj)

    return decorator


@rustc_diagnostic_item("doc")
def doc(
    path: Read,
) -> collections.Callable[
    [collections.Callable[P, U]],
    collections.Callable[P, U],
]:
    """Set `path` to be the object's documentation.

    Example
    -------
    ```py
    from sain import doc
    from pathlib import Path

    @doc(Path("../README.md"))
    class builtins:
        @doc("bool.html")
        def bool_docs() -> None:
            ...
    ```

    Parameters
    ----------
    path: `type[int] | type[str] | type[bytes] | type[PathLike[str]] | type[PathLike[bytes]]`
        The path to read the content from.
    """

    def decorator(f: collections.Callable[P, U]) -> collections.Callable[P, U]:
        with open(path, "r") as file:
            f.__doc__ = file.read()

        return lambda *args, **kwargs: f(*args, **kwargs)

    return decorator
