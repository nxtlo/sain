# Developing and Contributing to sain

Thank you for your interest in contributing to sain! There're a variety of ways
to contribute, and a few steps that you need to be aware of.

## Getting Started

This project mainly uses `uv` as the package manager instead of pip, its not required for contributing, but it is highly recommended.

You can install `uv`  from [here](https://docs.astral.sh/uv/getting-started/installation/)

Assuming you cloned the repository, follow the current steps.

Create a virtual environment.

```bash
uv venv
```

Equivalent in pip `python -m venv .venv`

Then enter it:

* On Unix: `source .venv/bin/activate`
* On Windows: `.\.venv\Scripts\activate`

If all good, Follow the next step in [nox](nox).

### nox

nox is a CLI utility helper which tests, generate documentation and check the internal library
using variety of Python tools.

Install process is fairly simple:

```bash
uv sync --group nox
```

Or using pip: `pip install nox[uv]`

You can then list all available sessions by typing `nox -l`

All jobs will need to succeed before anything gets merged.

## Coding style

### Type hints

This project is statically-type checked, which means everything must be type hinted if needed.

#### Example

```py
# Must be type hinted.
def concat(*strs: str) -> str:
    return "".join(strs)

# must be type hinted.
PATH: str = concat("/path", "/to", "/glory")

def main() -> None:
    var = concat("")
    # explicit `None` returns is not required.
```

### Documentation

This project uses numpy style for object documentation, as well as [PEP8].

The documentation has to be Comprehensive like Rust, provided with examples,
warnings, errors with useful diagnostics and contexts and safety.

#### Examples

```py
def add(x: int, y: int) -> int:
    """Calculates `x + y` and return the result.

    An example must be provided if the function isn't trivial.

    Example
    -------
    \```
    # An example that works.
    assert add(1, 2) == 3

    # also provide an example which may error.
    assert add(0, 0) == 1
    \```

    Safety
    ------
    If the function is not marked with `@unsafe`, You must provide an explanation
    on why this function might be unsafe to call.

    Parameters
    ----------
    `x` : `int`
      The first number
    `y` : `int`
      The second number

    If the function does what's not obvious, add a `Returns` block with the explanation.

    Returns
    -------
    `int`
      Returns `x` + `y`, or `sys.maxsize` if any overflow occurs.

    If the function raises a custom exception, which isn't stated under the `Returns` block, add it.

    Raises
    ------
    `OverflowError`
      If `x` + `y` overflows.
    """
```

Same thing goes for classes, global constants, methods, etc.

### `typing` and `collections.abc`

* abstract types must be imported from `collections.abc` and not `typing`.
* If the type you're importing in only used for type hints, include it under `TYPE_CHECKING`.
* If a class doesn't allow inheritance, mark it with `@typing.final`.
* Take advantage of `@typing.overload` for better ux.

#### Example

```py
# This import must be present in every `.py` file within the project tree.
from __future__ import annotations

# after that include the public interface in `__all__` .

__all_ = ("Generator", "DEFAULT_GENERATOR")

import typing

if typing.TYPE_CHECKING:
    import collections.abc as collections
    import datetime

    # generics, no explanation needed.
    # when a class using Generic[T], This needs to be outside of `TYPE_CHECKING`.
    T = typing.TypeVar("T")

@typing.final
class Generator:
    def gen(self) -> collections.Iterator[int]:
        return iter([1, 2, 3, 4])

# Global exports may be marked with `Final`, but not needed.
DEFAULT_GENERATOR: typing.Final[Generator] = Generator()
"""The global generator.

...other docs
"""

# if the return is a known constant, hint it with `typing.Literal[...]`
def _typeof() -> typing.Literal["function", "class"]: ...

# use builtin collection types for returns.
def _to_set(x: collections.Iterable[T]) -> set[T]:
    return set(x)
```

[PEP8]: https://peps.python.org/pep-0008/

### Using `Option<T>` and `Result<T, E>`

tl;dr is, nothing should raise and instead return `Result[T, E]`, and nothing should return `T | None` and instead return `Option[T]`, except only in specific cases.

You're allowed to return `T | None` when:

* A function that transposes from `Option[T]` to `T | None`, such as `Option::transpose()`.
* `T | None` function parameters, arguments.
* Class attributes can also be `T | None`, both are allowed.

Same things goes to `Result[T, E]`, only methods that panic in Rust's side like `.unwrap()`, `.expect()` should raise and error because the caller has full control,
otherwise the function should never raises and instead return `Result`

When implementing an item from Rust, It needs have the same signature as it's implementation in Rust.

#### Example

```rs
const fn checked_add(x: u8, y: u8) -> Option<u8> { x.checked_add(y) }
const unsafe fn unchecked_add(x: u8, y: u8) -> u8 { x.unchecked_add(y) }
```

Ported to Python may look like:

```py
from sain.option import Option, Some, NOTHING
from sain.macros import unsafe

# The signature has to be the same, or close enough to Rust's.
def checked_add(x: int, y: int) -> Option[int]:
    try:
      return Some(x + y)
    except OverflowError:
        # nothing represents `Option::None`
        return NOTHING

# unsafe Rust functions must be marked with the @unsafe decorator.
# This will generate documentation about the safety for this function.
@unsafe
def unchecked_add(x: int, y: int) -> int:
    return x + y
```

However, functions that panic in Rust, must raise in Python, as well documented
on why it raises.

```rs
fn get_config<P: AsRef<Path>>(p: P) -> String {
    std::fs::read_to_string(p.as_ref()).expect("context")
}
```

```py
def get_config(p: Path) -> str:
    # open() raises FileNotFoundError, no need to `try/except` here.
    return p.open("r").read()
```

### Feature requests

When opening a feature request, You need to include a public API section. Which will be exposed to the users of this library.

When writing your public API, you're allowed to use Python syntax which only available in future versions,
for an example instead of using `Generic[T]`, use the new syntax.

* You can use the new generic syntax instead of `Generic[T]`.
* You can use `type Value[T] = Class[T]` syntax instead of `TypeAlias`

This is only for preview, the actual implementation needs to support the syntax of all required Python versions.

Example:

#### Public API

```py
# exported to the public.
__all__ = ("Array", "from_fn")

@typing.final  # if the class cannot be subclassed.
@rustc_diagnostic_item("[T; N]")  # Links to the type in Rust.
class Array[T](collections.Sequence[T], slice.SpecContains[T]):
    def __init__(self, src: collections.Sequence[T]) -> None: ...
    def len(self) -> int: ...
    # If the type is an iterable, provide an `iter` method for it.
    def iter(self) -> iter.TrustedIter[T]: ...
    def is_empty(self) -> bool: ...
    # If the type can be sliced, provide an `as_ref` method for it.
    def as_ref(self) -> slice.Slice[T]: ...

    # rest of the methods...

# public functions are at the lower level of the module.
def from_fn[T](v: collections.Callable[[int], T]) -> Array[T]: ...
def repeat[T](n: int) -> Array[T]: ...
```

## [Type checking](https://www.python.org/dev/peps/pep-0484/)

The default type checker i use is `pyright`.
