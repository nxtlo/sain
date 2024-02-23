# sain

a dependency-free library that implements some of the Rust core functionalities for Python.

This library provides a type-safe mechanism for writing Python code, such as the `Result` and `Option` types,
which provides zero exception handling and and simply return errors as values.

This doesn't change the fact that you're still using `Python`, the core point is to provide more idiomatic Rust code
as Python code with almost no cost.

multiple `core`/`std` types are implemented in Python. Check the [project documentation](https://nxtlo.github.io/sain/sain.html)

## Install

You'll need Python 3.10 or higher.

PyPI

```sh
pip install sain
```

## Overview

Advanced examples in [examples](https://github.com/nxtlo/sain/tree/master/examples)

### no `try/except`

Exceptions suck, `Result` and `Option` is a much better way to avoid runtime exceptions.

```py
from sain import Ok, Err
from sain import vec
from sain import Some
from sain import Error

import typing

from dataclasses import dataclass

if typing.TYPE_CHECKING:
    # These are just type aliases. `Vec` is an actual object.
    # But since we're using `vec` we just need it as a type hint.
    from sain import Result, Option, Vec

@dataclass
class Resource[T]:
    object: Vec[T]


# Note that this is just a simple class that contains
# info about the error cause and not an actual exception.
# sain provides an `Error` interface that's similar to rusts's `Error` trait.
@dataclass
class HTTPError(Error):
    body: Option[str]
    cause: str
    # This message will be displayed when the error is printed.
    # A more verbose message can be shown by overriding `description` method.
    message: str = "HTTP error occurred"


def fetch(url: str) -> Result[Resource[bytes], Error]:
    response = client.get(url)

    if response.status == 200:
        # Ok result.
        return Ok(Resource(vec(response.bytes())))

    # An err occurred. we provide an error with some reasonable values.
    return Err(
        HTTPError(
            body=Some(response.text()) if response.content_type == "text/html" else Some(None),
            cause="expected bytes",
        )
    )

# no try/except.
response = fetch("github.com")
match response:
    case Ok(resource):
        print(resource.object)
    case Err(why):
        print(f"An error has occurred: {why}")

# You can also just unwrap the value, but will raise an error at runtime if it was an Err.
resource = response.unwrap()
# Using `~` operator is equivalent to `?` in Rust.
resource = ~response
```

## Equivalent types

- `Option<T>` -> `Option[T]` | `Some(T)`
- `Result<T, E>` -> `Result[T, E]` | `Ok(T)` | `Err(T)`
- `Error` -> `Error`
- `Vec<T>` -> `Vec[T]`
- `Default<T>` -> `Default[T]`
- `AsRef<T>` -> `AsRef[T]`
- `AsMut<T>` -> `AsMut[T]`
- `Iterator<Item>` -> `Iter[Item]`
- `OnceLock<T>` -> `Once[T]`

## Equivalent functions / macros

- `cfg!()` -> `sain.cfg`
- `todo!()` -> `sain.todo`. This is not a decorator.
- `deprecated!()` -> `sain.deprecated`
- `unimplemented!()` -> `sain.unimplemented`
- `std::iter::once()` -> `sain.iter.once`
- `std::iter::empty()` -> `sain.iter.empty`
- `#[cfg_attr]` -> `sain.cfg_attr`
- `#[doc(...)]` -> `sain.doc(...)`

## Notes

Since Rust is a compiled language, Whatever predict in `cfg` and `cfg_attr` returns False will not compile.

But there's no such thing as this in Python, So `RuntimeError` will be raised and whatever was predicated will not run.
