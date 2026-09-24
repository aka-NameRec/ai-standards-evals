"""Adapter contract for external coding agents."""

from __future__ import annotations

import os
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

DEFAULT_TIMEOUT_SECONDS = 900

# Spawned agents must not inherit the operator's user-level instructions: the
# eval runs measure the rendered standards, not whatever global guidance the
# workstation carries. An isolated empty config directory achieves that for
# XDG-configured CLIs while leaving the auth store (XDG data dir) untouched.
_ISOLATED_CONFIG_DIR = Path(tempfile.gettempdir()) / "kilo-evals-isolated-config"


def isolated_config_env() -> dict[str, str]:
    """Env override that points XDG config at a persistent empty directory."""
    _ISOLATED_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return {"XDG_CONFIG_HOME": str(_ISOLATED_CONFIG_DIR)}


class AgentRunError(RuntimeError):
    """Raised when the agent invocation fails to complete."""


@dataclass(frozen=True)
class AgentResult:
    """Raw outcome of one agent invocation."""

    adapter: str
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float
    answer: str


def run_agent_command(
    adapter: str,
    command: list[str],
    cwd: Path,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> AgentResult:
    """Execute one agent command and capture stdout, stderr, and the raw answer.

    A timeout is retried once: harness sessions occasionally hang on a single
    slow turn, and a second window resolves it more often than not. The retry
    is recorded in stderr so the artifacts stay honest about it.
    """
    started = time.monotonic()
    stderr_log = ""
    for attempt in (1, 2):
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
                cwd=str(cwd),
                timeout=timeout_seconds,
                check=False,
                env={**_child_env(), **isolated_config_env()},
            )
        except subprocess.TimeoutExpired:
            stderr_log += (
                f"[evals] attempt {attempt} timed out after {timeout_seconds}s in {cwd}\n"
            )
            if attempt == 2:
                duration = time.monotonic() - started
                msg = f"{adapter} run timed out after 2x{timeout_seconds}s in {cwd}"
                raise AgentRunError(msg) from None
            continue
        duration = time.monotonic() - started
        stderr = stderr_log + result.stderr
        return AgentResult(
            adapter=adapter,
            command=tuple(command),
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=stderr,
            duration_seconds=duration,
            answer=result.stdout.strip(),
        )
    msg = f"{adapter} run did not produce a result in {cwd}"  # pragma: no cover
    raise AgentRunError(msg)


def _child_env() -> dict[str, str]:
    return dict(os.environ)


class AgentAdapter(Protocol):
    """Runs one verbatim prompt against an external agent harness."""

    name: str

    @staticmethod
    def is_available() -> bool:
        """True when the harness CLI is installed and on PATH."""
        ...

    def run(self, prompt: str, cwd: Path, scenario_id: str) -> AgentResult:
        """Execute the prompt in ``cwd`` and capture the outcome."""
        ...
