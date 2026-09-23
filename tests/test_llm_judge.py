"""Tests for the LLM judge module (HTTP client injected, no network)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scorers.llm_judge import JudgeConfig, JudgeError, judge_report, load_rubric
from scripts.config import load_config

RUBRIC = """# Rubric: test

## Criteria

1. The finding names the defect.
2. The finding explains the consequence.

## Response format

Respond with ONLY a JSON object:
{"verdict": "pass" | "fail", "score": 0.0, "criteria": {}, "rationale": "..."}
"""

CONFIG = JudgeConfig(
    enabled=True,
    base_url="https://judge.example/api",
    model="judge-model-1",
    api_key_env="TEST_JUDGE_KEY",
    temperature=0.0,
)


class FakeClient:
    """Canned-response HttpJsonClient double that records the last payload."""

    def __init__(self, content: str) -> None:
        self.content = content
        self.last_payload: dict[str, object] | None = None

    def post_json(
        self, url: str, headers: dict[str, str], payload: dict[str, object]
    ) -> dict[str, object]:
        self.last_payload = payload
        self.last_headers = headers
        return {
            "choices": [{"message": {"content": self.content}}],
        }


def _verdict_content(verdict: str = "pass") -> str:
    return json.dumps(
        {
            "verdict": verdict,
            "score": 0.9,
            "criteria": {"defect_named": True, "consequence_explained": True},
            "rationale": "the finding explains the inversion",
        }
    )


@pytest.fixture(autouse=True)
def _key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEST_JUDGE_KEY", "secret-key")


def test_judge_report_parses_strict_json(tmp_path: Path) -> None:
    client = FakeClient(_verdict_content("pass"))

    verdict = judge_report(RUBRIC, "report text", "diff text", "", CONFIG, client)

    assert verdict.status == "pass"
    assert verdict.score == 0.9
    assert verdict.model == "judge-model-1"
    assert verdict.criteria["defect_named"] is True


def test_judge_report_sends_rubric_report_and_diff(tmp_path: Path) -> None:
    client = FakeClient(_verdict_content())

    judge_report(RUBRIC, "the report", "the diff", "extra context", CONFIG, client)

    assert client.last_payload is not None
    messages = client.last_payload["messages"]
    user_content = str(messages[-1]["content"])
    assert RUBRIC in user_content
    assert "the report" in user_content
    assert "the diff" in user_content
    assert "extra context" in user_content
    assert headers_ok(client)


def headers_ok(client: FakeClient) -> bool:
    return str(client.last_headers.get("Authorization", "")) == "Bearer secret-key"


def test_judge_report_accepts_fenced_json(tmp_path: Path) -> None:
    client = FakeClient("```json\n" + _verdict_content("pass") + "\n```")

    verdict = judge_report(RUBRIC, "report", "diff", "", CONFIG, client)

    assert verdict.status == "pass"


def test_judge_report_raises_on_non_json(tmp_path: Path) -> None:
    client = FakeClient("I could not decide.")

    with pytest.raises(JudgeError) as excinfo:
        judge_report(RUBRIC, "report", "diff", "", CONFIG, client)

    assert "not valid JSON" in str(excinfo.value)


def test_judge_report_raises_on_missing_verdict(tmp_path: Path) -> None:
    client = FakeClient(json.dumps({"score": 0.5}))

    with pytest.raises(JudgeError) as excinfo:
        judge_report(RUBRIC, "report", "diff", "", CONFIG, client)

    assert "pass/fail" in str(excinfo.value)


def test_load_rubric_reads_file(tmp_path: Path) -> None:
    (tmp_path / "cr-004.md").write_text("criteria here", encoding="utf-8")

    assert load_rubric(tmp_path, "CR-004") == "criteria here"


def test_load_rubric_raises_when_absent(tmp_path: Path) -> None:
    with pytest.raises(JudgeError):
        load_rubric(tmp_path, "CR-999")


def test_config_loads_judge_section(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        '[standards]\nrepo = "r"\nrevision = "x"\n'
        '[runner]\nmodel = "m"\n'
        "[judge]\nenabled = true\n"
        'base_url = "https://judge.example"\n'
        'model = "judge-1"\n'
        'api_key_env = "KEY_ENV"\n'
        "temperature = 0.0\n",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.judge is not None
    assert config.judge.enabled is True
    assert config.judge.model == "judge-1"
    assert config.judge.api_key_env == "KEY_ENV"


def test_config_without_judge_section_yields_none(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        '[standards]\nrepo = "r"\nrevision = "x"\n[runner]\nmodel = "m"\n',
        encoding="utf-8",
    )

    assert load_config(config_path).judge is None
