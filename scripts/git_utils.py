"""Shared Git helpers with actionable error context."""

from __future__ import annotations

import subprocess
from pathlib import Path

GIT_TIMEOUT_SECONDS = 120


class GitError(RuntimeError):
    """Raised when a Git command fails."""


def run_git(repo: Path, *args: str, timeout: int = GIT_TIMEOUT_SECONDS) -> str:
    """Run a Git command in ``repo`` and return stripped stdout; raise on failure."""
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if result.returncode != 0:
        msg = f"git {' '.join(args)} failed in {repo}: {result.stderr.strip()}"
        raise GitError(msg)
    return result.stdout.strip()


def run_git_ok(repo: Path, *args: str) -> bool:
    """Run a Git exit-code query (e.g. ``merge-base --is-ancestor``); return success."""
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        timeout=GIT_TIMEOUT_SECONDS,
        check=False,
    )
    return result.returncode == 0
