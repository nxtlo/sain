# sain

Sain is a dependency-free library that implements some of the Rust core standard types.

## Install

You'll need Python 3.10 or higher.

PyPI

```sh
pip install sain
```

## Overview

More examples in [examples](https://github.com/nxtlo/sain/tree/master/examples)

### `cfg`, `cfg_attr` and Marking objects

Conditionally include code at runtime and mark objects.

```py
from sain import cfg, cfg_attr

# Calling this on a non-unix system will raise a RuntimeError
# and the function will not run.
@cfg_attr(target_os="unix")
def run_when_unix() -> None:
    import uvloop
    uvloop.install()

if cfg(target_arch="arm64"):
    run_when_unix()

# If `cfg` returns True, Function will be in scope.
if cfg(requires_modules="aiohttp"):
    import aiohttp
    def create_app() -> aiohttp.web.Application:
        # Calling this will raise a runtime error. its marked as `TODO`.
        sain.todo("Finish me!")

# Assuming aiohttp is not installed.
# Calling the function will raise `NameError` since its not in scope.
app = create_app()

# Those will only warn at runtime and will not raise anything. They're just markers.
@sain.unimplemented(message="User is not fully implemented.")
class User:

    @property
    @sain.deprecated(since = "1.0.4", use_instead="use `get_id` instead.")
    def id(self) -> int:
        ...
```

### `Option<T>` and `Some<T>`

Implements the `Option` type and The `Some` variant. An object that may be `None` or `T`.

This frees you from unexpected runtime exceptions and converts them to as values.

Keep in mind that there're unrecoverable errors such as when calling `.unwrap`, Which you need to personally handle it.

```py
import os

from sain import Some

if typing.TYPE_CHECKING:
    # Available only during type checking.
    from sain import Option

# Replace typing.Optional[str]
def get_token(key: str) -> Option[str]:
    return Some(os.environ.get(key))

# Raises RuntimeError("No token found.") if `os.environ.get` return None.
token = get_token("SOME_KEY").expect("No token found.")

# This operator will internally call `token.unwrap()`.
print(~get_token('SOME_KEY'))

# The classic way to handle this in Python would be.
if token is None:
    token = "..."
else:
    ...

# Replace this with inlined `unwrap_or`. Returning DEFAULT_TOKEN if it was None.
env_or_default = get_token("SOME_KEY").unwrap_or("DEFAULT_TOKEN")

# Type hint is fine.
as_none: Option[str] = sain.Some(None)

# If you're 100% sure that the value will never be None during runtime.
as_none.unwrap() or as_none.unwrap_unchecked()
assert as_none.is_none() # True
```

### Other Types

#### Default

An interface that objects can implement which have a default value.

```py
import sain
import requests

class Session(sain.Default[requests.Session]):
    # One staticmethod must be implemented and must return the same type.
    @staticmethod
    def default() -> requests.Session:
        return requests.Session()

DEFAULT_SESSION = Session.default()
```

#### Once, A value that can be initialized once

```py
from sain import Once
from requests import Session

# Not initialized yet.
DEFAULT_SESSION: Once[Session] = Once()

# Other file.
def run():
    # Get the session if it was initialized from other thread.
    # Otherwise initialize it.
    session = DEFAULT_SESSION.get_or_init(Session())
    session.post("...")
    assert session.get().is_some()  # .get return Option<Session>
```

#### Iter

Turns normal iterables into lazy `Iter` type.

It holds all elements in memory ready to get flushed.

```py
import sain.iter import Iter, empty

f = Iter([1,2,3]) # or iter.iter([1,2,3])
assert 1 in f

for item in f.map(str):
    print(item)

# An iterator that yields nothing.
it = empty()
assert len(it) == 0
```

### Notes

Since Rust is a compiled language, Whatever predict in `cfg` and `cfg_attr` returns False will not compile.

But there's no such thing as this in Python, So `RuntimeError` will be raised and whatever was predicated will not run.
