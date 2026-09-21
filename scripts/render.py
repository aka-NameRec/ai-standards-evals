"""Render AGENTS.md for a fixture project via the pinned standards renderer."""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

RENDER_TIMEOUT_SECONDS = 600


class RenderError(RuntimeError):
    """Raised when AGENTS.md rendering fails."""


def render_agents_md(worktree: Path, target: Path, revision: str) -> Path:
    """Render ``AGENTS.md`` into ``target`` using the standards checkout at ``worktree``.

    A shared uv environment is keyed by revision so repeated runs stay cheap while
    never mixing renderer versions across revisions.
    """
    env = os.environ.copy()
    env["UV_PROJECT_ENVIRONMENT"] = str(Path(tempfile.gettempdir()) / _venv_name(revision))
    result = subprocess.run(
        ["uv", "run", "--quiet", "ai-sync", "render", "--project-root", str(target)],
        cwd=worktree,
        capture_output=True,
        text=True,
        timeout=RENDER_TIMEOUT_SECONDS,
        env=env,
        check=False,
    )
    if result.returncode != 0:
        msg = f"ai-sync render failed for {target}: {result.stderr.strip()}"
        raise RenderError(msg)
    rendered = target / "AGENTS.md"
    if not rendered.is_file():
        msg = f"ai-sync render reported success but {rendered} is missing"
        raise RenderError(msg)
    return rendered


def _venv_name(revision: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]", "-", revision)
    return f"venv-{safe}"
