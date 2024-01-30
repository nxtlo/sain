import typing

class Ok[T]:
    __slots__: tuple[typing.Literal["_value"]]

    def __init__(self, value: T) -> None: ...

class Err[E]:
    __slots__: tuple[typing.Literal["_value"]]

    def __init__(self, value: E) -> None: ...

type Result[T, E] = Ok[T] | Err[E]
