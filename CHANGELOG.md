# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).All notable changes to this project will be documented in this file.

## Unreleased

### Added

- `doc` decorator.
- The `Result` type including `OK` and `Err`.
- `ref.ref` function which constructs an `AsRef` object.
- `ref.ref_mut` function which constructs an `AsMut` object.
- `Vec[T]` type.
- `Error` type.

### Changed

- Iterating over `Iter` object with `for` doesn't return `Option[T]` anymore.
- Type hint `Option` isn't required to be under `TYPE_CHECKING` anymore.
- `futures.spawn` now returns `Result[T, E]` and doesn't raise.
- `Iter.async_for_each` now returns `Result[T, E]` and doesn't raise.

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
