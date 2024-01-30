"""
`Option<T>` and `Some<T>`

Implements the `Option` type and The `Some` variant, A value that's either `T` or `None`,
this frees you from unexpected runtime exceptions and converts them to as values,
keep in mind that there're unrecoverable errors such as when calling `.unwrap`, Which you need to personally handle it.
"""

from __future__ import annotations

import typing
import dataclasses

import sain

if typing.TYPE_CHECKING:
    from sain import Option
    from typing_extensions import Self


@dataclasses.dataclass
class TokenGetter:
    """A token getter strategy."""

    token: Option[str] = sain.Some(None)

    # ! Warning: the `required_modules` attribute is currently buggy
    # ! and will warn you if you run that code.
    @classmethod
    @sain.cfg_attr(requires="python-dotenv")
    def from_dotenv(cls, key: str, /) -> Self:
        """Gets the token from the .env file. This requires the module `python-dotenv`."""
        import dotenv  # pyright: ignore[reportMissingImports]

        return cls(sain.Some(dotenv.get_key(".env", key)))

    @classmethod
    def from_raw_env(cls, key: str, /) -> Self:
        """Gets the token from the raw OS environment."""
        import os

        return cls(sain.Some(os.environ.get(key)))


# CPython implementation only function.
@sain.cfg_attr(impl="CPython")
def main() -> None:
    if sain.cfg(target_os="windows"):
        print("Running on Windows...")
        getter = TokenGetter.from_dotenv("API_TOKEN")
    else:
        print("Running on Unix...")
        getter = TokenGetter.from_raw_env("API_TOKEN")

    # This should prints Some(None) if the token not in .env file.
    # Otherwise Some("token")
    print(getter.token)

    # If you're sure that the token exists, you can unwrap it.
    # NOTE: This raises a runtime error.
    try:
        print(getter.token.unwrap())
        # Or you can, This does exactly what `unwrap` does.
        print(~getter.token)
    except RuntimeError:
        pass

    # If you're not sure, you can safely use a default value.
    print(getter.token.unwrap_or("DEFAULT_TOKEN"))  # DEFAULT_TOKEN

    # Map the token to a function making it upper case.
    to_map = TokenGetter(sain.Some("blah"))
    print(to_map.token.map(str.upper))  # Some("BLAH")


if __name__ == "__main__":
    main()
