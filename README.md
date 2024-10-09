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


# A layout of some data.
@dataclass
class Layout(Into[Bytes], TryFrom[str, None]):
    tag: str
    content: str

    # converts this layout into a some raw bytes as JSON.
    def into(self) -> Bytes:
        # you probably want to use `json.dumps` here.
        return Bytes.from_str(str({"tag": self.tag, "content": self.content}))

    @classmethod
    def try_from(cls, value: str) -> Result[Layout, None]:
        # implement a conversion from a string to a layout.
        # in case of success, return Ok(layout)
        # and in case of failure, return Ok(None)
        parsed = value.split(".")  # this is an example.
        return Ok(Layout(tag=parsed[0], content=parsed[1]))


@dataclass
class Intrinsic:
    layouts: Vec[Layout] = field(default_factory=Vec)

    # extends the vec from an iterable.
    def add(self, *layouts: Layout):
        self.layouts.extend(layouts)

    # finds an optional layout that's tagged with `pattern`
    def find(self, pattern: str) -> Option[Layout]:
        return self.layouts.iter().find(lambda book: pattern in book.tag)

    # converts the entire buffer into `Bytes`
    def to_payload(self) -> Result[Bytes, None]:
        if not self.layouts:
            return Err(None)

        buffer = Bytes()
        for layout in self.layouts:
            buffer.put_bytes(layout.into())

        return Ok(buffer)


intr = Intrinsic()
intr.add(
    Layout("llm1", "content"),
)
# try to convert the string into a Layout.
match Layout.try_from("llm2.content"):
    case Ok(layout):
        intr.add(layout)  # add it if parsed.
    case Err(_):
        ...  # Error parsing the str.

print(intr.to_payload().unwrap())
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
