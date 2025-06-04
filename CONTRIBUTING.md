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

For an example:

```py
# Must be type hinted.
def concat(*strs: str) -> str:
  return "".join(strs)

# must be type hinted.
PATH: str = concat("/path", "/to", "/glory")

def main() -> None:
  # inferred, no need to type hint.
  var = concat("")
  # explicit `None` returns is not required.
  return None
```

### Documentation

This project uses numpy style for object documentation, as well as [PEP8].

Examples:

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
  \```

  Safety
  ------
  If the function is marked with `@unsafe`, You must provide an explanation
  on why this function is unsafe.

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
  """"
```

Same thing goes for classes, global constants, methods, etc.

### `typing` and `collections.abc`

* abstract types must be imported from `collections.abc` and not `typing`.
* If the type you're importing in only used for type hints, include it under `TYPE_CHECKING`.
* If a class doesn't allow inheritance, mark it with `@typing.final`.
* Take advantage of `@typing.overload` for better ux.

Example:

```py
# This import must be present in every `.py. file within the project tree.
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
"""The global default generator

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

When implementing an item from Rust, It needs to operate the same as it's implementation in Rust.

Example in Rust:

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
    if overflows_check:
        # nothing represents `Option::None`
        return NOTHING
    return Some(x + y)

# unsafe Rust functions must be marked with the @unsafe decorator.
@unsafe
def unchecked_add(x: int, y: int) -> int:
    return x + y
```

However, functions that panic in Rust, must raise in Python, as well documented
on why it raises.

```rs
fn get_config(p: &Path) -> String {
    std::fs::read_to_string(p).expect("context")
}
```

```py
def get_config(p: Path) -> str:
    if not p.exists():
        raise FileNotFoundError("context")

    return p.open("r").read()
```

### Feature requests

When opening feature request, You need to include a public API section.

When writing your public API, you're allowed to use Python syntax which only available in future versions,
for an example instead of using `Generic[T]`, use the new syntax.

* Using the new generic syntax instead of `Generic[T]`.
* Using `type Value[T] = Class[T]` syntax instead of `TypeAlias`

Example:

#### Public API

```py
# exported to the public.
__all__ = ("Array", "from_fn")

@typing.final  # Cannot be subclassed.
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

The default typechecker we use is `pyright`.
