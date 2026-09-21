"""Kilo harness adapter: non-interactive ``kilo run``."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from agents.base import AgentResult


class AgentRunError(RuntimeError):
    """Raised when the agent invocation fails to complete."""


class KiloAdapter:
    """Runs one verbatim prompt through the Kilo CLI in a fixture directory."""

    name = "kilo"

    def __init__(self, model: str, variant: str | None = None, timeout_seconds: int = 900) -> None:
        self.model = model
        self.variant = variant
        self.timeout_seconds = timeout_seconds

    def build_command(self, prompt: str, cwd: Path, scenario_id: str) -> list[str]:
        """Build the argv for one non-interactive run."""
        command = [
            "kilo",
            "run",
            "--dir",
            str(cwd),
            "--auto",
            "--format",
            "json",
            "--model",
            self.model,
            "--title",
            f"eval-{scenario_id}",
        ]
        if self.variant is not None:
            command += ["--variant", self.variant]
        return [*command, prompt]

    def run(self, prompt: str, cwd: Path, scenario_id: str) -> AgentResult:
        """Execute the prompt and capture stdout, stderr, and the extracted answer."""
        command = self.build_command(prompt, cwd, scenario_id)
        started = time.monotonic()
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            msg = f"kilo run timed out after {self.timeout_seconds}s in {cwd}"
            raise AgentRunError(msg) from error
        duration = time.monotonic() - started
        return AgentResult(
            adapter=self.name,
            command=tuple(command),
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            duration_seconds=duration,
            answer=extract_answer(result.stdout),
        )


def extract_answer(stdout: str) -> str:
    """Concatenate assistant text parts from ``kilo run --format json`` events."""
    parts: list[str] = []
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            event = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "text":
            continue
        part = event.get("part")
        if isinstance(part, dict) and isinstance(part.get("text"), str):
            parts.append(part["text"])
    return "\n".join(parts)
