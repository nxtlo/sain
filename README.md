# sain

a dependency-free library which implements a set of minimal abstraction that brings Rust's ecosystem to Python.
It offers a few of the core Rust features like `Vec<T>` and `Result<T, E>` and more. See the equivalent type section below.

This library provides a type-safe mechanism for writing Python code, such as the `Result<T, E>` and `Option<T>` types,
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
from __future__ import annotations

from sain import Ok, Err
from sain import Some
from sain import Vec

import typing
from dataclasses import dataclass, field

if typing.TYPE_CHECKING:
    # These are just type aliases that have no cost at runtime.
    # __annotations__ needs to be imported.
    from sain import Result, Option


@dataclass
class Chunk:
    tag: str
    data: Option[bytes] = Some(None)


@dataclass
class BlobStore:
    buffer: Vec[Chunk] = field(default_factory=Vec)
    size: int = 1024

    def put(self, tag: str) -> Result[Chunk, str]:
        if self.buffer.len() >= self.size:
            # The return type of the error doesn't have to be a str.
            # its much better to have it an opaque type such as enums
            # or any data type with more context.
            return Err("Reached maximum capacity sry :3")

        chunk = Chunk(tag, Some(f"chunk.{tag}".encode("utf-8")))
        self.buffer.push(chunk)
        return Ok(chunk)

    def next_chunk(self, filtered: str = "") -> Option[Chunk]:
        # this code makes you feel right at home.
        return self
            .buffer
            .iter()
            .take_while(lambda chunk: filtered in chunk.tag)
            .next()


storage = BlobStore()
match storage.put("first"):
    case Ok(chunk):
        print(storage.next_chunk())
    case Err(why):
        print(why)
```

## Equivalent types

- `Option<T>` -> `Option[T]` | `Some[T]`
- `Result<T, E>` -> `Result[T, E]` | `Ok` | `Err`
- `&dyn Error` -> `Error`
- `Vec<T>` -> `Vec[T]`
- `Default<T>` -> `Default[T]`
- `slice::Iter<Item>` -> `Iter[Item]`
- `IntoIterator<Item>` -> `Iterator[Item]`
- `Box<T>` -> `Box[T]`, Not a heap box.
- `cell::Cell<T>` -> `Cell[T]`, Slightly different.
- `cell::RefCell<T>` -> `RefCell[T]`, Slightly different.
- `sync::LazyLock<T>` -> `Lazy[T]`
- `sync::OnceLock<T>` -> `Once[T]`

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
