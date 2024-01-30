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


@dataclass
class Error:
    reason: str
    kind: str # Could be an enum.
    url: str

async def fetch(url: str) -> Result[Resource[bytes], Error]:
    async with client.get(url) as response:
        if response.ok:
            # Ok result.
            return Ok(response.as_bytes())

    # An err occurred. we provide an error with some reasonable values.
    return Err(Error(reason="some error reason.", kind="InternalError", url=url))

# no try/except.
response = await fetch("some_url.com")
# You can use `isinstance`, but match basically has a nicer syntax.
match response:
    case Ok(resp):
        print(resp.resource)
    case Err(why):
        print("An error has occurred", why.reason, why.url)
```

## Equivalent types

- `Option<T>` -> `Option[T]` | `Some(T)`
- `Result<T, E>` -> `Result[T, E]`. _WIP_
- `Default<T>` -> `Default[T]`
- `AsRef<T>` -> `AsRef[T]`.
- `AsMut<T>` -> `AsMut[T]`.
- `Iterator<Item>` -> `Iter[Item]`
- `OnceLock<T>` -> `Once[T]`

## Equivalent functions / macros

- `cfg!()` -> `sain.cfg`.
- `todo!()` -> `sain.todo`. This is not a decorator.
- `deprecated!()` -> `sain.deprecated`.
- `unimplemented!()` -> `sain.unimplemented`.
- `#[cfg_attr]` -> `sain.cfg_attr`.
- `#[doc(...)]` -> `sain.doc(...)`.

### Notes

Since Rust is a compiled language, Whatever predict in `cfg` and `cfg_attr` returns False will not compile.

But there's no such thing as this in Python, So `RuntimeError` will be raised and whatever was predicated will not run.
