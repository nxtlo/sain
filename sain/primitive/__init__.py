from __future__ import annotations

__all__ = (
    "u8",
    "u16",
    "u32",
    "u64",
)

import typing
from sain import Option, Some, NOTHING

if typing.TYPE_CHECKING:
    from typing_extensions import Self
    from _typeshed import ConvertibleToInt


class _Primitive(int):
    def __init__(
        self,
        *,
        ctype: typing.Literal["u8", "u16", "u32", "u64", "u128"],
        bits: int,
        min: int,
        max: int,
    ):
        if self < min or self > max:
            raise OverflowError(
                f"the literal `{self}` does not fit into the type `{ctype}` whose range is `{min}..{max}`"
            )

        self._ctype = ctype
        self._bits = bits
        self._min = min
        self._max = max

    def wrapping_add(self, value: Self) -> int:
        if value >= self._max or value <= self._min:
            return self

        self += value
        return self

    def wrapping_sub(self, value: Self) -> int:
        if value > self._max or value <= self._min:
            self = self._max

        self -= value
        return self

    @classmethod
    def from_str(cls, value: str) -> Self:
        return cls.__new__(cls, value)


# fmt: off
ASCII_CASE_MASK: typing.Final[int] = 0b0010_0000
ASCII_LOWERCASE_TABLE = frozenset((
    97, 98, 99, 100, 101,
    102, 103, 104, 105, 106,
    107, 108, 109, 110, 111,
    112, 113, 114, 115, 116,
    117, 118, 119, 120, 121,
    122,
))
ASCII_UPPERCASE_TABLE = frozenset((
    65, 66, 67, 68,
    69, 70, 71, 72,
    73, 74, 75, 76,
    77, 78, 79, 80,
    81, 82, 83, 84,
    85, 86, 87, 88,
    89, 90,
))
ASCII_DECIMAL_NUMBERS = frozenset((
    48, 49, 50, 51,
    52, 53, 54, 55,
    56, 57,
))
ASCII_OCTA_NUMBERS = frozenset((
    48, 49, 50, 51,
    52, 53, 54, 55,
))
# fmt: on


@typing.final
class u8(_Primitive):
    """The 8-bit unsigned integer type."""

    def __init__(self, _: ConvertibleToInt = 0) -> None:
        super().__init__(ctype="u8", bits=8, min=0, max=255)

    def is_ascii(self) -> bool:
        """Checks if the value is within the ASCII range.

        Examples
        --------
        ```py
        ascii = u8(97)
        non_ascii = u8(150)

        assert ascii.is_ascii()
        assert not non_ascii.is_ascii()
        ```
        """
        return self <= 127

    def as_ascii(self) -> Option[bytes]:
        # TYPE SAFETY: Returning NOTHING is the same as returning Some(None)
        # but we avoid constructing a new Some(None) object.
        return Some(self.to_bytes()) if self.is_ascii() else NOTHING  # pyright: ignore

    def to_ascii_uppercase(self: int) -> u8:
        return u8(self ^ ((self in ASCII_LOWERCASE_TABLE) * ASCII_CASE_MASK))

    def to_ascii_lowercase(self: int) -> u8:
        return u8(self | ((self in ASCII_UPPERCASE_TABLE) * ASCII_CASE_MASK))

    def is_ascii_uppercase(self: int) -> bool:
        return self in ASCII_UPPERCASE_TABLE

    def is_ascii_lowercase(self: int) -> bool:
        return self in ASCII_LOWERCASE_TABLE

    def is_ascii_alphabetic(self: int) -> bool:
        return self in ASCII_UPPERCASE_TABLE or self in ASCII_LOWERCASE_TABLE

    def is_ascii_alphanumeric(self: int) -> bool:
        return (
            self in ASCII_DECIMAL_NUMBERS
            or self in ASCII_LOWERCASE_TABLE
            or self in ASCII_UPPERCASE_TABLE
        )


@typing.final
class u16(_Primitive):
    """The 16-bit unsigned integer type."""

    def __init__(self, _: ConvertibleToInt = 0) -> None:
        super().__init__(ctype="u16", bits=16, min=0, max=65535)


@typing.final
class u32(_Primitive):
    """The 32-bit unsigned integer type."""

    def __init__(self, _: ConvertibleToInt = 0) -> None:
        super().__init__(ctype="u32", bits=8, min=0, max=4294967295)


@typing.final
class u64(_Primitive):
    """The 64-bit unsigned integer type."""

    def __init__(self, _: ConvertibleToInt = 0) -> None:
        super().__init__(ctype="u64", bits=8, min=0, max=18446744073709551615)
