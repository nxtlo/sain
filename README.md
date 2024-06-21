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

## built-in types

| name in Rust                  | name in Python                   | note                                                                                                                       | restrictions               |
| ----------------------------- | -------------------------------  | -------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| Option\<T>, Some(T), None     | Option[T], Some(T), Some(None)   | Some(None) has the same layout as `None` in Rust                                                                           |                            |
| Result\<T, E>, Ok(T), Err(E)  | Result[T, E], Ok(T), Err(E)      |                                                                                                                            |                            |
| Vec\<T>                       | Vec[T]                           |                                                                                                                            |                            |
| Cell\<T>                      | Cell[T]                          | this isn't an interior mutability type                                                                                     |                            |
| RefCell\<T>                   | RefCell[T]                       | this isn't an interior mutability type                                                                                     |                            |
| LazyLock\<T>                  | Lazy[T]                          |                                                                                                                            |                            |
| OnceLock\<T>                  | Once[T]                          |                                                                                                                            |                            |
| Box\<T>                       | Box[T]                           | this isn't a heap box, [See]([https://nxtlo.github.io/sain/sain/boxed.html](https://nxtlo.github.io/sain/sain/boxed.html)) |                            |
| MaybeUninit\<T>               | MaybeUninit[T]                   | they serve the same purpose, but slightly different                                                                        |                            |
| Default                       | Default[T]                       |                                                                                                                            |                            |
| &dyn Error                    | Error                            |                                                                                                                            |                            |
| Iterator\<T>                  | Iterator[T]                      |                                                                                                                            |                            |
| Iter\<'a, T>                  | Iter[T]                          | collections called by `.iter` are built from this type                                                                     |                            |
| iter::once::\<T>()            | iter.once[T]                     |                                                                                                                            |                            |
| iter::empty::\<T>()           | iter.empty[T]                    |                                                                                                                            |                            |
| iter::repeat::\<T>()          | iter.repeat[T]                   |                                                                                                                            |                            |
| cfg!()                        | cfg()                            | runtime cfg, not all predictions are supported                                                                             |                            |
| #[cfg_attr]                   | @cfg_attr()                      | runtime cfg, not all predictions are supported                                                                             |                            |
| #[doc]                        | @doc()                           | the docs get generated at runtime                                                                                          |                            |
| todo!()                       | todo()                           |                                                                                                                            |                            |
| #[deprecated]                 | @deprecated()                    | will get removed when it get stabilized in `warnings` in Python `3.13`                                                     |                            |
| unimplemented!()              | @unimplemented()                 |                                                                                                                            |                            |

## Notes

Since Rust is a compiled language, Whatever predict in `cfg` and `cfg_attr` returns False will not compile.

But there's no such thing as this in Python, So `RuntimeError` will be raised and whatever was predicated will not run.
