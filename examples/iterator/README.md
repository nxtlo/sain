# Dealing with the `Iterator` trait

The Iterator pattern allows you to perform some tasks on a sequence of items, which is also responsible for
the logic of iterating over each item and determining when to stop.

The structure of iterators in sain is defined as:

- interfaces: such as `Iterator`, `ExactSizeIterator` and `AsyncIterator`, they're known as traits in Rust which only require and implementation of the `poll_|next` method.
- implementations: such as `Iter`, `TrustedIter`, `Stream`. These are top-level implementations of `Async|Iterator` and the rest of the interfaces, which are ready to use by consumers.
- adapters: like `Enumerate`, `Map`, `Take`. each one of those are adapters returned from `Iterator` it self, They implement a special `__next__` which executes a special operation on each value being yielded.
- functions: these are special functions which return a specialized implementation of an `Iterator`, usually their names tells you exactly what they do. such as `empty()` is an empty iterator.

Go to [iter.py](iters.py) to get started.
