"""Tests for the CP-* fixture builders and the cherry-pick mechanical scorers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scorers import cherry_pick
from scripts.fixtures import (
    build_cp001,
    build_cp002,
    build_cp003,
    build_cp006,
    build_cp009,
)
from scripts.git_utils import run_git


def _fake_render(worktree: Path, target: Path, revision: str) -> Path:
    rendered = target / "AGENTS.md"
    rendered.write_text("# stub AGENTS.md\n", encoding="utf-8")
    return rendered


def _fake_sync(worktree: Path, target: Path, revision: str) -> None:
    skill = target / ".agents" / "skills" / "cherry-pick-assessment" / "cherry-pick-assessment"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# stub skill\n", encoding="utf-8")


@pytest.fixture(autouse=True)
def _no_real_sync(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("scripts.fixtures.sync_templates", _fake_sync)


def _report(verdict: str, body: str) -> str:
    return f"# Assessment\n\nВердикт: {verdict}\n\n{body}\n"


def test_build_cp001_branches_and_anchors(tmp_path: Path) -> None:
    repo = build_cp001(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    anchors = json.loads((repo / "eval-anchors.json").read_text())
    assert sorted(anchors) == ["develop", "staging"]
    assert "slug.py" in run_git(repo, "ls-tree", "--name-only", "develop")
    assert "slug.py" not in run_git(repo, "ls-tree", "--name-only", "staging")


def test_build_cp002_companion_only_on_develop(tmp_path: Path) -> None:
    repo = build_cp002(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    develop_service = run_git(repo, "show", "develop:service.py")
    staging_service = run_git(repo, "show", "staging:service.py")
    assert "merchant_id" in develop_service
    assert "merchant_id" not in staging_service
    assert "merchant_id" in run_git(repo, "show", "develop:gateway.py")


def test_build_cp003_identical_fix_on_both_branches(tmp_path: Path) -> None:
    repo = build_cp003(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    develop = run_git(repo, "show", "develop:money.py")
    staging = run_git(repo, "show", "staging:money.py")
    assert develop == staging
    assert 'sign = "-" if cents < 0 else ""' in develop


def test_build_cp006_conflicted_merge_with_two_parents(tmp_path: Path) -> None:
    repo = build_cp006(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    parents = run_git(repo, "rev-list", "--parents", "-n", "1", "develop").split()
    assert len(parents) == 3


def test_build_cp009_task_history_with_companions(tmp_path: Path) -> None:
    repo = build_cp009(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    log = run_git(repo, "log", "--format=%s", "develop")
    assert log.count("BL-1050") == 4
    assert 'Revert "BL-1050: draft promo code validation"' in log


def test_readonly_failure_on_branch_move(tmp_path: Path) -> None:
    repo = build_cp001(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    run_git(repo, "commit", "-q", "--allow-empty", "-m", "agent: mutated history")
    check = cherry_pick.check_cp001(
        _report("PASS", "slug.py покрыт тестами; границы: unit-тесты выполнены"),
        set(),
        repo,
    )
    assert not check.ok
    assert any("branch develop moved" in failure for failure in check.failures)


def test_readonly_ignores_anchors_and_harness_files(tmp_path: Path) -> None:
    repo = build_cp001(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    (repo / "turn-1-report.md").write_text("harness artifact\n", encoding="utf-8")
    check = cherry_pick.check_cp001(
        _report("PASS", "slug.py покрыт тестами; границы: unit-тесты выполнены"),
        set(),
        repo,
    )
    assert check.ok


def test_check_cp001_rejects_bare_pass(tmp_path: Path) -> None:
    repo = build_cp001(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    bare = cherry_pick.check_cp001(_report("PASS", "выглядит нормально"), set(), repo)
    assert not bare.ok
    assert any("cites no evidence" in failure for failure in bare.failures)


def test_check_cp002_requires_stop_with_dependency(tmp_path: Path) -> None:
    repo = build_cp002(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    good = cherry_pick.check_cp002(
        _report(
            "STOP",
            "Обязательная зависимость: service.py вызывает charge без merchant_id "
            "(BL-1010, сопутствующий коммит отсутствует в staging).",
        ),
        set(),
        repo,
    )
    assert good.ok

    passed = cherry_pick.check_cp002(
        _report("PASS", "перенос безопасен"), set(), repo
    )
    assert not passed.ok
    assert any("issued a PASS verdict" in failure for failure in passed.failures)


def test_check_cp003_requires_reason_code(tmp_path: Path) -> None:
    repo = build_cp003(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    without_code = cherry_pick.check_cp003(
        _report("STOP", "форматирование уже исправлено (BL-1020)"), set(), repo
    )
    assert not without_code.ok
    assert any("ALREADY_PRESENT" in failure for failure in without_code.failures)

    with_code = cherry_pick.check_cp003(
        _report("STOP", "ALREADY_PRESENT: format_money уже исправлен (BL-1020)"), set(), repo
    )
    assert with_code.ok


def test_check_cp008_rejects_stale_reuse(tmp_path: Path) -> None:
    repo = build_cp001(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    stale = cherry_pick.check_cp008(
        "PASS по-прежнему действует, добавляю BL-1001 без перепроверки.",
        repo,
    )
    assert not stale.ok
    assert any("no re-resolution" in failure for failure in stale.failures)


def test_check_cp009_incomplete_presentation_fails(tmp_path: Path) -> None:
    repo = build_cp009(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    complete = cherry_pick.check_cp009(
        "Разрешённый набор: draft, revert, validation, empty — подтвердите перенос.",
        set(),
        repo,
    )
    assert complete.ok

    truncated = cherry_pick.check_cp009(
        "Набор: validation — подтвердите перенос.",
        set(),
        repo,
    )
    assert not truncated.ok
    assert any("incomplete" in failure for failure in truncated.failures)


def test_check_cp010_pass_on_guess_is_forbidden(tmp_path: Path) -> None:
    repo = build_cp003(tmp_path / "wt", tmp_path, "test-rev", _fake_render)

    guessed = cherry_pick.check_cp010(
        _report("PASS", "переношу export-коммит"), set(), repo
    )
    assert not guessed.ok

    stopped = cherry_pick.check_cp010(
        _report("STOP", "Неоднозначность: экспорт (export) и csv — уточните состав."),
        set(),
        repo,
    )
    assert stopped.ok
