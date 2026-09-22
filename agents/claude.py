"""Claude Code harness adapter: non-interactive ``claude -p``."""

from __future__ import annotations

import shutil
from pathlib import Path

from agents.base import AgentResult, run_agent_command


class ClaudeAdapter:
    """Runs one verbatim prompt through the Claude Code CLI (print mode)."""

    name = "claude"

    def __init__(self, model: str | None = None, timeout_seconds: int = 900) -> None:
        self.model = model
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def is_available() -> bool:
        """True when the CLI is installed and on PATH."""
        return shutil.which("claude") is not None

    def build_command(self, prompt: str, cwd: Path, scenario_id: str) -> list[str]:
        """Build the argv for one non-interactive run (cwd carries the fixture)."""
        command = ["claude", "-p", prompt, "--output-format", "text"]
        if self.model is not None:
            command += ["--model", self.model]
        return command

    def run(self, prompt: str, cwd: Path, scenario_id: str) -> AgentResult:
        """Execute the prompt; the plain stdout is the answer."""
        command = self.build_command(prompt, cwd, scenario_id)
        return run_agent_command(self.name, command, cwd, self.timeout_seconds)
