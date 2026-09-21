"""Runner configuration loading."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import cast

DEFAULT_CONFIG_PATH = Path("config.toml")
DEFAULT_TIMEOUT_SECONDS = 900


@dataclass(frozen=True)
class EvalConfig:
    """Pinned standards revision and runner parameters."""

    standards_repo: Path
    standards_revision: str
    model: str
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS


def load_config(path: Path | None = None) -> EvalConfig:
    """Load the runner configuration from a TOML file."""
    config_path = path or DEFAULT_CONFIG_PATH
    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    standards = cast("dict[str, object]", data["standards"])
    runner = cast("dict[str, object]", data["runner"])
    return EvalConfig(
        standards_repo=Path(cast("str", standards["repo"])).expanduser(),
        standards_revision=cast("str", standards["revision"]),
        model=cast("str", runner["model"]),
        timeout_seconds=cast("int", runner.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)),
    )
