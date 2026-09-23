"""Deterministic Git-based oracles for history-dependent scenarios."""

from __future__ import annotations

from pathlib import Path

from scripts.git_utils import run_git, run_git_ok


def blame_commit(repo: Path, path: str, line: int) -> str:
    """Return the commit hash that last touched ``line`` of ``path`` (working tree)."""
    out = run_git(repo, "blame", "-l", "-L", f"{line},{line}", "--", path)
    return out.split(" ", 1)[0].strip()


def line_is_preexisting(repo: Path, path: str, line: int) -> bool:
    """True when the reviewed working-tree change did not introduce ``line``.

    Uncommitted lines blame to the all-zero placeholder hash; anything else means
    the line comes from a committed revision, i.e. it predates the change under
    review.
    """
    commit = blame_commit(repo, path, line)
    return set(commit) != {"0"}


def is_ancestor(repo: Path, commit: str, of: str = "HEAD") -> bool:
    """Exit-code query for ``commit`` being an ancestor of ``of``."""
    return run_git_ok(repo, "merge-base", "--is-ancestor", commit, of)


def changed_files(repo: Path, base: str = "HEAD") -> set[str]:
    """Files changed in the working tree (staged and unstaged) relative to ``base``."""
    out = run_git(repo, "diff", "--name-only", base)
    return {line for line in out.splitlines() if line}


def diff_patch(repo: Path, base: str = "HEAD") -> str:
    """Full patch of the working tree changes relative to ``base``."""
    return run_git(repo, "diff", base)
