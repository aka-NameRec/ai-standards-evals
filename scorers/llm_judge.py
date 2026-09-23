"""LLM judge: grades finding depth against a scenario rubric via an OpenAI-compatible API."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, cast

import httpx

from scripts.config import JudgeConfig

JUDGE_MODEL_MARKER = "llm-judge/v1"
RUBRICS_DIR = Path(__file__).resolve().parent / "rubrics"
_JSON_FENCE = ("```json", "```")


@dataclass(frozen=True)
class JudgeVerdict:
    """Outcome of one judge call over a saved report."""

    status: str  # "pass" | "fail" | "error"
    model: str
    score: float | None
    rationale: str
    raw_response: str
    criteria: dict[str, bool]


class HttpJsonClient(Protocol):
    """Minimal HTTP surface the judge needs; injectable for tests."""

    def post_json(
        self, url: str, headers: dict[str, str], payload: dict[str, object]
    ) -> dict[str, object]:
        """POST a JSON body and return the parsed JSON response."""
        ...


class HttpxJsonClient:
    """Default ``HttpJsonClient`` backed by httpx.

    Judge calls can be slow on long reports; one retry absorbs transient
    transport failures.
    """

    def post_json(
        self, url: str, headers: dict[str, str], payload: dict[str, object]
    ) -> dict[str, object]:
        request_timeout = 300.0
        last_error: Exception | None = None
        for attempt in (1, 2):
            try:
                response = httpx.post(
                    url, headers=headers, json=payload, timeout=request_timeout
                )
                response.raise_for_status()
                return dict(response.json())
            except httpx.HTTPError as error:
                last_error = error
                if attempt == 2:
                    break
        msg = f"judge transport failed after retry: {last_error}"
        raise JudgeError(msg)


class JudgeError(RuntimeError):
    """Raised when the judge itself fails; never counted against the agent."""

    def __init__(self, message: str, raw_response: str = "") -> None:
        super().__init__(message)
        self.raw_response = raw_response


def judge_report(
    rubric_text: str,
    report: str,
    diff: str,
    context_text: str,
    config: JudgeConfig,
    client: HttpJsonClient,
) -> JudgeVerdict:
    """Grade one saved report against a rubric via the configured judge model."""
    api_key = os.environ.get(config.api_key_env, "")
    if not api_key:
        raise JudgeError(
            f"judge API key is missing: set the {config.api_key_env} environment variable"
        )
    user_content = (
        f"{rubric_text}\n\n"
        f"--- REPORT ---\n{report}\n\n"
        f"--- REVIEWED DIFF ---\n{diff}\n\n"
        f"--- CONTEXT ---\n{context_text}"
    )
    payload = {
        "model": config.model,
        "temperature": config.temperature,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a strict review-quality judge. Grade the report "
                    "against the rubric. Respond with ONLY the JSON object the "
                    "rubric specifies."
                ),
            },
            {"role": "user", "content": user_content},
        ],
    }
    response = client.post_json(
        f"{config.base_url.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        payload=payload,
    )
    raw = _extract_message(response)
    data = _parse_verdict(raw)
    return JudgeVerdict(
        status=str(data["verdict"]),
        model=config.model,
        score=float(cast("int | float | str", data["score"])),
        rationale=str(data.get("rationale", "")),
        raw_response=raw,
        criteria={
            str(key): bool(value)
            for key, value in cast("dict[str, object]", data.get("criteria", {})).items()
        },
    )


def load_rubric(rubrics_dir: Path, scenario_id: str) -> str:
    """Load the rubric text for a scenario from the rubrics directory."""
    rubric_path = rubrics_dir / f"{scenario_id.lower()}.md"
    if not rubric_path.is_file():
        msg = f"rubric not found: {rubric_path}"
        raise JudgeError(msg)
    return rubric_path.read_text(encoding="utf-8")


def _extract_message(response: dict[str, object]) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        msg = f"judge response has no choices: {json.dumps(response)[:200]}"
        raise JudgeError(msg)
    message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str):
        msg = "judge response message content is not a string"
        raise JudgeError(msg)
    return content.strip()


def _parse_verdict(raw: str) -> dict[str, object]:
    stripped = raw.strip()
    for fence in _JSON_FENCE:
        if stripped.startswith(fence):
            stripped = stripped.split(fence, 1)[1]
            break
    if stripped.endswith("```"):
        stripped = stripped[: -3]
    try:
        data = json.loads(stripped.strip())
    except json.JSONDecodeError as error:
        msg = f"judge response is not valid JSON: {error}"
        raise JudgeError(msg, raw_response=raw) from error
    if not isinstance(data, dict) or data.get("verdict") not in ("pass", "fail"):
        msg = "judge response is missing a pass/fail verdict"
        raise JudgeError(msg, raw_response=raw)
    return data
