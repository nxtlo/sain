# sain — Write safe Python code like Rust

a dependency-free which implements Rust's core crates, purely, in Python.
Offering core Rust items such as `Vec<T>`, `Result<T, E>`, `Option<T>` and more. See the built-in types section below.

## Install

Python 3.10 or higher is required.

Using uv:

```sh
uv pip install sain
```

Using pip:

```sh
pip install sain
```

## Overview

sain is built completely on-top of Python's stdlib, inspired by The Rust Standard Library, designed to bring modern,
safe, and ergonomic data structures and utilities to Python.

The goal is to provide developers with high-level abstractions and low-level
control similar to what Rust offers, making it easier to write robust, and maintainable code.

## Example

In this example we are writing a simple app that takes advantage of Rust's types which're implemented in Python.

This example provides a simple library that contains a `Vec` of books. Here, we take advantage of the `Vec` type and its idiomatic methods.

```py
from __future__ import annotations
from sain import Result, Ok, Err  # used for safe error handling.
from sain import Option  # used for absence of a value, similar to `T | None`.
from sain import Vec  # An extension for builtin `list` type.

from dataclasses import dataclass, field

@dataclass
class Book:
    name: str
    author: str
    tags: set[str]
    pages = field(default_factory=set[str])

@dataclass
class Library:
    # just like any other mutable sequences.
    # it needs a default factory.
    books = field(default_factory=Vec[Book])

    # add a books to this library.
    def add(self, *books: Book):
        self.books.extend(books)

    # finds the first book that contains a specific tag.
    def find(self, pattern: str) -> Option[Book]:
        return self.books.iter().find(lambda book: pattern in book.tags)

    # finds the first book that contains a specific tag,
    # mapping Option[Book] to Result[Book, str] where `str` is the context
    # of the error.
    def find_or(self, pattern: str) -> Result[Book, str]:
        return self.find(pattern).ok_or(f"book with pattern {pattern} not found.")

    # We simply filter books that matches `author` and collect them into a list.
    def books_for(self, author: str) -> list[Book]:
        return self.books.iter().filter(lambda book: book.author == author).collect()


lib = Library()
lib.add(
    Book("Twilight", "Stephenie Meyer", {"Vampire", "Romance"}),
    Book("Silo", "Hugh Howey", {"Dystopian", "Sci-Fi"}),
    Book("The Eternaut", "Héctor Germán", {"Invasion", "Mystery"}),
)

# find the first vampire book then maps the book to its pages.
# maps Option[Book] -> Option[set[str]]
for page in lib.find("Vampire").map(lambda book: book.pages).unwrap():
    print(page)  # {page1, page2, ...}

match lib.find_or("Sci-Fi"):
    case Ok(book):
        print(book)  # Book("Silo", ...)
    case Err(err):
        print(err)  # book with pattern Sci-Fi not found.

# show Hugh's books.
print(lib.books_for("Hugh Howey"))  # [Book("Silo", ...)]
```

## built-in types

| name in Rust                  | name in Python                   | note                                                                                                                       | restrictions               |
| ----------------------------- | -------------------------------  | -------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| Option\<T>, Some(T), None     | Option[T], Some(T), Some(None)   | Some(None) has the same layout as `None` in Rust                                                                           |                            |
| Result\<T, E>, Ok(T), Err(E)  | Result[T, E], Ok(T), Err(E)      | Basically a better and more verbose `try/except`                                                                           |                            |
| Vec\<T>                       | Vec[T]                           | Same layout as `list[T]`                                                                                                   |                            |
| HashMap\<K, V>                | HashMap[K, V]                    | Same layout as `dict[K, V]`                                                                                                |                            |
| bytes::Bytes                  |  Bytes                           |                                                                                                                            |                            |
| bytes::BytesMut               |  BytesMut                        |                                                                                                                            |                            |
| LazyLock\<T>                  | Lazy[T]                          |                                                                                                                            |                            |
| OnceLock\<T>                  | Once[T]                          |                                                                                                                            |                            |
| Box\<T>                       | Box[T]                           | this isn't a heap box                                                                                                      |                            |
| MaybeUninit\<T>               | MaybeUninit[T]                   | they serve the same purpose, but slightly different                                                                        |                            |
| impl Default                  | Default[T]                       |                                                                                                                       |                            |
| &dyn Error                    | Error                            |                                                                                                                            |                            |
| impl Iterator\<T>             | Iterator[T]                      |                                                                                                                       |                            |
| Iter\<'a, T>                  | Iter[T]                          | collections called by `.iter()` are built from this type                                                                   |                            |
| iter::once::\<T>()            | iter.once[T]                     |                                                                                                                            |                            |
| iter::empty::\<T>()           | iter.empty[T]                    |                                                                                                                            |                            |
| iter::repeat::\<T>()          | iter.repeat[T]                   |                                                                                                                            |                            |
| cfg!()                        | cfg()                            | runtime cfg, not all predictions are supported                                                                             |                            |
| #[cfg_attr]                   | @cfg_attr()                      | runtime cfg, not all predictions are supported                                                                             |                            |
| #[doc]                        | @doc()                           | the docs get generated at runtime                                                                                          |                            |
| todo!()                       | todo()                           |                                                                                                                            |                            |
| #[deprecated]                 | @deprecated()                    | will get removed when it get stabilized in `warnings` in Python `3.13`                                                     |                            |
| unimplemented!()              | @unimplemented()                 |                                                                                                                            |                            |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Remaining work

This is still early days for `sain`, it is no where near as stable as Python's stdlib.

This project mainly started as a fun / learning experience but turned into something more inspiring.

The release cycles were breaking due to poor decision making at first, but it _should_ be stable enough now.
