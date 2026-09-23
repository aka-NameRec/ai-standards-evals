"""Deterministic fixture builders for the code-review scenarios."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from scripts.git_utils import GitError, run_git
from scripts.render import render_agents_md, sync_templates

RenderFn = Callable[[Path, Path, str], Path]

_IDENTITY_ARGS = (
    "-c",
    "user.name=Eval Fixture",
    "-c",
    "user.email=evals@example.invalid",
    "-c",
    "commit.gpgsign=false",
)


class FixtureError(RuntimeError):
    """Raised when a fixture repository cannot be built."""


@dataclass(frozen=True)
class FixtureBuild:
    """Built fixture repository and the scenario-specific oracle anchors."""

    path: Path
    notes: tuple[str, ...] = ()


def has_fixture_builder(scenario_id: str) -> bool:
    """True when a deterministic fixture builder exists for the scenario."""
    return scenario_id in BUILDERS


def build_fixture(
    scenario_id: str,
    worktree: Path,
    parent: Path,
    revision: str,
    render: RenderFn = render_agents_md,
) -> Path | None:
    """Build the fixture for a scenario; return None when the scenario has none."""
    builder = BUILDERS.get(scenario_id)
    if builder is None:
        return None
    return builder(worktree, parent, revision, render)


def build_cr002(worktree: Path, parent: Path, revision: str, render: RenderFn) -> Path:
    """Clean one-line rename plus a new unit test; the no-padding control."""
    repo = parent / "cr-002-review-no-valid-findings"
    _init_repo(repo, worktree, revision, features=["code-review"], stacks=["python"], render=render)
    _write(
        repo / "README.md",
        "# stats-playground\n\nSmall utility library used for internal experiments.\n",
    )
    _write(repo / "conftest.py", "")
    _write(
        repo / "stats.py",
        '"""Small statistics helpers."""\n'
        "\n"
        "\n"
        "def mean(values):\n"
        "    total = 0\n"
        "    for data in values:\n"
        "        total += data\n"
        "    return total / len(values)\n",
    )
    _write(
        repo / "tests" / "test_stats.py",
        "from stats import mean\n"
        "\n"
        "\n"
        "def test_mean():\n"
        "    assert mean([1, 2, 3]) == 2\n",
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "feat: mean helper with basic coverage")

    _write(
        repo / "stats.py",
        '"""Small statistics helpers."""\n'
        "\n"
        "\n"
        "def mean(values):\n"
        "    total = 0\n"
        "    for payload in values:\n"
        "        total += payload\n"
        "    return total / len(values)\n",
    )
    _write(
        repo / "tests" / "test_stats.py",
        "from stats import mean\n"
        "\n"
        "\n"
        "def test_mean():\n"
        "    assert mean([1, 2, 3]) == 2\n"
        "\n"
        "\n"
        "def test_mean_single_value():\n"
        "    assert mean([7]) == 7\n",
    )
    _git(repo, "add", "-A")
    return repo


def build_cr001(worktree: Path, parent: Path, revision: str, render: RenderFn) -> Path:
    """New pricing helper duplicates an existing abstraction outside the diff."""
    repo = parent / "cr-001-duplicate-abstraction-exists"
    _init_repo(
        repo, worktree, revision, features=["code-review"], stacks=["typescript"], render=render
    )
    _write(
        repo / "package.json",
        "{\n"
        '  "name": "eval-fixture-cr001",\n'
        '  "version": "1.0.0",\n'
        '  "private": true,\n'
        '  "scripts": {\n'
        '    "test": "vitest run"\n'
        "  }\n"
        "}\n",
    )
    _write(
        repo / "src" / "money.ts",
        "export function formatMoney(cents: number, currency: string): string {\n"
        '  const symbol = currency === "EUR" ? "\u20ac" : currency === "GBP" ? "\u00a3" : "$";\n'
        "  const negative = cents < 0;\n"
        "  const abs = Math.abs(cents);\n"
        "  const whole = Math.floor(abs / 100);\n"
        '  const frac = String(abs % 100).padStart(2, "0");\n'
        '  const grouped = whole.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",");\n'
        "  return `${negative ? \"-\" : \"\"}${symbol}${grouped}.${frac}`;\n"
        "}\n",
    )
    _write(
        repo / "test" / "money.test.ts",
        'import { describe, expect, it } from "vitest";\n'
        'import { formatMoney } from "../src/money";\n'
        "\n"
        'describe("formatMoney", () => {\n'
        '  it("formats cents with a currency symbol", () => {\n'
        '    expect(formatMoney(12345, "USD")).toBe("$123.45");\n'
        "  });\n"
        "\n"
        '  it("handles negatives", () => {\n'
        '    expect(formatMoney(-501, "EUR")).toBe("-\u20ac5.01");\n'
        "  });\n"
        "});\n",
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "feat: money formatting helper")

    _write(
        repo / "src" / "pricing.ts",
        "export function formatPrice(amount: number, currency: string): string {\n"
        '  const symbols: Record<string, string> = { EUR: "\u20ac", GBP: "\u00a3", USD: "$" };\n'
        "  const negative = amount < 0;\n"
        "  const abs = Math.abs(amount);\n"
        "  const whole = Math.floor(abs / 100);\n"
        '  const frac = String(abs % 100).padStart(2, "0");\n'
        '  let grouped = "";\n'
        "  const digits = whole.toString();\n"
        "  for (let i = 0; i < digits.length; i++) {\n"
        '    if (i > 0 && (digits.length - i) % 3 === 0) grouped += ",";\n'
        "    grouped += digits[i];\n"
        "  }\n"
        '  return `${negative ? "-" : ""}${symbols[currency] ?? "$"}${grouped}.${frac}`;\n'
        "}\n",
    )
    _git(repo, "add", "-A")
    return repo


def build_cr003(worktree: Path, parent: Path, revision: str, render: RenderFn) -> Path:
    """Pre-existing off-by-one in ``readHeaders``; the diff only touches ``parseHeader``."""
    repo = parent / "cr-003-pre-existing-defect-in-fixture"
    _init_repo(
        repo, worktree, revision, features=["code-review"], stacks=["typescript"], render=render
    )
    _write(
        repo / "package.json",
        "{\n"
        '  "name": "eval-fixture-cr003",\n'
        '  "version": "1.1.0",\n'
        '  "private": true,\n'
        '  "scripts": {\n'
        '    "test": "vitest run"\n'
        "  }\n"
        "}\n",
    )
    _write(repo / "src" / "reader.ts", _READER_CLEAN)
    _write(
        repo / "test" / "reader.test.ts",
        'import { describe, expect, it } from "vitest";\n'
        'import { readHeaders } from "../src/reader";\n'
        "\n"
        'describe("readHeaders", () => {\n'
        '  it("parses header lines", () => {\n'
        '    expect(readHeaders(["a: 1", "b: 2"])).toEqual([\n'
        '      { name: "a", value: "1" },\n'
        '      { name: "b", value: "2" },\n'
        "    ]);\n"
        "  });\n"
        "});\n",
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "feat: header reader")
    _git(repo, "tag", "v1.0.0")

    _write(repo / "src" / "reader.ts", _READER_OFF_BY_ONE)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "fix: tolerate trailing input in readHeaders")
    _git(repo, "tag", "v1.1.0")

    _write(repo / "src" / "reader.ts", _READER_CANDIDATE)
    _git(repo, "add", "-A")
    return repo


def build_cr004(worktree: Path, parent: Path, revision: str, render: RenderFn) -> Path:
    """Inverted withdrawal boundary the fixture's own tests never touch."""
    repo = parent / "cr-004-real-correctness-defect"
    _init_repo(repo, worktree, revision, features=["code-review"], stacks=["python"], render=render)
    _write(repo / "conftest.py", "")
    _write(
        repo / "README.md",
        "# ledger-lite\n\nToy ledger used for boundary-condition experiments.\n",
    )
    _write(
        repo / "src" / "account.py",
        '"""Account withdrawal rules."""\n'
        "\n"
        "\n"
        "def can_withdraw(balance: int, amount: int) -> bool:\n"
        '    """Return whether ``amount`` may be withdrawn from ``balance``."""\n'
        "    return amount <= balance\n",
    )
    _write(
        repo / "tests" / "test_account.py",
        "from account import can_withdraw\n"
        "\n"
        "\n"
        "def test_routine_withdrawal():\n"
        "    assert can_withdraw(100, 40) is True\n",
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "feat: withdrawal rule")

    _write(
        repo / "src" / "account.py",
        '"""Account withdrawal rules."""\n'
        "\n"
        "\n"
        "def can_withdraw(balance: int, amount: int) -> bool:\n"
        '    """Return whether ``amount`` may be withdrawn from ``balance``."""\n'
        "    return amount >= balance\n",
    )
    _git(repo, "add", "-A")
    return repo


def build_cr005(worktree: Path, parent: Path, revision: str, render: RenderFn) -> Path:
    """Two new modules carry identical helpers; no reusable abstraction exists."""
    repo = parent / "cr-005-new-internal-duplication"
    _init_repo(repo, worktree, revision, features=["code-review"], stacks=["python"], render=render)
    _write(repo / "conftest.py", "")
    _write(
        repo / "src" / "rows.py",
        '"""Tabular helpers for report modules."""\n'
        "\n"
        "\n"
        "def to_rows(records):\n"
        '    return [[record.get("name", "")] for record in records]\n',
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "feat: reporting scaffolding")

    _format_period = (
        'def format_period(start: str, end: str) -> str:\n'
        '    """Render a reporting period label."""\n'
        "    if start > end:\n"
        "        start, end = end, start\n"
        '    return f"{start}..{end}"\n'
    )
    _csv_header = '"""CSV export for period reports."""\n\n\n'
    _json_header = '"""JSON export for period reports."""\n\n\n'
    _write(repo / "src" / "csv_export.py", _csv_header + _format_period)
    _write(repo / "src" / "json_export.py", _json_header + _format_period)
    _git(repo, "add", "-A")
    return repo


def build_cr006(worktree: Path, parent: Path, revision: str, render: RenderFn) -> Path:
    """API handler writes the repository directly despite the accepted decision."""
    repo = parent / "cr-006-architecture-decision-violation"
    _init_repo(repo, worktree, revision, features=["code-review"], stacks=["python"], render=render)
    _write(repo / "conftest.py", "")
    _write(
        repo / "docs" / "decisions" / "ADR-004.md",
        "# ADR-004: inventory writes go through the reservation service\n"
        "\n"
        "All inventory writes must go through `InventoryReservationService`.\n"
        "Direct repository writes from API handlers are prohibited.\n",
    )
    _write(
        repo / "inventory_service.py",
        '"""Inventory reservation service."""\n'
        "\n"
        "\n"
        "class InventoryReservationService:\n"
        '    """Single write path for inventory mutations."""\n'
        "\n"
        "    def __init__(self, repository):\n"
        "        self._repository = repository\n"
        "\n"
        "    def save(self, item: dict) -> None:\n"
        "        self._repository.save(item)\n",
    )
    _write(
        repo / "inventory_repository.py",
        '"""Low-level inventory storage."""\n'
        "\n"
        "\n"
        "class InventoryRepository:\n"
        '    """Direct storage access; not for API handlers."""\n'
        "\n"
        "    def save(self, item: dict) -> None:\n"
        "        ...",
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "feat: inventory write path with ADR-004")

    _write(
        repo / "api_handler.py",
        '"""API handler for stock adjustments."""\n'
        "\n"
        "from inventory_repository import InventoryRepository\n"
        "\n"
        "\n"
        "def adjust_stock(sku: str, qty: int) -> None:\n"
        "    repository = InventoryRepository()\n"
        "    repository.save({\"sku\": sku, \"qty\": qty})\n",
    )
    _git(repo, "add", "-A")
    return repo


def build_cr007(worktree: Path, parent: Path, revision: str, render: RenderFn) -> Path:
    """New endpoint looks unvalidated in the diff; the router wrapper validates it."""
    repo = parent / "cr-007-apparent-violation-disproved"
    _init_repo(repo, worktree, revision, features=["code-review"], stacks=["python"], render=render)
    _write(repo / "conftest.py", "")
    _write(
        repo / "validation.py",
        '"""Payload validation boundary."""\n'
        "\n"
        "\n"
        "def validate_input(schema, payload):\n"
        '    """Validate ``payload`` against ``schema``; raises on violations."""\n'
        "    if not isinstance(payload, dict):\n"
        '        raise TypeError("payload must be a dict")\n'
        "    return payload\n",
    )
    _write(
        repo / "src" / "register.py",
        '"""Registration endpoints."""\n'
        "\n"
        "from validation import validate_input\n"
        "\n"
        "\n"
        "class RegisterSchema:\n"
        '    """Payload schema for registration requests."""\n'
        "\n"
        "\n"
        "ROUTES = []\n"
        "\n"
        "\n"
        "def route(schema):\n"
        '    """Register a handler under the module-wide validation boundary."""\n'
        "\n"
        "    def wrap(handler):\n"
        "        def wrapped(payload):\n"
        "            return handler(validate_input(schema, payload))\n"
        "\n"
        "        ROUTES.append(wrapped)\n"
        "        return wrapped\n"
        "\n"
        "    return wrap\n"
        "\n"
        "\n"
        "@route(RegisterSchema)\n"
        "def register_user(payload):\n"
        '    return {"ok": True, "user": payload}\n',
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "feat: registration endpoints with validation boundary")

    _write(
        repo / "src" / "register.py",
        _read(repo / "src" / "register.py")
        + "\n\n"
        + "@route(RegisterSchema)\n"
        + "def resend_confirmation(payload):\n"
        + '    return {"ok": True, "queued": True}\n',
    )
    _git(repo, "add", "-A")
    return repo


def build_cr008(worktree: Path, parent: Path, revision: str, render: RenderFn) -> Path:
    """Test suite cannot execute (missing driver); the diff is a pure refactor."""
    repo = parent / "cr-008-verification-unavailable"
    _init_repo(repo, worktree, revision, features=["code-review"], stacks=["python"], render=render)
    _write(repo / "conftest.py", "")
    _write(
        repo / "src" / "formatting.py",
        '"""Report formatting helpers."""\n'
        "\n"
        "\n"
        "def format_title(name: str) -> str:\n"
        "    return name.strip().title()\n",
    )
    _write(
        repo / "tests" / "test_formatting.py",
        "import pytest\n"
        "\n"
        "from formatting import format_title\n"
        "\n"
        "\n"
        "def test_title():\n"
        '    assert format_title("report q3") == "Report Q3"\n'
        "\n"
        "\n"
        "def test_db_backed_titles(db):\n"
        "    assert db\n",
    )
    _write(
        repo / "tests" / "conftest.py",
        "import psycopg2  # noqa: F401 — database driver, absent from the eval environment\n",
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "feat: title formatting with db-backed suite")

    _write(
        repo / "src" / "formatting.py",
        '"""Report formatting helpers."""\n'
        "\n"
        "\n"
        "def format_title(name: str) -> str:\n"
        "    return _title(name)\n"
        "\n"
        "\n"
        "def _title(name: str) -> str:\n"
        "    return name.strip().title()\n",
    )
    _git(repo, "add", "-A")
    return repo


def build_cr009(worktree: Path, parent: Path, revision: str, render: RenderFn) -> Path:
    """New parser gains an error branch; tests cover only the success path."""
    repo = parent / "cr-009-missing-error-path-test"
    _init_repo(repo, worktree, revision, features=["code-review"], stacks=["python"], render=render)
    _write(repo / "conftest.py", "")
    _write(
        repo / "src" / "config.py",
        '"""Config parsing helpers."""\n'
        "\n"
        "\n"
        "def parse_setting(raw: str) -> int:\n"
        '    """Parse a positive integer setting."""\n'
        "    value = int(raw)\n"
        "    if value <= 0:\n"
        '        raise ValueError("must be positive")\n'
        "    return value\n",
    )
    _write(
        repo / "tests" / "test_config.py",
        "import pytest\n"
        "\n"
        "from config import parse_setting\n"
        "\n"
        "\n"
        "def test_setting():\n"
        '    assert parse_setting("5") == 5\n'
        "\n"
        "\n"
        "def test_setting_rejects_zero():\n"
        "    with pytest.raises(ValueError):\n"
        '        parse_setting("0")\n',
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "feat: setting parsing with coverage")

    _write(
        repo / "src" / "config.py",
        _read(repo / "src" / "config.py")
        + "\n\n"
        + "def parse_timeout(text: str) -> int:\n"
        + '    """Parse a timeout in seconds; raises ValueError for non-positive input."""\n'
        + "    value = int(text)\n"
        + "    if value <= 0:\n"
        + '        raise ValueError("timeout must be positive")\n'
        + "    return value\n",
    )
    _write(
        repo / "tests" / "test_config.py",
        _read(repo / "tests" / "test_config.py")
        + "\n\n"
        + "from config import parse_timeout\n"
        + "\n"
        + "\n"
        + "def test_timeout():\n"
        + '    assert parse_timeout("30") == 30\n',
    )
    _git(repo, "add", "-A")
    return repo


def build_cr010(worktree: Path, parent: Path, revision: str, render: RenderFn) -> Path:
    """Boundary defect plus a typo; templates synced for the metadata invariants."""
    repo = parent / "cr-010-report-metadata"
    _init_repo(
        repo,
        worktree,
        revision,
        features=["code-review"],
        stacks=["python"],
        render=render,
        sync=True,
    )
    _write(repo / "conftest.py", "")
    _write(
        repo / "README.md",
        "# slugkit\n\nTiny slug helpers used for internal experiments.\n",
    )
    _write(
        repo / "slugkit.py",
        '"""Slug helpers."""\n'
        "\n"
        "\n"
        "def is_valid_slug(text: str) -> bool:\n"
        '    """Return whether ``text`` is a usable slug."""\n'
        "    return len(text) > 0 and text.strip() == text\n"
        "\n"
        "\n"
        "def save_slug(path, text) -> None:\n"
        '    path.write_text(text, encoding="utf-8")\n'
        '    print("Succesfully saved")\n',
    )
    _write(
        repo / "tests" / "test_slugkit.py",
        "from slugkit import is_valid_slug\n"
        "\n"
        "\n"
        "def test_valid_slug():\n"
        '    assert is_valid_slug("hello-world") is True\n',
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "feat: slug helpers")

    _write(
        repo / "slugkit.py",
        '"""Slug helpers."""\n'
        "\n"
        "\n"
        "def is_valid_slug(text: str) -> bool:\n"
        '    """Return whether ``text`` is a usable slug."""\n'
        "    return len(text) >= 0 and text.strip() == text\n"
        "\n"
        "\n"
        "def save_slug(path, text) -> None:\n"
        '    path.write_text(text, encoding="utf-8")\n'
        '    print("Succesfully saved")\n',
    )
    _git(repo, "add", "-A")
    return repo


def build_cr011(worktree: Path, parent: Path, revision: str, render: RenderFn) -> Path:
    """Self-contained clean change; templates synced so the reporting reference exists."""
    repo = parent / "cr-011-reporting-reference"
    _init_repo(
        repo,
        worktree,
        revision,
        features=["code-review"],
        stacks=["python"],
        render=render,
        sync=True,
    )
    _build_clean_textkit_change(repo)
    return repo


def build_cr012(worktree: Path, parent: Path, revision: str, render: RenderFn) -> Path:
    """Self-contained clean change; sync-templates never runs, so both report
    files are absent and the fallback path is exercised."""
    repo = parent / "cr-012-reporting-fallback"
    _init_repo(repo, worktree, revision, features=["code-review"], stacks=["python"], render=render)
    _build_clean_textkit_change(repo)
    return repo


def _build_clean_textkit_change(repo: Path) -> None:
    """Committed helper plus a clean rename-and-coverage diff (no reportable defects)."""
    _write(repo / "conftest.py", "")
    _write(
        repo / "README.md",
        "# textkit\n\nSmall text utilities for internal tools.\n",
    )
    _write(
        repo / "textkit.py",
        '"""Text utilities."""\n'
        "\n"
        "\n"
        "def shout(text: str) -> str:\n"
        '    """Return ``text`` uppercased."""\n'
        "    result = text\n"
        "    return result.upper()\n",
    )
    _write(
        repo / "tests" / "test_textkit.py",
        "from textkit import shout\n"
        "\n"
        "\n"
        "def test_shout():\n"
        '    assert shout("hi") == "HI"\n',
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "feat: shout helper")

    _write(
        repo / "textkit.py",
        '"""Text utilities."""\n'
        "\n"
        "\n"
        "def shout(text: str) -> str:\n"
        '    """Return ``text`` uppercased."""\n'
        "    return text.upper()\n",
    )
    _write(
        repo / "tests" / "test_textkit.py",
        "from textkit import shout\n"
        "\n"
        "\n"
        "def test_shout():\n"
        '    assert shout("hi") == "HI"\n'
        "\n"
        "\n"
        "def test_shout_keeps_caseless_text():\n"
        '    assert shout("123") == "123"\n',
    )
    _git(repo, "add", "-A")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_trg001(worktree: Path, parent: Path, revision: str, render: RenderFn) -> Path:
    """Tiny project with the standard-code-review skill deployed for activation cases."""
    repo = parent / "trg-001-standard-code-review-triggers"
    _init_repo(
        repo,
        worktree,
        revision,
        features=["code-review"],
        stacks=["typescript"],
        render=render,
        agents=["kilo"],
    )
    _write(
        repo / "src" / "greet.ts",
        "export function greet(name: string): string {\n  return `Hello, ${name}!`;\n}\n",
    )
    _write(
        repo / "src" / "volume.ts",
        "export const shout = (text: string): string => text.toUpperCase();\n",
    )
    _git(repo, "add", "-A")
    return repo


def _init_repo(
    repo: Path,
    worktree: Path,
    revision: str,
    features: list[str],
    stacks: list[str],
    render: RenderFn,
    agents: list[str] | None = None,
    sync: bool = False,
) -> None:
    repo.mkdir(parents=True)
    _write(repo / "ai.project.toml", _manifest(revision, features, stacks, agents or []))
    _write(repo / "ai" / "project-rules.md", _project_rules())
    render(worktree, repo, revision)
    if agents or sync:
        sync_templates(worktree, repo, revision)
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "chore: project scaffolding")


def _manifest(revision: str, features: list[str], stacks: list[str], agents: list[str]) -> str:
    return (
        f'ai_standards_version = "{revision}"\n'
        "\n"
        f"fragments = {json.dumps(['core/base'])}\n"
        "\n"
        f"features = {json.dumps(features)}\n"
        "\n"
        f"stacks = {json.dumps(stacks)}\n"
        "\n"
        f"local_overrides = {json.dumps(['ai/project-rules.md'])}\n"
        "\n"
        "[tooling]\n"
        f"agents = {json.dumps(agents)}\n"
        "\n"
        "[metadata]\n"
        'project_name = "eval-fixture"\n'
    )


def _project_rules() -> str:
    return (
        "# Project rules\n"
        "\n"
        "This is a synthetic fixture project used by the behavioral eval suite;\n"
        "follow the existing code style of the repository.\n"
    )


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _git(repo: Path, *args: str) -> str:
    try:
        return run_git(repo, *_IDENTITY_ARGS, *args)
    except GitError as error:
        msg = f"fixture git step failed: {error}"
        raise FixtureError(msg) from error


_READER_CLEAN = (
    "export interface Header {\n"
    "  name: string;\n"
    "  value: string;\n"
    "}\n"
    "\n"
    "export function readHeaders(lines: string[]): Header[] {\n"
    "  const headers: Header[] = [];\n"
    "  for (let i = 0; i < lines.length; i++) {\n"
    "    headers.push(parseHeader(lines[i]));\n"
    "  }\n"
    "  return headers;\n"
    "}\n"
    "\n"
    "export function parseHeader(line: string): Header {\n"
    '  const idx = line.indexOf(":");\n'
    "  if (idx === -1) {\n"
    "    throw new Error(`invalid header line: ${line}`);\n"
    "  }\n"
    "  return { name: line.slice(0, idx).trim(), value: line.slice(idx + 1).trim() };\n"
    "}\n"
)

_READER_OFF_BY_ONE = _READER_CLEAN.replace(
    "for (let i = 0; i < lines.length; i++) {",
    "for (let i = 0; i <= lines.length; i++) {",
)

_READER_CANDIDATE = _READER_OFF_BY_ONE.replace(
    "export function parseHeader(line: string): Header {",
    "/** Parse a `name: value` line into a Header record. */\n"
    "export function parseHeader(line: string): Header {",
) + (
    "\n"
    "/** Parse a single header line, returning null instead of throwing. */\n"
    "export function tryParseHeader(line: string): Header | null {\n"
    "  try {\n"
    "    return parseHeader(line);\n"
    "  } catch {\n"
    "    return null;\n"
    "  }\n"
    "}\n"
)


BUILDERS: dict[str, Callable[[Path, Path, str, RenderFn], Path]] = {
    "CR-001": build_cr001,
    "CR-002": build_cr002,
    "CR-003": build_cr003,
    "CR-004": build_cr004,
    "CR-005": build_cr005,
    "CR-006": build_cr006,
    "CR-007": build_cr007,
    "CR-008": build_cr008,
    "CR-009": build_cr009,
    "CR-010": build_cr010,
    "CR-011": build_cr011,
    "CR-012": build_cr012,
    "TRG-001": build_trg001,
}
