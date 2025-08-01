# sain — Write safe Python code like Rust

This library provides Rust's core crates, implemented purely, in Python.
Offering core Rust items such as `Vec<T>`, `Result<T, E>`, `Option<T>`, `Iterator` semantics and more.
You can either look up the source code, or the built-in types section below.

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

## Example

<details>
    <summary>Equivalent Rust code</summary>

```rs
let mut books: Vec<&str> = vec!["Dune", "1984"];
books.push("Foundation");

for book in books.iter().map(|book| book.to_uppercase()) {}

let s = &mut books[..];
let (first, elements) = s.split_first_mut()?;

fn first_element<'a>(slice: &'a [&str]) -> Option<&'a str> {
    slice.first().copied()
}

let fav_book = first_element(&books);
println!("{:?}", fav_book); // Some("Dune")
assert_eq!(fav_book, Some("Dune"));

fn last_or<'a>(err: &'static str, vec: &'a Vec<&str>) -> Result<&'a str, &'static str> {
    vec.last().copied().ok_or(err)
}

// use pattern matching to handle a result.
match last_or("not found", &books) {
    Ok(book) => {
        println!("Last is {book}");
    }
    Err(why) => {
        println!("{why}",);
    }
}
```

</details>

```py
from __future__ import annotations

# Import some of the most primitive types.
from sain import Result, Ok, Err  # used for safe error handling.
from sain import Option, Some  # used for absence of a value, similar to `T | None`.
from sain import Vec  # An extension for builtin `list` type.
from sain.collections import Slice  # a view into some immutable sequence.

# A vec is an extension of a list.
books: Vec[str] = Vec(["Dune", "1984"])
# Vec is by default mutable.
books.push("Foundation")

# inline lazy iteration, thanks to `Iterator`.
for book in books.iter().map(lambda book: book.upper()):
    ...

# There's also a slicing API.
s = books[...] # returns a unique SliceMut<str> off of vec.
# The ~ operator here acts as `?`.
first, elements = ~s.split_first_mut() # Option<(str, SliceMut<str>)>
# Out: "Dune", SliceMut(["1984", "Foundation"])

def first_element(vec: Slice[str]) -> Option[str]:
    # a `Vec` coerces to `SliceMut<T>`, so you can call its methods on it directly.
    return vec.first()

# both `s` and `books` are valid parameters.
fav_book = first_element(books) 
print(fav_book) # Some("Dune")
assert fav_book == Some("Dune")

def last_or(err: str, vec: Vec[str]) -> Result[str, str]:
    return vec.split_last().ok_or(err)

# use pattern matching to handle a result.
match last_or("not found", books):
    case Ok(book):
        print("Last is", book)
    case Err(why):
        print(why)
```

## built-in types

| name in Rust                  | name in Python                   | note                                                                                                                       | restrictions               |
| ----------------------------- | -------------------------------  | -------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| Option\<T>, Some(T), None     | Option[T], Some(T), Some(None)   | Some(None) has the same layout as `None` in Rust                                                                           |                            |
| Result\<T, E>, Ok(T), Err(E)  | Result[T, E], Ok(T), Err(E)      |                                                                            |                            |
| Vec\<T>                       | Vec[T]                           | Same layout as `list[T]`                                                                                                   |                            |
| &[T]                       | Slice[T]                           |                                                                                                    |                            |
| &mut [T]                       | SliceMut[T]                           |                                                                                                    |                            |
| HashMap\<K, V>                | HashMap[K, V]                    | Same layout as `dict[K, V]`                                                                                                |                            |
| bytes::Bytes                  |  Bytes                           |                                                                                                                            |                            |
| bytes::BytesMut               |  BytesMut                        |                                                                                                                            |                            |
| LazyLock\<T>                  | Lazy[T]                          |                                                                                                                            |                            |
| OnceLock\<T>                  | Once[T]                          |                                                                                                                            |                            |
| Box\<T>                       | Box[T]                           | this isn't a heap box                                                                                                      |                            |
| MaybeUninit\<T>               | MaybeUninit[T]                   | they serve the same purpose, but slightly different                                                                        |                            |
| Default                  | Default[T]                       |                                                                                                                       |                            |
| &dyn Error                    | Error                            |                                                                                                                            |                            |
| Iterator\<T>             | Iterator[T]                      |                                                                                                                       |                            |
| Iter\<'a, T>                  | Iter[T]                          | some collections called by `.iter()` are built from this type                                                                   |                            |
| iter::once::\<T>()            | iter.once[T]                     |                                                                                                                            |                            |
| iter::empty::\<T>()           | iter.empty[T]                    |                                                                                                                            |                            |
| iter::repeat::\<T>()          | iter.repeat[T]                   |                                                                                                                            |                            |
| cfg!()                        | cfg()                            | runtime cfg, not all predictions are supported                                                                             |                            |
| #[cfg_attr]                   | @cfg_attr()                      | runtime cfg, not all predictions are supported                                                                             |                            |
| #[doc]                        | @doc()                           | the docs get generated at runtime                                                                                          |                            |
| todo!()                       | todo()                           |                                                                                                                            |                            |
| unimplemented!()              | unimplemented()                 |                                                                                                                            |                            |
| #[deprecated]                 | @deprecated()                    |                                                      |                            |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Performance

don't use Python if you're worried about performance.

## Remaining work

This is still early days for `sain`, it is no where near being stable.
The release cycles were breaking due to poor decision making, but it _should_ be stable enough for general-purpose now.
