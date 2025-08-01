# sain — Write safe Python code like Rust 🦀

sain is a dependency-free Python library which brings the Rust ecosystem to Python, Allowing its users to write safe, idiomatic Python code just like Rust.

## What sain provides

If you already know what you are looking for, the fastest way is to use the search bar,

otherwise, you may want to jump into one of these useful sections:

* Fundamental types, such as [slice][].
* [collections][] Implementations of the most common general purpose data structures from Rust's `std::collections` and friends such as [HashMap<K, V>][], `Vec`.
* Core error-handling types such as `Option` and `Some` variant, `Result` and `Ok`, `Err` variants.
* The `Iterator` trait and its adapters.
* Common traits such as `From`, `Into`.
* Synchronization primitives, includes [LazyLock][] and [Once][].
* Support macros such as `#[deprecated]`, `todo!()`, `unimplemented!()` and more.

## A Tour of sain

The next section will include the most general purpose and notable features of Rust implemented in sain.

### Containers and Collections

The [option][] and [result][] modules define optional and error-handling types,
[Option<T>][] and [Result<T, E>][].
The [iter][] module defines the [Iterator][] trait.

For `std::collections` types, sain exposes `Vec` to the top level, which can be imported directly, as for the rest of the types,
they all exist under `sain.collections`, notable ones are:

* [Vec<T>][] - Built on-top of a `list` object, contains all of Rust's [Vec<T>][] methods.
* [HashMap<K, V>][] - Built on-top of a `dict` object, contains all of Rust's [HashMap<K, V>][] methods.
* [Bytes][] and [BytesMut][] - although these are not part of the standard library, it implements `bytes::Bytes` crate.

[slice]: https://nxtlo.github.io/sain/sain/collections/slice.html
[collections]: https://nxtlo.github.io/sain/sain/collections.html
[Vec<T>]: https://nxtlo.github.io/sain/sain/collections/vec.html#Vec
[HashMap<K, V>]: https://nxtlo.github.io/sain/sain/collections/hash_map.html#HashMap
[Bytes]: https://nxtlo.github.io/sain/sain/collections/buf.html#Bytes
[BytesMut]: https://nxtlo.github.io/sain/sain/collections/buf.html#BytesMut
[option]: https://nxtlo.github.io/sain/sain/option.html
[Option<T>]: https://nxtlo.github.io/sain/sain/option.html#Some
[result]: https://nxtlo.github.io/sain/sain/result.html
[Result<T, E>]: https://nxtlo.github.io/sain/sain/result.html#Result
[iter]: https://nxtlo.github.io/sain/sain/iter.html
[Iterator]: https://nxtlo.github.io/sain/sain/iter.html#Iterator
[Once]: https://nxtlo.github.io/sain/sain/sync.html#Once
[LazyLock]: https://nxtlo.github.io/sain/sain/sync.html#Lazy
