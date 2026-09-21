"""Adapter contract for external coding agents."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


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


class AgentAdapter(Protocol):
    """Runs one verbatim prompt against an external agent harness."""

    name: str

    def run(self, prompt: str, cwd: Path, scenario_id: str) -> AgentResult:
        """Execute the prompt in ``cwd`` and capture the outcome."""
        ...
