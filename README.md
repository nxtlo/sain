# sain

a dependency-free library which implements a few of Rust's core crates purely in Python.
It offers a few of the core Rust features such as `Vec<T>`, `Result<T, E>`, `Option<T>` and more. See the equivalent type section below.

a few `std` types are implemented. Check the [project documentation](https://nxtlo.github.io/sain/sain.html)

## Install

You'll need Python 3.10 or higher.

PyPI

```sh
pip install sain
```

## Overview

More examples in [examples](https://github.com/nxtlo/sain/tree/master/examples)

### no `try/except`

Rust doesn't have exception, But `Option<T>` which handles None's, and `Result<T, E>` for returning and propagating errors.
we can easily achieve the same results in Python

```py
from __future__ import annotations

from sain import Option, Result, Ok, Err
from sain.collections import Vec, Bytes
from sain.convert import Into

from dataclasses import dataclass, field


# A chunk of data, the Into protocol allows users to convert the chunk into bytes.
# similar to Rust's Into trait.
@dataclass
class Chunk(Into[bytes]):
    tag: str
    data: Bytes

    # convert a chunk into bytes.
    # in Rust, this consumes `self`, But in Python it copies it.
    def into(self) -> bytes:
        return self.data.to_bytes()


@dataclass
class BlobStore:
    pos: int
    # A buffer that contains chunks of bytes over which we might
    # lazily load from somewhere. This buffer can hold up to 1024 chunks.
    buffer: Vec[Chunk] = field(default_factory=lambda: Vec[Chunk].with_capacity(1024))

    def put(self, tag: str, data: bytes) -> Result[None, str]:
        chunk = Chunk(tag, Bytes.from_bytes(data))
        # push_within_capacity returns `Result[None, Chunk]`.
        # It returns the chunk that got failed to be pushed,
        # we try to push if there's space, mapping the error to
        # a string.
        return self.buffer.push_within_capacity(chunk).map_err(
            lambda chunk: "No more capacity to push chunk: " + str(chunk)
        )

    def next_chunk(self) -> Option[Chunk]:
        chunk = self.buffer.get(self.pos)
        self.pos += 1
        return chunk


def main() -> None:
    blobs = BlobStore(0)

    # upload a blob matching any errors.
    match blobs.put("c1", b"first chunk"):
        case Ok(_):
            print("chunk pushed succefully.")
        case Err(why):
            print(why)

    # or just
    blobs.put("c2", b"second chunk").unwrap()

    # Read back the chunks, and map it to bytes object.
    # in Rust, you would do something similar to
    # * while let Some(chunk) = option.map(String::from_utf8_lossy) { ... } *
    while (chunk := blobs.next_chunk()).is_some():
        print(chunk.map(Chunk.into))

    # use an iterator over the chunks
    for pos, chunk in blobs.buffer.iter().enumerate():
        print(pos, chunk.data)


```

## built-in types

| name in Rust                  | name in Python                   | note                                                                                                                       | restrictions               |
| ----------------------------- | -------------------------------  | -------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| Option\<T>, Some(T), None     | Option[T], Some(T), Some(None)   | Some(None) has the same layout as `None` in Rust                                                                           |                            |
| Result\<T, E>, Ok(T), Err(E)  | Result[T, E], Ok(T), Err(E)      |                                                                                                                            |                            |
| Vec\<T>                       | Vec[T]                           |                                                                                                                            |                            |
| HashMap\<K, V>                      | HashMap[K, V]                          |                                                                                      |                            |
| bytes::Bytes                      |  Bytes                          |                                                                                      |                            |
| LazyLock\<T>                  | Lazy[T]                          |                                                                                                                            |                            |
| OnceLock\<T>                  | Once[T]                          |                                                                                                                            |                            |
| Box\<T>                       | Box[T]                           | this isn't a heap box, [See]([https://nxtlo.github.io/sain/sain/boxed.html](https://nxtlo.github.io/sain/sain/boxed.html)) |                            |
| MaybeUninit\<T>               | MaybeUninit[T]                   | they serve the same purpose, but slightly different                                                                        |                            |
| &dyn Default                       | Default[T]                       |                                                                                                                            |                            |
| &dyn Error                    | Error                            |                                                                                                                            |                            |
| &dyn Iterator\<T>                  | Iterator[T]                      |                                                                                                                            |                            |
| Iter\<'a, T>                  | Iter[T]                          | collections called by `.iter()` are built from this type                                                                     |                            |
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
