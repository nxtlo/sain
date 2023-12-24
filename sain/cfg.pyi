import typing as _typing
from collections.abc import Callable

type System = _typing.Literal["linux", "win32", "darwin", "unix", "windows"]
type Arch = _typing.Literal["x86", "x64", "arm", "arm64"]
type Python = _typing.Literal["CPython", "PyPy", "IronPython", "Jython"]

def cfg_attr[F: Callable[..., object]](
    *,
    requires: str | None = ...,
    target_os: System | None = ...,
    python_version: tuple[int, int, int] | None = ...,
    target_arch: Arch | None = ...,
    impl: Python | None = ...,
) -> Callable[[F], F]: ...
def cfg(
    *,
    target_os: System | None = ...,
    requires: str | None = ...,
    python_version: tuple[int, int, int] | None = ...,
    target_arch: Arch | None = ...,
    impl: Python | None = ...,
) -> bool: ...

class _AttrCheck[F: Callable[..., object]]:
    def __init__(
        self,
        callback: F,
        target_os: System | None = ...,
        requires: str | None = ...,
        python_version: tuple[int, int, int] | None = ...,
        target_arch: Arch | None = ...,
        impl: Python | None = ...,
        *,
        no_raise: bool = ...,
    ) -> None: ...
    def __call__(self, *args: _typing.Any, **kwds: _typing.Any) -> F: ...
    def internal_check(self) -> bool: ...
