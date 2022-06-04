# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).All notable changes to this project will be documented in this file.

## Unreleased

## Added
- Examples
- Proper documentation.
- `Drop` protocol and `drop` function.
- `RefMut` type and `as_mut`.
- Tests
- `Default` is now slotted

## Changed
- The `Some` type `__str__` now returns `Some(repr(value))` instead of just `repr(value)`.
- `Ref` now supports `__hash__`.

## Removed
- `Some.is_none_and` method since it made no sense.

## Fixed
- `sain.cfg()` wasn't working correctly.

## 0.0.2
## Addeed
* A type alias `Option[T]` for `Some[T]`.

## Changed
* Export modules to top level.

## 0.0.1
## Added
* First push
* Added target arch + python impl options.
* Some[T], Default[T], Ref[T], Iter[T] types.

## Changed
* requires_modules option now accepts a sequence instead of tuple.

## Removed

## Fixed
- Fixed a bug where `cfg` was always returning `True`.