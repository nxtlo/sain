"""A simple example of using the `cfg` and `Option` APIs."""

from __future__ import annotations

import typing
import dataclasses

import sain

if typing.TYPE_CHECKING:
    from sain import Option


@dataclasses.dataclass
class TokenGetter:
    """A token getter strategy."""

    token: Option[str] = sain.Some(None)

    # ! Warning: the `required_modules` attribute is currently buggy
    # ! and will warn you if you run that code.
    @classmethod
    @sain.cfg_attr(requires_modules="python-dotenv")
    def from_env(cls, key: str, /) -> TokenGetter:
        """Gets the token from the .env file. This requires the module `python-dotenv`."""
        import dotenv

        return cls(sain.Some(dotenv.get_key(".env", key)))

    @classmethod
    def from_raw_env(cls, key: str, /) -> TokenGetter:
        """Gets the token from the raw OS enviorment."""
        import os

        return cls(sain.Some(os.getenv(key)))


# CPython implementation only function.
@sain.cfg_attr(impl="CPython")
def main() -> None:
    if sain.cfg(target_os="windows"):
        print("Running on Windows...")
        getter = TokenGetter.from_env("API_TOKEN")
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
    except RuntimeError:
        pass

    # If you're not sure, you can safely use a default value.
    print(getter.token.unwrap_or("zzxxcc"))  # zzxxcc

    # Map the token to a function making it upper case.
    to_map = TokenGetter(sain.Some("bAah"))
    print(to_map.token.map(lambda x: x.upper()))  # Some("BAAH")


if __name__ == "__main__":
    main()
