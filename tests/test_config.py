"""Tests for runner configuration loading."""

from __future__ import annotations

from pathlib import Path

from scripts.config import load_config

CONFIG_SAMPLE = """
[standards]
repo = "~/workspace/myself/ai-standards"
revision = "2.5.0-2026-09-21"

[runner]
model = "test-provider/test-model"
timeout_seconds = 60
"""


def test_load_config_reads_pinned_values(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(CONFIG_SAMPLE, encoding="utf-8")

    config = load_config(config_path)

    assert config.standards_repo == Path("~/workspace/myself/ai-standards").expanduser()
    assert config.standards_revision == "2.5.0-2026-09-21"
    assert config.model == "test-provider/test-model"
    assert config.timeout_seconds == 60


def test_load_config_applies_timeout_default(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        '[standards]\nrepo = "repo"\nrevision = "r1"\n[runner]\nmodel = "m"\n',
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.timeout_seconds == 900
