"""Codex harness adapter: non-interactive ``codex exec``."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from agents.base import AgentResult, AgentRunError, run_agent_command

_VSCODE_CODEX_GLOB = (
    "/home/*/.vscode/extensions/openai.chatgpt-*/bin/linux-x86_64/codex"
)


class CodexAdapter:
    """Runs one verbatim prompt through the Codex CLI (exec mode)."""

    name = "codex"
    DEFAULT_SANDBOX = "workspace-write"

    def __init__(
        self,
        model: str | None = None,
        timeout_seconds: int = 900,
        sandbox: str | None = None,
    ) -> None:
        import os

        self.model = model
        self.timeout_seconds = timeout_seconds
        self.sandbox = sandbox or os.environ.get("CODEX_SANDBOX", self.DEFAULT_SANDBOX)

    @staticmethod
    def resolve_binary() -> str | None:
        """Resolve the Codex CLI binary: env, PATH, or the VS Code extension bundle."""
        import os

        env_override = os.environ.get("CODEX_BIN")
        if env_override:
            return env_override
        on_path = shutil.which("codex")
        if on_path:
            return on_path
        matches = sorted(Path("/home").glob(_VSCODE_CODEX_GLOB.replace("/home/*/", "*/")))
        return str(matches[-1]) if matches else None

    @classmethod
    def is_available(cls) -> bool:
        """True when the CLI binary can be resolved."""
        return cls.resolve_binary() is not None

    def build_command(self, prompt: str, cwd: Path, scenario_id: str) -> list[str]:
        """Build the argv for one non-interactive run (cwd carries the fixture)."""
        binary = self.resolve_binary()
        if binary is None:
            msg = "Codex CLI binary not found (CODEX_BIN, PATH, or the VS Code extension)"
            raise AgentRunError(msg)
        command = [
            binary,
            "exec",
            "--cd",
            str(cwd),
            "--skip-git-repo-check",
            "-s",
            self.sandbox,
            "--json",
        ]
        if self.model is not None:
            command += ["--model", self.model]
        return [*command, prompt]

    def run(self, prompt: str, cwd: Path, scenario_id: str) -> AgentResult:
        """Execute the prompt; the answer is extracted from JSONL agent messages."""
        command = self.build_command(prompt, cwd, scenario_id)
        result = run_agent_command(self.name, command, cwd, self.timeout_seconds)
        if result.returncode != 0 and not result.stdout:
            msg = f"codex exec failed with code {result.returncode}: {result.stderr[:400]}"
            raise AgentRunError(msg)
        return AgentResult(
            adapter=result.adapter,
            command=result.command,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            duration_seconds=result.duration_seconds,
            answer=extract_answer(result.stdout),
        )


def extract_answer(stdout: str) -> str:
    """Concatenate agent_message texts from ``codex exec --json`` events."""
    parts: list[str] = []
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            event = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "item.completed":
            continue
        item = event.get("item")
        if isinstance(item, dict) and item.get("type") == "agent_message":
            text = item.get("text")
            if isinstance(text, str):
                parts.append(text)
    return "\n\n".join(parts)


def skill_invoked(stdout: str) -> bool:
    """Codex has no skill machinery; judge scenarios are not applicable."""
    return False
