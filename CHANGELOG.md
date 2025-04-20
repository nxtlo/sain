# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).All notable changes to this project will be documented in this file.

## Unreleased

### Added

- `Vec.shirnk_to`
- `Vec.shirnk_to_fit`
- `macros.include_str`
- `macros.include_bytes`
- `macros.assert_eq`
- `macros.assert_ne`
- `iter.Once`
- `iter.ExactSizeIterator`

### Changed

- `iter.once() -> Once[T]` now returns a specialized iterator.

## 1.3.0 - 01/01/2025

### Added

- `Bytes.split_at`
- `Vec.split_at`
- `Iterator.chunks`
- `MaybeUninit.array_assume_init`
- `MaybeUninit.array_assume_init_mut`
- `Bytes.zeroed`
- `Bytes.to_vec`
- `Bytes.fill`
- `Bytes.swap`
- `Bytes.swap_unchecked`
- `Bytes.truncate`
- `Bytes.split_off`
- `Bytes.split_first`
- `Bytes.split_last`
- `Bytes.remove`
- `Bytes.swap_remove`
- `Bytes.put_char`
- `Bytes.extend`
- `Vec.swap`
- `Vec.swap_unchecked`
- `Vec.fill`
- `Iterator.sum`
- `Iterator.position`
- `Iterator.fold`
- `convert.ToString`

### Changed

- Greatly improved the speed of some `Vec` methods.
- Renamed `HashMap.new_mut` to `HashMap.from_mut`
- Specialized implementation for `iter.repeat`

## 1.2.0 - 09/09/2024

### Added

- `HashMap`
- `Bytes.chars`
- `Bytes.as_ptr`
- `Iterator.collect_into`
- `Option.insert`
- `Option.get_or_insert`
- `Option.get_or_insert_with`
- `Option.ok_or`
- `Option.ok_or_else`
- `Option.zip`
- `Option.zip_with`
- `Option.inspect`

### Changed

- Improved performance by removing `nothing_unchecked` calls from methods that return `Option[T]` by replacing with `NOTHING` constant.
- `MaybeUninit` no longer exported to top level.
- `Option.into_inner` renamed to `Option.transpose`
- `Lazy` and `LazyFuture` now take a closure that initialize the value at first access
instead of calling `.set` manually.
- Renamed `Bytes.as_bytes` to `Bytes.to_bytes`

## Removed

- `Option.as_ref`
- `Option.as_mut`
- `Cell` and `RefCell`

## 1.1.0 - 27/06/2024

### Added

- `conversion` interfaces `Into`, `From`, `TryInto` and `TryFrom`.
- `count`, `index` and `sort` methods to `Vec`.
- `macos` alias to `darwin` for `target_os`.
- `ios` support to `target_os`.
- impl `Bytes`

### Changed

- starting from this release, all collections are moved to `collections` instead of being in top-level.
of course, core implementations such as `Vec` are still at top level.

## 09/06/2024

### Added

- `MaybeUninit[T]` type.
- `Iterator` interface which represents `Iterator`  trait in Rust
- Default external adapters for `Iterator`.
- `Vec.push_within_capacity`
- `Vec.reserve`
- `Some.take_if`
- `iter.repeat`

### Changed

- `Option.take` now return `Option[T]` instead of `None`
- Stabilized `Vec.with_capacity` and its fellow methods.
- Calling `RefCell.copy` now increment its ref count when called.
- The repr of `Some(None)` is now `None` instead of `Some(None)`
- Passing a `list` variable when constructing a `Vec` now will point to that list instead of copying it.
- Better documentation on `Vec`
- `vec.vec` is renamed to `vec.from_args`
- `iter.empty` now returns `Empty[T]` instead of `Iter[Never]` with better type hinting.
- Better `repr` for iterators.
- Changed the default value of `Some` from `NoneType` to `Some(None)`

## 0.0.6 - 05/04/2024

### Added

- `@doc` decorator.
- The `Result` type including `OK` and `Err`.
- `Vec[T]` type.
- `Error` type.
- `Box[T]` type. This is not the same as rust's `Box`, Check the object documentation.
- `sync` package which contains the following modules. they're object safe.
  - `lazy.Lazy[T]` and `lazy.LazyFuture[T]`.
  - `once.AsyncOnce[T]` and `once.Once[T]`.
- `Iter.sink` method.
- `RefCell` received two methods, `increment` and `decrement` which increments the ref count of the object its holding.

### Changed

- Iterating over `Iter` object with `for` doesn't return `Option[T]` anymore.
- Type hint `Option` isn't required to be under `TYPE_CHECKING` anymore.
- `futures.spawn` now returns `Result[T, E]` and doesn't raise.
- `Iter.async_for_each` now returns `Result[T, E]` and doesn't raise.
- `ref.AsRef` is now `cell.Cell`, `ref.AsMut` is now `cell.RefCell`.

## 0.0.5

### Added

- `Once` type.
- `Iter.next` now returns `sain.Option[T]` instead of `typing.Optional[T]`.
- `.copied`, `by_ref`, `.async_for_each` methods to the `Iter`.
- `empty` function in `sain.iter` module.
- `once` function in `sain.iter` module.
- `Some.iter` method to the `Some` object.
- `option.NOTHING` default constant.

### Removed

- method `Iter.discard` in favor of `Iter.filter` method.

### Changed

- `casting` parameter in `Iter.collect` renamed to `cast`.

## 0.0.4

## Added

- New decorators defined in module `macros.py`
  - `todo`
  - `unimplemented`
  - `deprecated`
- `futures` module which exports usefull functions for `async` programming.
- `Some.unwrap_unchecked` method.

## Changed

- Python `3.10+` is now required to install sain.
- Use the `collections.abc` and `builtins` for the standard types.
- You need to import `__futures__ annotations` to use `Option<T>` type hint, You also need to import it under `TYPE_CHECKING`.
- Project tree restructure.
- The `Drop` check is now deprecated and no longer can be used.
- The standard types not do not inherit from `Default<T>`
- Drop `pkg_resources` module for `__import__` during `requires_modules` attrs check..

## Removed

- The `Drop` protocol from top-level.

## 0.0.3

## Added

- Examples
- Proper documentation.
- `Drop` protocol and `drop` function.
- `RefMut` type and `as_mut`.
- Tests
- `Default` is now slotted
- `.pyi` stubs.

## Changed

- The `Some` type `__str__` now returns `Some(repr(value))` instead of just `repr(value)`.
- `Ref` now supports `__hash__`.
- `target_os` no accepts `windows` as an alias to `win32`.

## Removed

- `Some.is_none_and` method since it made no sense.

## Fixed

- `sain.cfg()` wasn't working correctly.

## 0.0.2

## Addeed

- A type alias `Option[T]` for `Some[T]`.

## Changed

- Export modules to top level.

## 0.0.1

## Added

- First push

- Added target arch + python impl options.
- Some[T], Default[T], Ref[T], Iter[T] types.

## Changed

- requires_modules option now accepts a sequence instead of tuple.

## Removed

## Fixed

- Fixed a bug where `cfg` was always returning `True`.
