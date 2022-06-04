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
"""Protocol for types that can be dropped(deleted)."""
from __future__ import annotations

__all__: tuple[str, str] = ("Drop", "drop")

import typing


@typing.runtime_checkable
class Drop(typing.Protocol):
    """Protocol that types can implement to provide more functionality when
    they get garbage collected.

    Example
    -------
    ```py
    import sain
    import requests
    import dataclasses

    @dataclasses.dataclass
    class Connector(sain.Drop):
        session = requests.Session()

        # Called internally.
        def drop(self) -> None:
            self.session.close()

        def on_drop(self) -> None:
            print("Session is closed...")

        def get(self, url: str) -> requests.Response:
            return self.session.get(url)

    cxn = Connector()
    response = cxn.get("https://example.com")
    print(response.status_code)
    # 200
    # Session is closed...
    ```
    """

    __dropped: bool = False

    def drop(self) -> None:
        """Manually drop an object."""
        raise NotImplementedError("Method `drop` must be implemented.")

    def on_drop(self) -> None:
        """Register a callback to be called when the object is dropped."""
        if not self.__dropped:
            raise RuntimeError("Object not dropped yet.")

    def __del__(self) -> None:
        self.drop()
        self.__dropped = True
        self.on_drop()


def drop(obj: Drop) -> None:
    """Drop objects that implements `Drop`."""
    obj.drop()
