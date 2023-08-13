# sain
Sain is a dependency-free library that implements some of the Rust core standard types.


## Install
You'll need Python 3.10 or higher.

PyPI
```sh
$ pip install sain
```

## Overview
More examples in [examples](https://github.com/nxtlo/sain/tree/master/examples)

### `cfg`, `cfg_attr` and Marking objects.
Conditionally include code at runtime and mark objects.

```py
from sain import cfg, cfg_attr

@cfg_attr(target_os="unix")
# Calling this on a non-unix system will raise a RuntimeError
# and the function will not run.
def run_when_unix() -> None:
    import uvloop
    uvloop.install()

if cfg(target_arch="arm64"):
    run_when_unix()

# If `cfg` returns True, Function will be in scope.
if cfg(requires_modules="aiohttp"):
    def create_app() -> aiohttp.web.Application:
        # Calling this will raise a runtime error. its marked as `TODO`.
        sain.todo("Finish me!")

# Assuming aiohttp is not installed.
# Calling the function will raise `NameError` since its not in scope.
create_app()

# Those will only warn at runtime and will not raise anything. They're just markers.
@sain.unimplemented(message="User is not fully implemented.")
class User:

    @property
    @sain.deprecated(since = "1.0.4", use_instead="use `get_id` instead.")
    def id(self) -> int:
        ...
```

### `Option<T>` and `Some<T>`
Implements the standard `Option` and `Some` types. An object that may be `None` or `T`.

```py
import sain
import os

if typing.TYPE_CHECKING:
    # Avaliable only during type checking.
    from sain import Option

# Stright up replace typing.Optional[str]
def get_token(key: str) -> Option[str]:
    # What os.getenv returns may be str or None.
    return sain.Some(os.environ.get(key))

# Raises RuntimeError("No token found.") if os.getenv return None.
token = get_token().expect("No token found.")

# The classic way to handle this in Python would be.
if token is None:
    token = "..."
else:
    ...

# Replace this with `unwrap_or`.
# Returning DEFAULT_TOKEN if it was None.
env_or_default = get_token().unwrap_or("DEFAULT_TOKEN")

# Type hint is fine.
as_none: Option[str] = sain.Some(None)
as_none.uwnrap_or(123)  # Error: Must be type `str`!
assert as_none.is_none() # True
```

### Defaults
An interface that types can implement which have a default value.

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

### Iter
Turns normal iterables into `Iter` type.

```py
import sain

f = sain.Iter([1,2,3])
# or f = sain.into_iter([1,2,3])
assert 1 in f

for item in f.map(lambda i: str(i)):
    print(item)
```

### Notes
Since Rust is a compiled language, Whatever predict in `cfg` and `cfg_attr` returns False will not compile.

But there's no such thing as this in Python, So `RuntimeError` will be raised and whatever was predicated will not run.
