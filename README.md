# sain

a dependency-free library which implements a set of minimal abstraction that brings Rust's ecosystem to Python.
It offers a few of the core Rust features like `Vec<T>` and `Result<T, E>` and more. See the equivalent type section below.

This library provides a type-safe mechanism for writing Python code, such as the `Result<T< E>` and `Option<T>` types,
which provides zero exception handling, where you simply return errors as values.

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
from sain import Some

import typing

if typing.TYPE_CHECKING:
    # These are just type aliases that have no cost at runtime.
    from sain import Result, Option

# Results. a replacement for try/except.
def convert(x: str, y: str) -> Result[float, str]:
    if x.isdigit() and y.isdigit():
        total = sum(map(float, (x, y)))
        return Ok(total)

    return Err("either x or y must be integers.")

# matching on a result.
value = convert("3", "5")
match value:
    case Ok(num):
        print(num)
    case Err(why):
        print(f"An error has occurred: {why}")

# Options, a replacement from typing.Optional
def best_car(model: int) -> Option[str]:
    if model >= 2020:
        return Some("Mazda")

    return Some(None)

# extracting the contained values has drawbacks,
# it will raise a runtime errors, some with context.
value = best_car(2024).expect("bad car.")
# A better way to deal with this is to return a default value.
value = best_car(2019).unwrap_or("a better car")
# An inline unwrap looks like this, the tilde operator acts like `?` in rust.
value = best_car(2015).unwrap() or ~best_car(1999)
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
- `N/A` -> `Box[T]`, This is different from a rust box.

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
