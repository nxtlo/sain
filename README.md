# sain
A pure Python package that implements standard Rust core types for Python.


## Install
You'll need Python 3.8 or higher.

PyPI
```rs
$ pip install sain
```

## Examples
More stuff in [examples](https://github.com/nxtlo/sain/tree/master/examples)

### `cfg`, `cfg_attr`
Conditionally include code.

```py
from sain import cfg, cfg_attr

@cfg_attr(target_os="unix")
# Calling this on a non-unix system will raise a RuntimeError
# and the function will not run.
def run_when_unix() -> None:
    import uvloop
    uvloop.install()

if cfg(target_arch="arm64")
    run_when_unix()

# If this returns True, Function will be in scope.
if cfg(requires_modules="hikari-tanjun"):
    def create_client() -> tanjun.Client:
        return tanjun.Client(...)

# Assuming tanjun is not installed.
# Calling the function will raise `NameError`
# since its not in scope.
create_client()
```

### `Option<T>` and `Some<T>`
Implements the standard `Option` and `Some` types. An object the may be `None` or `T`.

```py
import sain
import os

# Stright up replace typing.Optional[str]
def get_token(key: str) -> sain.Option[str]:
    # What os.getenv may be str or None
    return sain.Some(os.getenv(key))

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

# Safe type hint is fine.
as_none: sain.Option[str] = sain.Some(None)
as_none.uwnrap_or(123)  # Error: Must be type `str`!
assert as_none.is_none()
```

### Defaults
A protocol that types can implement which have a default value.

```py
import sain
import requests

class Session(sain.Default[requests.Session]):
    # One staticmethod must be implemented and must return the same type.
    @staticmethod
    def default() -> requests.Session:
        return requests.Session()

session = Session.default()
```

### Iter
Turns normal iterables into `Iter` type.

```py
import sain

f = sain.Iter([1,2,3])
# or f = sain.into_iter([1,2,3])
assert 1 in f

for item in f.take_while(lambda i: i > 1):
    print(item)
```

### Why
This is whats Python missing.

### Notes
Since Rust is a compiled language, Whatever predict in `cfg` and `cfg_attr` returns False will not compile.

But there's no such thing as this in Python, So `RuntimeError` will be raised and whatever was predicated will not run.
