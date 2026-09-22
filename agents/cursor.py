"""Cursor harness adapter: non-interactive ``cursor-agent -p``."""

from __future__ import annotations

import shutil
from pathlib import Path

from agents.base import AgentResult, run_agent_command


class CursorAdapter:
    """Runs one verbatim prompt through the Cursor Agent CLI (print mode)."""

    name = "cursor"

    def __init__(self, model: str | None = None, timeout_seconds: int = 900) -> None:
        self.model = model
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def is_available() -> bool:
        """True when the CLI is installed and on PATH."""
        return shutil.which("cursor-agent") is not None or shutil.which("cursor") is not None

    def build_command(self, prompt: str, cwd: Path, scenario_id: str) -> list[str]:
        """Build the argv for one non-interactive run (cwd carries the fixture)."""
        binary = "cursor-agent" if shutil.which("cursor-agent") else "cursor"
        command = [binary, "-p", prompt]
        if self.model is not None:
            command += ["--model", self.model]
        return command

    def run(self, prompt: str, cwd: Path, scenario_id: str) -> AgentResult:
        """Execute the prompt; the plain stdout is the answer."""
        command = self.build_command(prompt, cwd, scenario_id)
        return run_agent_command(self.name, command, cwd, self.timeout_seconds)
