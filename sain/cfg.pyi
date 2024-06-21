import typing as _typing
from collections.abc import Callable

type System = _typing.Literal[
    "linux", "win32", "darwin", "macos", "unix", "windows", "ios"
]
type Arch = _typing.Literal["x86", "x86_64", "arm", "arm64"]
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
