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

`sain` provides a variety of the standard library crates. such as `Vec<T>` and converter interfaces.

```py
from sain import Option, Result, Ok, Err
from sain.collections import Vec
from sain.collections.buf import Bytes
from sain.convert import Into, TryFrom

from dataclasses import dataclass, field


# some blob of data.
@dataclass
class Blob(Into[Bytes], TryFrom[str, None]):
    tag: str
    buffer: bytes

    # converts this layout into some raw bytes.
    def into(self) -> Bytes:
        buf = Bytes()
        buf.put_str(self.tag)
        buf.put_bytes(b"-")
        buf.put_bytes(self.buffer)
        return buf

    @classmethod
    def try_from(cls, value: str) -> Result[Blob, None]:
        # implement a conversion from a string to a blob.
        # in case of success, return Ok(layout)
        # and in case of failure, return Ok(None)
        tag, buffer = value.split(".")  # this is an example.
        return Ok(Blob(tag, buffer.encode()))


@dataclass
class BlobStore:
    buf: Vec[Blob] = field(default_factory=Vec)

    # extends the vec from an iterable.
    def add(self, *blobs: Blob):
        self.buf.extend(blobs)

    # finds blob that's tagged with `pattern`
    def find(self, pattern: str) -> Option[Blob]:
        return self.buf.iter().find(lambda blob: pattern in blob.tag)

    # converts the entire buffer into `Bytes`
    def into_bytes(self) -> Result[Bytes, None]:
        if not self.buf:
            return Err(None)

        buffer = Bytes()
        for blob in self.buf:
            buffer.put_bytes(blob.into())

        return Ok(buffer)


blobstore = BlobStore()
blobstore.add(Blob("safe", b"Rust"))
# try to convert the string into a Layout.
match Blob.try_from("unsafe.Python"):
    case Ok(blob):
        blobstore.add(blob)  # add it if parsed.
    case Err(_):
        ...  # Error parsing the str.

print(blobstore.into_bytes().expect("cannot convert to bytes").to_str())
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
