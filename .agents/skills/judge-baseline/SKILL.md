---
name: judge-baseline
description: Post-hoc LLM grading of saved baseline/candidate runs — use when asked to «прогрейдить baseline», «judge-прогон», before merging ai-standards branches that change rules or skills, and for milestone verification.
---

# Judge Baseline

Задний числом LLM-грейд сохранённых прогонов сценариями CR-004 и CR-006:
находка проверяется судьёй (GLM) против rubric сценария, вердикт дописывается
в артефакты.

## Когда применять

- после milestone baseline-прогона набора (suite уже записал отчёты в `reports/`);
- перед слиянием ветки `ai-standards`, меняющей `fragments/**` или
  `templates/**` — артефакты гейта кандидата уже лежат в `reports/`;
- по прямому запросу «прогрейдить baseline» / «judge-прогон».

## Как запускать

```bash
uv run python -m scripts.judge_baseline
```

- Грейдятся все прогоны CR-004/CR-006 без `judge.json`; `--force` — перестрейдить,
  `--revision <rev>` — фильтр по ревизии.
- Ключ судьи берётся автоматически из `~/.local/share/kilo/auth.json`
  (провайдер `zai-coding-plan`) и подставляется в env-переменную из
  `[judge] api_key_env` (`config.toml`). Ручной экспорт не нужен.
- Судья и base_url — `[judge] model` / `[judge] base_url` в `config.toml`.

## Результат

- каждый ран: `judge.json` + блок `judge` в `verdict.json`;
- сводка: `reports/<stamp>-judge-baseline/summary.json`;
- exit 1 — есть judge `fail` (находка не удовлетворяет rubric — блокирует
  milestone), exit 2 — ошибки судьи.

## Интерпретация

- `fail` — находка не удовлетворяет rubric сценария; сигнал против агентской
  ревизии, не против судьи.
- `error` — проблема судьи или конфигурации (нет ключа, невалидный JSON);
  агента не наказывает, перезапустить после устранения.
- Модель судьи фиксируется в каждом judge-блоке: смена судьи видна в истории.
