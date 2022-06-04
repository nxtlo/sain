"""Example on how to use the Drop trait."""

import dataclasses

import requests

import sain


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
response = cxn.get("https://Python.org")
print(response.status_code)  # 200
# Session is closed...
