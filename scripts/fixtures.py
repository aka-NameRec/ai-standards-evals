"""Deterministic fixture builders for the code-review scenarios."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from scripts.git_utils import GitError, run_git
from scripts.render import render_agents_md

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


def build_fixture(
    scenario_id: str,
    worktree: Path,
    parent: Path,
    revision: str,
    render: RenderFn = render_agents_md,
) -> Path | None:
    """Build the fixture for a scenario; return None when the scenario has none."""
    builders: dict[str, Callable[[Path, Path, str, RenderFn], Path]] = {
        "CR-001": build_cr001,
        "CR-002": build_cr002,
        "CR-003": build_cr003,
    }
    builder = builders.get(scenario_id)
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


def _init_repo(
    repo: Path,
    worktree: Path,
    revision: str,
    features: list[str],
    stacks: list[str],
    render: RenderFn,
) -> None:
    repo.mkdir(parents=True)
    _write(repo / "ai.project.toml", _manifest(revision, features, stacks))
    _write(repo / "ai" / "project-rules.md", _project_rules())
    render(worktree, repo, revision)
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "chore: project scaffolding")


def _manifest(revision: str, features: list[str], stacks: list[str]) -> str:
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
        "agents = []\n"
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
