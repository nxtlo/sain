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

"""Temporal quantification"""

from __future__ import annotations

import typing

__all__ = ("Duration",)

import datetime
import sys

NANOS_PER_SEC = 1_000_000_000
NANOS_PER_MILLI = 1_000_000
NANOS_PER_MICRO = 1_000
MILLIS_PER_SEC = 1_000
MICROS_PER_SEC = 1_000_000
SECS_PER_MINUTE = 60
MINS_PER_HOUR = 60
HOURS_PER_DAY = 24
DAYS_PER_WEEK = 7


@typing.final
class Duration:
    """A `Duration` type, used to represent a span of time, usually used for system timeouts.

    Each `Duration` is composed of a number of seconds and a fractional part represented
    as `nanoseconds`.

    It includes core methods inherited from `std::time::Duration`.

    `Duration` implement many common operators such as `+`, `-`, `*` and many more.

    Example
    -------
    ```py
    five_seconds = Duration(5, 0)
    ten_seconds = five_seconds * Duration(2, 0)
    assert ten_seconds.as_secs() == 10

    ten_milli_secs = Duration.from_millis(10)
    ```
    """

    __slots__ = ("_secs", "_nanos")
    _secs: int
    _nanos: int

    # These are lazily initialized at the end.

    SECOND: typing.ClassVar[Duration]
    """The duration of one second.

    Example
    -------
    ```py
    from sain.time import Duration

    assert Duration.SECOND, Duration.from_secs(1)
    ```
    """

    MILLISECOND: typing.ClassVar[Duration]
    """The duration of one millisecond.

    Example
    -------
    ```py
    from sain.time import Duration

    assert Duration.MILLISECOND == Duration.from_millis(1)
    ```
    """

    MICROSECOND: typing.ClassVar[Duration]
    """The duration of one microsecond.

    Example
    -------
    ```py
    from sain.time import Duration

    assert Duration.MICROSECOND == Duration.from_micros(1)
    ```
    """

    NANOSECOND: typing.ClassVar[Duration]
    """The duration of one nanosecond.

    Example
    -------
    ```py
    from sain.time import Duration

    assert Duration.NANOSECOND == Duration.from_nanos(1)
    ```
    """

    ZERO: typing.ClassVar[Duration]
    """The zero duration.

    Example
    -------
    ```py
    from sain.time import Duration

    assert Duration.ZERO == Duration(0, 0)
    ```
    """

    MAX: typing.ClassVar[Duration]
    """The maximum possible duration.

    Example
    -------
    ```py
    from sain.time import Duration

    assert Duration.MAX.as_secs() == sys.maxsize
    ```
    """

    def __init__(self, secs: int, nanos: int, /) -> None:
        self._secs = secs
        self._nanos = nanos

    def __new__(cls, secs: int, nanos: int, /) -> Duration:
        if secs < 0:
            raise ValueError("`secs` must be non-negative.")

        new = super().__new__(cls)
        if nanos < NANOS_PER_SEC:
            new._secs = secs
            new._nanos = nanos
        else:
            extra_secs = nanos // NANOS_PER_SEC
            try:
                new._secs = secs + extra_secs
            except OverflowError as e:
                raise OverflowError("overflow in Duration.__new__") from e
            new._nanos = nanos % NANOS_PER_SEC

        return new

    @classmethod
    def from_timedelta(cls, delta: datetime.timedelta) -> Duration:
        """Creates a `Duration` new from a `timedelta`.

        Example
        -------
        ```py
        duration = Duration.from_timedelta(datetime.timedelta(minutes=1, seconds=30))
        assert duration.as_secs() == 90
        ```
        """
        nanos = int(delta.total_seconds() * NANOS_PER_SEC)
        return Duration.from_nanos(nanos)

    @classmethod
    def from_secs(cls, secs: int) -> Duration:
        """Creates a `Duration` new representing the given number of seconds.

        Example
        -------
        ```py
        duration = Duration.from_secs(10)
        assert duration.as_secs() == 10
        ```
        """
        return Duration(secs, 0)

    @classmethod
    def from_millis(cls, n: int) -> Duration:
        """Creates a `Duration` new representing the given number of milliseconds.

        Example
        -------
        ```py
        duration = Duration.from_millis(1500)
        assert duration.as_secs() == 1
        assert duration.subsec_millis() == 500
        ```
        """
        secs = n // MILLIS_PER_SEC
        nanos = (n % MILLIS_PER_SEC) * NANOS_PER_MILLI
        return cls(secs, nanos)

    @classmethod
    def from_micros(cls, n: int) -> Duration:
        """Creates a `Duration` new representing the given number of microseconds.

        Example
        -------
        ```py
        duration = Duration.from_micros(1_500_000)
        assert duration.as_secs() == 1
        assert duration.subsec_micros() == 500_000
        ```
        """
        secs = n // MICROS_PER_SEC
        nanos = (n % MICROS_PER_SEC) * NANOS_PER_MICRO
        return cls(secs, nanos)

    @classmethod
    def from_nanos(cls, n: int) -> Duration:
        """Creates a `Duration` new representing the given number of nanoseconds.

        Example
        -------
        ```py
        duration = Duration.from_nanos(1_500_000_000)
        assert duration.as_secs() == 1
        assert duration.subsec_nanos() == 500_000_000
        ```
        """
        secs = n // NANOS_PER_SEC
        nanos = n % NANOS_PER_SEC
        return cls(secs, nanos)

    @classmethod
    def from_weeks(cls, n: int) -> Duration:
        """Creates a `Duration` new representing the given number of weeks.

        Example
        -------
        ```py
        duration = Duration.from_weeks(2)
        assert duration.as_secs() == 2 * 7 * 24 * 60 * 60
        ```
        """
        return cls(
            n * DAYS_PER_WEEK * HOURS_PER_DAY * MINS_PER_HOUR * SECS_PER_MINUTE, 0
        )

    @classmethod
    def from_days(cls, n: int) -> Duration:
        """Creates a `Duration` new representing the given number of days.

        Example
        -------
        ```py
        duration = Duration.from_days(3)
        assert duration.as_secs() == 3 * 24 * 60 * 60
        ```
        """
        return cls(n * HOURS_PER_DAY * MINS_PER_HOUR * SECS_PER_MINUTE, 0)

    @classmethod
    def from_hours(cls, n: int) -> Duration:
        """Creates a `Duration` new representing the given number of hours.

        Example
        -------
        ```py
        duration = Duration.from_hours(5)
        assert duration.as_secs() == 5 * 60 * 60
        ```
        """
        return cls(n * MINS_PER_HOUR * SECS_PER_MINUTE, 0)

    @classmethod
    def from_mins(cls, n: int) -> Duration:
        """Creates a `Duration` new representing the given number of minutes.

        Example
        -------
        ```py
        duration = Duration.from_mins(3)
        assert duration.as_secs() == 3 * 60
        ```
        """
        return cls(n * SECS_PER_MINUTE, 0)

    def is_zero(self) -> bool:
        """Returns True if the duration is zero (both seconds and nanoseconds are zero).

        Example
        -------
        ```py
        duration = Duration(0, 0)
        assert duration.is_zero() is True

        duration = Duration(1, 0)
        assert duration.is_zero() is False
        ```
        """
        return self._secs == 0 and self._nanos == 0

    def as_secs(self) -> int:
        """Returns the number of whole seconds in the duration as an integer.

        This does not return the included fractional (nanosecond) part of the
        duration, this can be returned by using `subsec_nanos`.

        Example
        -------
        ```py
        duration = Duration(5, 500_000_000)
        assert duration.as_secs() == 5
        ```
        """
        return self._secs

    def subsec_millis(self) -> float:
        """Returns the fractional part of this `Duration` in a whole milliseconds.

        Example
        -------
        ```py
        duration = Duration(1, 500_000_000)
        assert duration.subsec_millis() == 500.0
        ```
        """
        return self._nanos / NANOS_PER_MILLI

    def subsec_micros(self) -> float:
        """Returns the fractional part of this `Duration` in a whole microseconds.

        Example
        -------
        ```py
        duration = Duration(1, 500_000)
        assert duration.subsec_micros() == 500.0
        ```
        """
        return self._nanos / NANOS_PER_MICRO

    def subsec_nanos(self) -> int:
        """Returns the fractional part of this `Duration` in a whole nanoseconds.

        Example
        -------
        ```py
        duration = Duration.from_millis(5_010)
        assert duration.subsec_nanos() == 10_000_000
        ```
        """
        return self._nanos

    def as_millis(self) -> float:
        """Returns the total duration in milliseconds as a floating-point number.

        This includes both the whole seconds and the fractional nanoseconds
        converted into milliseconds.

        Example
        -------
        ```py
        duration = Duration(1, 500_000_000)
        assert duration.as_millis() == 1500.0
        ```
        """
        return self._secs * MILLIS_PER_SEC + (self._nanos / NANOS_PER_MILLI)

    def as_micros(self) -> float:
        """Returns the total duration in microseconds as a floating-point number.

        This includes both the whole seconds and the fractional nanoseconds
        converted into microseconds.

        Example
        -------
        ```py
        duration = Duration(1, 500_000)
        assert duration.as_micros() == 1_000_500.0
        ```
        """
        return self._secs * MICROS_PER_SEC + (self._nanos / NANOS_PER_MICRO)

    def as_nanos(self) -> int:
        """Returns the total duration in nanoseconds as an integer.

        This includes both the whole seconds and the fractional nanoseconds.

        Example
        -------
        ```py
        duration = Duration(1, 500_000_000)
        assert duration.as_nanos() == 1_500_000_000
        ```
        """
        return self._secs * NANOS_PER_SEC + self._nanos

    def __add__(self, rhs: Duration) -> Duration:
        if type(rhs) is not Duration:
            raise TypeError("rhs must be of type `Duration`")

        secs = self._secs + rhs._secs
        nanos = self._nanos + rhs._nanos
        return Duration(secs, nanos)

    def __sub__(self, rhs: Duration) -> Duration:
        if type(rhs) is not Duration:
            raise TypeError("rhs must be of type `Duration`")

        if self._nanos >= rhs._nanos:
            return Duration(self._secs - rhs._secs, self._nanos - rhs._nanos)
        return Duration(
            self._secs - rhs._secs - 1, NANOS_PER_SEC + self._nanos - rhs._nanos
        )

    def __mul__(self, rhs: Duration) -> Duration:
        if type(rhs) is not Duration:
            raise TypeError("rhs must be of type `Duration`")

        total_nanos = (self._secs * NANOS_PER_SEC + self._nanos) * (
            rhs._secs * NANOS_PER_SEC + rhs._nanos
        )
        secs = total_nanos // NANOS_PER_SEC
        nanos = total_nanos % NANOS_PER_SEC
        return Duration(secs, nanos)

    def __iadd__(self, rhs: Duration) -> Duration:
        if type(rhs) is not Duration:
            raise TypeError("rhs must be of type `Duration`")

        self._secs += rhs._secs
        self._nanos += rhs._nanos
        if self._nanos >= NANOS_PER_SEC:
            self._secs += 1
            self._nanos -= NANOS_PER_SEC
        return self

    def __isub__(self, rhs: Duration) -> Duration:
        if type(rhs) is not Duration:
            raise TypeError("rhs must be of type `Duration`")

        if self._nanos >= rhs._nanos:
            self._nanos -= rhs._nanos
            self._secs -= rhs._secs
        else:
            self._nanos = NANOS_PER_SEC + self._nanos - rhs._nanos
            self._secs = self._secs - rhs._secs - 1
        return self

    def __imul__(self, rhs: Duration) -> Duration:
        if type(rhs) is not Duration:
            raise TypeError("rhs must be of type `Duration`")
        total_nanos = (self._secs * NANOS_PER_SEC + self._nanos) * (
            rhs._secs * NANOS_PER_SEC + rhs._nanos
        )
        self._secs = total_nanos // NANOS_PER_SEC
        self._nanos = total_nanos % NANOS_PER_SEC
        return self

    def __truediv__(self, rhs: Duration) -> float:
        if type(rhs) is not Duration:
            raise TypeError("rhs must be of type `Duration`")
        self_nanos = self._secs * NANOS_PER_SEC + self._nanos
        rhs_nanos = rhs._secs * NANOS_PER_SEC + rhs._nanos
        if rhs_nanos == 0:
            raise ZeroDivisionError("division by zero")
        return self_nanos / rhs_nanos

    def __itruediv__(self, rhs: Duration) -> float:
        if type(rhs) is not Duration:
            raise TypeError("rhs must be of type `Duration`")

        return self.__truediv__(rhs)

    def __repr__(self) -> str:
        return f"Duration(secs={self._secs}, nanos={self._nanos})"


Duration.SECOND = Duration.from_secs(1)
Duration.MILLISECOND = Duration.from_millis(1)
Duration.MICROSECOND = Duration.from_micros(1)
Duration.NANOSECOND = Duration.from_nanos(1)
Duration.ZERO = Duration(0, 0)
Duration.MAX = Duration(sys.maxsize, NANOS_PER_SEC - 1)
