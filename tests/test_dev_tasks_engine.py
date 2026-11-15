"""`make serve ENGINE=granian` reaches the container.

Make exports command-line variables to its recipes, so ``ENGINE`` arrives
in this process's environment; compose only forwards what the compose file
names, which is ``WEBSERVER_ENGINE``. The translation happens here, and a
plain ``make serve`` must not pin an engine at all.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import pytest

from scripts import dev_tasks


@pytest.fixture
def serve_kwargs(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """What ``serve()`` hands to ``subprocess.run``: the keyword arguments,
    and the compose command under ``cmd``."""
    captured: dict[str, Any] = {}

    def fake_run(cmd: list[str], **kwargs: Any) -> None:
        captured.update(kwargs, cmd=cmd)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(dev_tasks, "resolve_ports", lambda **_: {})
    for name in ("ENGINE", "WEBSERVER_ENGINE", "LOOP", "WEBSERVER_LOOP"):
        monkeypatch.delenv(name, raising=False)
    # Never this machine's ~/.ssh or ssh-agent, unless a test asks for them.
    monkeypatch.setattr(dev_tasks, "_deploy_agent_ready", lambda env: None)
    return captured


def test_engine_becomes_the_webserver_setting(
    serve_kwargs: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ENGINE", "granian")

    dev_tasks.serve()

    assert serve_kwargs["env"]["WEBSERVER_ENGINE"] == "granian"


def test_loop_becomes_the_webserver_setting(
    serve_kwargs: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    """`make serve LOOP=rloop`, the same way."""
    monkeypatch.setenv("LOOP", "rloop")

    dev_tasks.serve()

    assert serve_kwargs["env"]["WEBSERVER_LOOP"] == "rloop"


def test_plain_serve_pins_no_engine(serve_kwargs: dict[str, Any]) -> None:
    dev_tasks.serve()

    assert "WEBSERVER_ENGINE" not in serve_kwargs["env"]


class TestTheDeployAgent:
    """``make serve`` readies what compose's ``deploy-agent`` service mounts
    from this machine; compose runs it, beside the rest of the stack."""

    @pytest.fixture
    def home(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.chdir(tmp_path)
        return tmp_path

    def _ssh_add(self, monkeypatch: pytest.MonkeyPatch, holds: int) -> list[list[str]]:
        """An ssh-agent that answers ``ssh-add -l`` with ``holds``."""
        ran: list[list[str]] = []

        def run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
            ran.append(cmd)
            return subprocess.CompletedProcess(cmd, holds if cmd[1:] == ["-l"] else 0)

        monkeypatch.setattr(dev_tasks.shutil, "which", lambda _: "/usr/bin/ssh-add")
        monkeypatch.setattr(dev_tasks.subprocess, "run", run)
        return ran

    def test_the_checkout_is_named_at_its_own_path(
        self, home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The agent drives the host's Docker: a path it hands over must be
        the host's."""
        self._ssh_add(monkeypatch, holds=0)
        env: dict[str, str] = {}

        dev_tasks._deploy_agent_ready(env)

        assert env["AEGIS_PROJECT_ROOT"] == str(Path.cwd())

    def test_known_hosts_is_made_so_docker_mounts_a_file(
        self, home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._ssh_add(monkeypatch, holds=0)

        dev_tasks._deploy_agent_ready({})

        assert (home / ".ssh" / "known_hosts").is_file()

    def test_an_agent_holding_no_key_is_given_one(
        self, home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The container signs through the ssh-agent, never the key file."""
        ran = self._ssh_add(monkeypatch, holds=1)

        dev_tasks._deploy_agent_ready({})

        assert ran[0] == ["ssh-add", "-l"] and ran[1][0] == "ssh-add"
        assert len(ran) == 2

    def test_an_agent_holding_a_key_is_left_alone(
        self, home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        ran = self._ssh_add(monkeypatch, holds=0)

        dev_tasks._deploy_agent_ready({})

        assert ran == [["ssh-add", "-l"]]

    def _generated_from(self, home: Path, source: str) -> None:
        (home / ".copier-answers.yml").write_text(
            f"_commit: None\n_src_path: {source}\nproject_name: x\n"
        )

    def test_a_stack_generated_from_a_checkout_runs_its_aegis(
        self, home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The pinned release may predate the agent this checkout's
        templates expect: run the checkout the stack came from."""
        self._ssh_add(monkeypatch, holds=0)
        checkout = home / "aegis-stack"
        checkout.mkdir()
        (checkout / "pyproject.toml").write_text("")
        self._generated_from(home, f"git+file://{checkout}")
        env: dict[str, str] = {}

        dev_tasks._deploy_agent_ready(env)

        assert env["AEGIS_STACK_SOURCE"] == str(checkout)

    def test_a_released_stack_or_a_chosen_checkout_is_left_alone(
        self, home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._ssh_add(monkeypatch, holds=0)
        self._generated_from(home, "gh:lbedner/aegis-stack")
        env: dict[str, str] = {}
        dev_tasks._deploy_agent_ready(env)
        assert "AEGIS_STACK_SOURCE" not in env

        self._generated_from(home, f"git+file://{home}")
        (home / "pyproject.toml").write_text("")
        chosen = {"AEGIS_STACK_SOURCE": "/elsewhere"}
        dev_tasks._deploy_agent_ready(chosen)
        assert chosen["AEGIS_STACK_SOURCE"] == "/elsewhere"
