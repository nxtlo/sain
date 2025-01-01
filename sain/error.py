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
"""Interfaces for working with Errors.

This exposes one abstract interface, `Error` that other errors can implement and use as an argument to match upon.

Usually this error is returned from a `Result[T, Error]` object.

Those errors can be converted into `RuntimeError` exceptions by calling `sain.Result.unwrap` and `sain.Option.unwrap`.

For an example

```py
# Read the env variable, raises `RuntimeError` if it is not present.
path: Option[str] = Some(os.environ.get('SOME_PATH')).unwrap()
```

HTTP requests are good example where errors can be returned all the time.
Lets implement one.

Example
-------
from sain import Error
from dataclasses import dataclass

# Base error.
class HTTPError(Error):
    ...

@dataclass
class NotFound(HTTPError):
    message = "Response not found."
    response: requests.Response

    def description(self) -> str:
        ...
"""

from __future__ import annotations

__all__ = ("Error", "catch_unwind")

import typing

from . import option as _option
from sain import result as _result
from .convert import ToString

if typing.TYPE_CHECKING:
    from collections.abc import Callable

    from sain import Option
    from sain import result as _result

R = typing.TypeVar("R", covariant=True)


@typing.runtime_checkable
class Error(ToString, typing.Protocol):
    """`Error` is an interface usually used for values that returns `sain.Result[T, E]`

    where `E` is an implementation of this interface.

    Example
    -------
    ```py
    import requests
    from dataclasses import dataclass

    from sain import Error, Option, Some
    from sain import Result, Ok, Err

    # Base error.
    class HTTPError(Error): ...

    @dataclass
    class NotFound(HTTPError):
        message = "The response returned [404]: not found."
        http_status = 404
        response: requests.Response

        def description(self) -> str:
            return "Couldn't find what you're looking for " + self.response.url

        # It is not necessary to define this method,
        # it just gives more context to the user handling this error.
        def source(self) -> Option[type[HTTPError]]:
            return Some(HTTPError)

    @dataclass
    class UserNotFound(NotFound):
        user_id: int

        def __post_init__(self) -> None:
            request = self.response.request
            self.message = f"User {self.user_id} fetched from {request.path_url} was not found."

        # It is not necessary to define this method,
        # it just gives more context to the user handling this error.
        def source(self) -> Option[type[NotFound]]:
            return Some(NotFound)

        def description(self) -> str:
            return f"Couldn't find the resource: {self.response.raw}."

    # A simple request that handles [404] responses.
    def request(
        url: str,
        resourceful: bool = False,
        uid: int
    ) -> Result[requests.Response, HTTPError]:
        response = requests.get(
            url,
            json={"resourceful": True, "user_id": uid}
            if resourceful else None
        )

        if response.status_code == 404:
            if resourceful:
                return Err(UserNotFound(response, uid))
            return Err(NotFound(response))

        return Ok(response)

    # Execute the request
    match request("some-url.com', True, uid=0):
        case Ok(response):
            # Deal with the response
            ...
        case Err(why):
            # Deal with the error.
            print(why.message)
    ```
    """

    __slots__ = ("message",)

    def __init__(self, message: str = "") -> None:
        self.message = message
        """A basic error message."""

    def source(self) -> Option[type[Error]]:
        """The source of this error, if any."""
        return _option.NOTHING  # pyright: ignore

    def description(self) -> str:
        """Context for this error."""
        return ""

    def to_string(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        source = None if (src := self.source()).is_none() else src
        return (
            f'{type(self).__qualname__}(message: "{self.message}, source: {source!r})'
        )

    def __str__(self) -> str:
        return self.message

    # An error is always falsy.
    def __bool__(self) -> typing.Literal[False]:
        return False


def catch_unwind(fn: Callable[[], R]) -> _result.Result[R, BaseException]:
    """Invokes a closure, capturing exceptions if any one raised.

    This function will return `Ok` with the closure's result if it doesn't raise any exceptions,
    otherwise it will return `Err(cause)` with the exception.

    You can treat this as an inline try-except block.

    Notes
    -----
    This function also catch exceptions such as `KeyboardInterrupt` and `SystemExit`,
    so try to use it with extreme caution.

    Example
    -------
    ```py
    from sain.error import catch_unwind

    def request() -> str:
        return requests.get("some url").text

    def fetch() -> str:
        raise RuntimeError from None

    result = catch_unwind(request)
    assert result.is_ok()

    result = catch_unwind(fetch)
    assert result.is_err()
    ```

    Parameters
    ----------
    fn: `Callable[[], R]`
        The function to run.

    Returns
    -------
    `Result[R, BaseException]`
        Returns `Ok(value)` if the function ran successfully, otherwise `Err(cause)` with the exception.
    """
    try:
        return _result.Ok(fn())
    except BaseException as e:
        return _result.Err(e)
