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

import nox

UNSTABLE_MODULES = ("async_iter",)


@nox.session(reuse_venv=True)
def pdoc(session: nox.Session) -> None:
    session.run_install(
        "uv",
        "sync",
        "--locked",
        "--only-group",
        "docs",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run(
        "pdoc",
        "sain",
        "-d",
        "numpy",
        "-o",
        "./docs",
        "-t",
        "./templates",
    )


@nox.session(reuse_venv=True)
def fmt(session: nox.Session) -> None:
    session.run_install(
        "uv",
        "sync",
        "--locked",
        "--only-group",
        "fmt",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("ruff", "format", "sain")
    session.run("ruff", "check", "sain", "--fix")
    session.run("isort", "sain")


@nox.session(reuse_venv=True)
def pyright(session: nox.Session) -> None:
    session.run_install(
        "uv",
        "sync",
        "--locked",
        "--only-group",
        "type-checking",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("pyright", "sain")


@nox.session(reuse_venv=True)
def pytest(session: nox.Session) -> None:
    session.run_install(
        "uv",
        "sync",
        "--locked",
        "--only-group",
        "tests",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.install("-e", ".")
    session.run("pytest", "tests")


@nox.session(reuse_venv=True)
def slotscheck(session: nox.Session) -> None:
    session.run_install(
        "uv",
        "sync",
        "--locked",
        "--group",
        "lint",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run(
        "slotscheck", "-m", "sain", "--verbose", "--exclude-modules", *UNSTABLE_MODULES
    )


@nox.session(reuse_venv=True)
def codespell(session: nox.Session) -> None:
    session.run_install(
        "uv",
        "sync",
        "--locked",
        "--only-group",
        "lint",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("codespell", "sain", "-w")
