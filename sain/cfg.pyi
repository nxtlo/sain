import collections.abc as _collections
import typing as _typing

import typing_extensions as _typing_extensions

Signature = _typing.TypeVar("Signature", bound=_collections.Callable[..., object])
TARGET_OS: _typing_extensions.TypeAlias = _typing.Literal["linux", "win32", "darwin", "unix", "windows"]
TARGET_ARCH: _typing_extensions.TypeAlias = _typing.Literal["x86", "x64", "arm", "arm64"]
PY_IMPL: _typing_extensions.TypeAlias = _typing.Literal["CPython", "PyPy", "IronPython", "Jython"]

def cfg_attr(
    *,
    requires_modules: str | _collections.Sequence[str] | None = ...,
    target_os: TARGET_OS | None = ...,
    python_version: tuple[int, int, int] | None = ...,
    target_arch: TARGET_ARCH | None = ...,
    impl: PY_IMPL | None = ...,
) -> _collections.Callable[[Signature], Signature]: ...
def cfg(
    *,
    target_os: TARGET_OS | None = ...,
    requires_modules: str | _collections.Sequence[str] | None = ...,
    python_version: tuple[int, int, int] | None = ...,
    target_arch: TARGET_ARCH | None = ...,
    impl: PY_IMPL | None = ...,
) -> bool: ...

class _AttrCheck(_typing.Generic[Signature]):
    def __init__(
        self,
        callback: Signature,
        target_os: TARGET_OS | None = ...,
        requires_modules: str | _collections.Sequence[str] | None = ...,
        python_version: tuple[int, int, int] | None = ...,
        target_arch: TARGET_ARCH | None = ...,
        impl: PY_IMPL | None = ...,
        *,
        no_raise: bool = ...,
    ) -> None: ...
    def __call__(self, *args: _typing.Any, **kwds: _typing.Any) -> Signature: ...
    def internal_check(self) -> bool: ...
