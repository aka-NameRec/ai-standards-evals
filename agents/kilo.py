"""Kilo harness adapter: non-interactive ``kilo run``."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from agents.base import AgentResult, AgentRunError, run_agent_command


class KiloAdapter:
    """Runs one verbatim prompt through the Kilo CLI in a fixture directory."""

    name = "kilo"

    def __init__(self, model: str, variant: str | None = None, timeout_seconds: int = 900) -> None:
        self.model = model
        self.variant = variant
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def is_available() -> bool:
        """True when the CLI is installed and on PATH."""
        return shutil.which("kilo") is not None

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
        """Execute the prompt and capture stdout, stderr, and the extracted answer.

        An empty answer means the harness produced no assistant output at all
        (server-side connection resets surface this way with exit code 0);
        such a run is retried once, and the retry is recorded in stderr.
        """
        command = self.build_command(prompt, cwd, scenario_id)
        result = run_agent_command(self.name, command, cwd, self.timeout_seconds)
        answer = extract_answer(result.stdout)
        if not answer:
            stderr_note = "[evals] empty answer (no assistant output), retrying once\n"
            result = run_agent_command(self.name, command, cwd, self.timeout_seconds)
            result = AgentResult(
                adapter=result.adapter,
                command=result.command,
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=stderr_note + result.stderr,
                duration_seconds=result.duration_seconds,
                answer=extract_answer(result.stdout),
            )
        if result.returncode != 0 and not result.stdout:
            msg = f"kilo run failed with code {result.returncode}: {result.stderr[:400]}"
            raise AgentRunError(msg)
        return result


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


def skill_invoked(stdout: str) -> bool:
    """Detect a skill tool invocation in ``kilo run --format json`` events."""
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            event = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "tool_use":
            continue
        part = event.get("part")
        if isinstance(part, dict) and str(part.get("tool", "")).lower() == "skill":
            return True
    return False
