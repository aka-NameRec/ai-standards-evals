"""Adapter registry with availability auto-detection."""

from __future__ import annotations

from agents.base import AgentAdapter
from agents.claude import ClaudeAdapter
from agents.codex import CodexAdapter
from agents.cursor import CursorAdapter
from agents.kilo import KiloAdapter

_KILO_MODEL = "zai-coding-plan/glm-5.3-flash"


def build_adapters(
    model: str = _KILO_MODEL,
    timeout_seconds: int = 900,
    wanted: list[str] | None = None,
) -> dict[str, AgentAdapter]:
    """Build every installed adapter (or only the ``wanted`` names), keyed by name."""
    candidates: dict[str, AgentAdapter] = {
        KiloAdapter.name: KiloAdapter(model=model, timeout_seconds=timeout_seconds),
        ClaudeAdapter.name: ClaudeAdapter(
            model=None if model == _KILO_MODEL else model, timeout_seconds=timeout_seconds
        ),
        CodexAdapter.name: CodexAdapter(
            model=None if model == _KILO_MODEL else model, timeout_seconds=timeout_seconds
        ),
        CursorAdapter.name: CursorAdapter(
            model=None if model == _KILO_MODEL else model, timeout_seconds=timeout_seconds
        ),
    }
    if wanted is not None:
        candidates = {name: adapter for name, adapter in candidates.items() if name in wanted}
    return {name: adapter for name, adapter in candidates.items() if adapter.is_available()}
