"""Tests for the adapter base: timeout retry and env isolation."""

from __future__ import annotations

import subprocess
from pathlib import Path

from agents.base import AgentRunError, isolated_config_env, run_agent_command


def test_timeout_is_retried_once(monkeypatch) -> None:
    calls: list[list[str]] = []

    class _FakeCompleted:
        returncode = 0
        stdout = "done"
        stderr = ""

    def _fake_run(command, **kwargs):
        calls.append(command)
        if len(calls) == 1:
            raise subprocess.TimeoutExpired(cmd=command, timeout=900)
        return _FakeCompleted()

    monkeypatch.setattr("agents.base.subprocess.run", _fake_run)
    result = run_agent_command("kilo", ["kilo", "run"], Path("."), timeout_seconds=1)

    assert result.answer == "done"
    assert "[evals] attempt 1 timed out" in result.stderr
    assert len(calls) == 2


def test_timeout_raises_after_the_second_attempt(monkeypatch) -> None:
    def _fake_run(command, **kwargs):
        raise subprocess.TimeoutExpired(cmd=command, timeout=900)

    monkeypatch.setattr("agents.base.subprocess.run", _fake_run)
    try:
        run_agent_command("kilo", ["kilo", "run"], Path("."), timeout_seconds=1)
    except AgentRunError as error:
        assert "2x1s" in str(error)
    else:
        raise AssertionError("AgentRunError expected")


def test_isolated_config_env_points_xdg_at_a_persistent_directory() -> None:
    override = isolated_config_env()
    assert "XDG_CONFIG_HOME" in override
    assert Path(override["XDG_CONFIG_HOME"]).is_dir()
