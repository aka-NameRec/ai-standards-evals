"""Tests for deterministic fixture builders and the Git history oracle."""

from __future__ import annotations

from pathlib import Path

from scripts.fixtures import build_cr002, build_cr003, build_cr010, build_cr011, build_cr012
from scripts.git_utils import run_git
from scripts.oracle import line_is_preexisting


def _fake_render(worktree: Path, target: Path, revision: str) -> Path:
    rendered = target / "AGENTS.md"
    rendered.write_text("# stub AGENTS.md\n", encoding="utf-8")
    return rendered


def test_build_cr002_fixture_stages_clean_candidate(tmp_path: Path) -> None:
    repo = build_cr002(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    assert (repo / "AGENTS.md").is_file()
    assert (repo / "ai.project.toml").is_file()
    assert run_git(repo, "rev-list", "--count", "HEAD") == "2"
    staged = run_git(repo, "diff", "--cached", "--name-only", "HEAD").splitlines()
    assert "stats.py" in staged
    assert "tests/test_stats.py" in staged
    content = (repo / "stats.py").read_text(encoding="utf-8")
    assert "for payload in values" in content


def test_build_cr003_fixture_history_and_oracle(tmp_path: Path) -> None:
    repo = build_cr003(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    assert run_git(repo, "rev-list", "--count", "HEAD") == "3"
    tags = run_git(repo, "tag", "--list").splitlines()
    assert "v1.0.0" in tags
    assert "v1.1.0" in tags

    lines = (repo / "src" / "reader.ts").read_text(encoding="utf-8").splitlines()
    buggy_line = next(i + 1 for i, text in enumerate(lines) if "i <=" in text)
    candidate_line = next(i + 1 for i, text in enumerate(lines) if "tryParseHeader" in text)

    assert line_is_preexisting(repo, "src/reader.ts", buggy_line) is True
    assert line_is_preexisting(repo, "src/reader.ts", candidate_line) is False


def test_build_cr011_deploys_report_templates(tmp_path: Path, monkeypatch) -> None:
    synced: list[Path] = []

    def _fake_sync(worktree: Path, target: Path, revision: str) -> None:
        synced.append(target)

    monkeypatch.setattr("scripts.fixtures.sync_templates", _fake_sync)
    repo = build_cr011(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    assert synced == [repo]
    staged = run_git(repo, "diff", "--cached", "--name-only", "HEAD").splitlines()
    assert "textkit.py" in staged
    assert "tests/test_textkit.py" in staged


def test_build_cr012_never_deploys_templates(tmp_path: Path, monkeypatch) -> None:
    def _fail_sync(worktree: Path, target: Path, revision: str) -> None:
        msg = "CR-012 must exercise the fallback path without deployed templates"
        raise AssertionError(msg)

    monkeypatch.setattr("scripts.fixtures.sync_templates", _fail_sync)
    repo = build_cr012(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    assert not (repo / ".ai-standards").exists()
    staged = run_git(repo, "diff", "--cached", "--name-only", "HEAD").splitlines()
    assert "textkit.py" in staged


def test_build_cr010_deploys_templates_and_stages_boundary_defect(
    tmp_path: Path, monkeypatch
) -> None:
    synced: list[Path] = []

    def _fake_sync(worktree: Path, target: Path, revision: str) -> None:
        synced.append(target)

    monkeypatch.setattr("scripts.fixtures.sync_templates", _fake_sync)
    repo = build_cr010(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    assert synced == [repo]
    staged = run_git(repo, "diff", "--cached", "--name-only", "HEAD").splitlines()
    assert staged == ["slugkit.py"]
    content = (repo / "slugkit.py").read_text(encoding="utf-8")
    assert "len(text) >= 0" in content
    assert "Succesfully saved" in content
