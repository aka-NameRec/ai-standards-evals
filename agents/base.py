"""Adapter contract for external coding agents."""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

DEFAULT_TIMEOUT_SECONDS = 900


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
    """Execute one agent command and capture stdout, stderr, and the raw answer."""
    started = time.monotonic()
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            cwd=str(cwd),
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        msg = f"{adapter} run timed out after {timeout_seconds}s in {cwd}"
        raise AgentRunError(msg) from error
    duration = time.monotonic() - started
    return AgentResult(
        adapter=adapter,
        command=tuple(command),
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
        duration_seconds=duration,
        answer=result.stdout.strip(),
    )


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
