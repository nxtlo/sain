# sain

a dependency-free library that implements some of the Rust core standard types.

This library provides a type-safe mechanism for writing Python code, such as the `Result` and `Option` types,
which provides zero exception handling and errors as values.

This doesn't change the fact that you're still using `Python`, the core point is to provide more idiomatic Rust code
into the Python world with Zero-cost.

## Install

You'll need Python 3.10 or higher.

PyPI

```sh
pip install sain
```

## Overview

Advanced examples in [examples](https://github.com/nxtlo/sain/tree/master/examples)

### Escape the `try/except` mistake

Exceptions sucks, `Result` is simply a better way to avoid runtime exceptions.

```py
from sain import Ok, Err, Result
from dataclasses import dataclass

@dataclass
class Resource[T]:
    object: T


# Note that this is just a simple class that contains 
# info about the error cause and not an actual exception.
@dataclass
class Error:
    url: str
    # reason, http status code.
    cause: tuple[str, int]

def fetch(url: str) -> Result[Resource[bytes], Error]:
    response = http.get(url)
    if response.ok:
        # Ok result.
        return Ok(Resource(response.as_bytes()))

    # An err occurred. we provide an error with some reasonable values.
    return Err(Error(cause=(response.status, response.reason), url=url))

# no try/except.
response = fetch("github.com")
match response:
    case Ok(resource):
        print(resource.object.decode('utf-8'))
    case Err(why):
        print(f"An error has occurred: {why.cause} - {why.url}")

# You can also just unwrap the value, but will raise an error at runtime if it was an Err.
resource = response.unwrap()
# Using `~` operator is equivalent to `?` in Rust.
resource = ~response
```

## Equivalent types

- `Option<T>` -> `Option[T]` | `Some(T)`
- `Result<T, E>` -> `Result[T, E]`
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

### Notes

Since Rust is a compiled language, Whatever predict in `cfg` and `cfg_attr` returns False will not compile.

But there's no such thing as this in Python, So `RuntimeError` will be raised and whatever was predicated will not run.
