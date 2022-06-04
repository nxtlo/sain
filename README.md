# sain
A pure Python package that implements standard Rust core types for Python.


## Install
You'll need Python 3.8 or higher.

PyPI
```rs
$ pip install sain
```

## Example
```py
import sain

#[cfg_attr(target_os = unix)]
@sain.cfg_attr(target_os="unix")
def run_when_unix() -> None:
    import uvloop
    uvloop.install()

# If this returns True, get_token will run, otherwise returns.
if sain.cfg(requires_modules="python-dotenv", python_version=(3, 9, 6)):
    # Stright up replace typing.Optional[str]
    def get_token() -> sain.Option[str]:
        import dotenv
        return sain.Some(dotenv.get_key(".env", "SECRET_TOKEN"))

# Raises RuntimeError("No token found.") if T is None.
token: str = get_token().expect("No token found.")

# Unwrap the value, Returning DEFAULT_TOKEN if it was None.
env_or_default: str = get_token().unwrap_or("DEFAULT_TOKEN")

# type hint is fine.
as_none: sain.Option[str] = sain.Some(None)
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
i like Rust coding style :p

### Notes
Since Rust is a compiled language, Whatever predict returns False will not compile.

But there's no such thing as this in Python, So `RuntimeError` will be raised and whatever was predicated will not run.
