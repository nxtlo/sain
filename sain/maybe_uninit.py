# BSD 3-Clause License
#
# Copyright (c) 2022-Present, nxtlo
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""A wrapper type to construct uninitialized instances of T."""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from typing_extensions import Self

T = typing.TypeVar("T")


@typing.final
class MaybeUninit(typing.Generic[T]):
    """A wrapper type to construct uninitialized instances of `T`.

    This is kinda equivalent to Rust's `MaybeUninit<T>` wrapper.

    The difference is what's happening under the hood is when initializing an instance of this object,
    nothing really is being initialized, until you call `.write()` to initialize the inner value.

    What??
    -----
    Ok, so `MaybeUninit<T>` is in a sense the unsafe equivalent of `Option<T>`, it either contains a value of type `T`,
    or it contains uninitialized memory (`the attribute doesn't exist`).

    However, `MaybeUninit` is unable to tell you whether the value it contains is `Some(T)` or `None`, So you
    as a programmer is responsible for initializing it.

    And by default, `Option<T>` always contain a default value, which is `None`.

    Examples
    --------
    ```py
    # Create a list of 3 uninitialized strings preallocated.
    pool: list[MaybeUninit[str]] = MaybeUninit.uninit_array(3)
    chars = ['a', 'b', 'c']

    for index, uninit in enumerate(pool):
        uninit.write(chars[index])

    assert all(obj.assume_init() for obj in pool)
    ```
    """

    __slots__ = ("__value",)

    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, value: T) -> None: ...

    def __init__(self, value: T | None = None) -> None:
        if value is None:
            return super().__init__()
        else:
            # we simply pre-initialize the value if it was passed
            # when constructing the instance.
            self.__value = value

    @classmethod
    def uninit(cls) -> Self:
        """Creates a new `MaybeUninit<T>` in an uninitialized state.

        Example
        -------
        ```py
        v: MaybeUninit[str] = MaybeUninit().uninit() # or just MaybeUninit()
        ```
        """
        return cls()

    @classmethod
    def uninit_array(cls, n: int) -> list[Self]:
        """Creates a new list of `MaybeUninit<T>` in an uninitialized state.

        Note that `inner` value doesn't exist in this state until you call `.write` to set it.

        Example
        -------
        ```py
        v : list[MaybeUninit[str]] = MaybeUninit().uninit_array(3)
        assert len(v) == 3
        for uninit in v:
            uninit.write('content')

            initialized = uninit.assume_init()
        ```
        """

        return [cls()] * n

    def assume_init(self) -> T:
        """Get the inner value, assuming that it was initialized by the caller.

        It is unsafe and undefined behavior to call this method on an uninitialized state,

        Example
        -------
        ```py
        uninit: MaybeUninit[int] = MaybeUninit.uninit()
        val = uninit.assume_init() # This is UNSAFE ⚠️

        # Initialize it first.
        uninit.write(0)
        val = uninit.assume_init() # This is safe to access.
        ```

        Raises
        ------
        `LookupError`
            If the `self` is not initialized.
        """
        # SAFETY: the caller must guarantee that `self` is initialized.
        try:
            return self.__value
        except AttributeError:
            raise LookupError("Invalid access to uninitialized value.") from None

    def write(self, value: T) -> T:
        """Sets the value of the `MaybeUninit[T]`.

        This will overwrite any previous values, if was initialized obviously.

        Example
        -------
        ```py
        def scoped(value: MaybeUninit[bytes]) -> MaybeUninit[bytes]:
            response = requests.get("...")
            if response.ok:
                # If ok, initialize.
                value.write(response.content)

            return value

        buffer: MaybeUninit[bytes] = MaybeUninit()
        data = scoped(buffer) # buffer is initialized now.
        print(data.assume_init())
        ```
        """
        self.__write_mangling(value)
        return self.assume_init()

    # These are magic methods to bypass the name mangling.
    def __write_mangling(self, value: T) -> T:
        # A little hack to bypass name dangling.
        object.__setattr__(self, "_MaybeUninit__value", value)
        return value

    def __read_mangling(self) -> T:
        return getattr(self, "_MaybeUninit__value")

    def __repr__(self) -> str:
        try:
            return f"MaybeUninit(value: {self.__read_mangling()!r})"
        except AttributeError:
            return "<uninit>"

    __str__ = __repr__

    def __bool__(self) -> bool:
        """Perform a boolean check on whether the value is initialized or not.

        Example
        -------
        ```py
        v = MaybeUninit[bool]()
        assert not v
        ```
        """
        return hasattr(self, "_MaybeUninit__value")

    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, MaybeUninit):
            return NotImplemented

        if not self or not value:
            # either ones not initialized.
            return False

        return self.__read_mangling() == typing.cast(
            "MaybeUninit[T]", value.__read_mangling()
        )

    def __ne__(self, value: object, /) -> bool:
        return not self.__eq__(value)

    def __hash__(self) -> int:
        return self.__read_mangling().__hash__()
