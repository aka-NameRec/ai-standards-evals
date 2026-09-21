# ai-standards-evals

Исполнимая поведенческая верификация для [ai-standards](https://github.com/aka-NameRec/ai-standards).
Спецификация: issue [aka-NameRec/ai-standards#18](https://github.com/aka-NameRec/ai-standards/issues/18),
исходное предложение — `docs/archive/20260917-032748-proposal-eval-spec.md` в репозитории `ai-standards`.

## Назначение

Репозиторий проверяет **наблюдаемое поведение агента**, а не скрытые рассуждения, по цепочке:

```text
доступность → активация → поведение → результат
```

Активация без корректного поведения недостаточна.

## Разделение ответственности

| Репозиторий | Владеет |
|---|---|
| `ai-standards` | нормативной семантикой: правила (`rule_map.toml`), контракты сценариев (`docs/scenarios/`), формат интерфейса раннера (`scenario-format.md`) |
| `ai-standards-evals` | материализацией фикстур, датасетами, scorers/graders, адаптерами агентов (runners), отчётами о прогонах |

Направление зависимости — только `ai-standards-evals` → `ai-standards` (чтение указанной ревизии).
Этот репозиторий не является и не должен становиться вторым источником нормативной истины.

## Связь с `ai-standards`

- Раннер соблюдает контракт **Required Harness Behavior** из
  `docs/scenarios/scenario-format.md` ревизии стандартов: детерминированная сборка фикстуры,
  прогон дословного промпта через адаптер harness с включёнными features, захват артефакта,
  проверка инвариантов и запрещённых исходов, вердикты по сценариям, поддержка baseline/candidate.
- Каждый прогон привязан к ревизии стандартов: тег `<version>-<date>` (совпадает с
  `meta.toml` `[release]` и пином `ai_standards_version`).
- Базовая линия: релиз **2.5.0** (тег `2.5.0-2026-09-21`).

## Релизный гейт

Начиная с #18 предполагаемый релиз `ai-standards` проходит верификацию через
regression suite этого репозитория: machine-readable отчёт для целевой ревизии в `reports/`,
критерий — отсутствие необъяснённых поведенческих регрессий относительно baseline.
Подробнее: `docs/cross-repo-flow.md`.

## Структура

```text
evals/       — задачи Inspect AI (сценарий → прогон → скоринг)
datasets/    — датасет-записи (метаданные сценариев, не содержимое фикстур)
fixtures/    — материализованные фикстуры (в т.ч. реальные Git-репозитории base → candidate)
scorers/     — детерминированные oracle, structured/LLM graders
agents/      — адаптеры внешних coding agents (Codex, Claude Code, Kilo, Cursor)
scripts/     — run_baseline / run_candidate / compare_runs / coverage_report
reports/     — отчёты прогонов и сравнения baseline/candidate
docs/        — cross-repo flow, авторство evals, guidelines для scorers
```

## Статус

Рабочий контур v0.1 — детерминированный сквозной прогон одного сценария:

- пин ревизии стандартов (`config.toml`) → временный worktree (`scripts/standards.py`);
- разбор контрактов сценариев и `rule_map.toml` запиненной ревизии;
- рендер `AGENTS.md` фикстуры через `ai-sync` (features/stacks из манифеста фикстуры);
- детерминированные фикстуры `CR-001`–`CR-003` — реальные Git-репозитории с историей
  base → candidate + Git-oracle «внесено ли изменение» (`scripts/fixtures.py`, `scripts/oracle.py`);
- адаптер Kilo (`kilo run --format json`), CLI `python -m scripts.run_scenario`,
  Inspect-обвязка `evals/code_review.py`;
- двуязычный (EN/RU) механический скорер формы отчёта (`scorers/report_shape.py`).

`CR-002` (no-padding control) проходит сквозной прогон; эталонные артефакты —
`reports/20260921-063453-CR-002/`.

Дальше: скоринг находок CR-001/CR-003 (структурированный грейдер), исполнение TRG-001
(деплой skill в фикстуру), контракты `CR-004`–`CR-009` в `ai-standards` через cross-repo
flow, baseline-отчёт по всем сценариям на 2.5.0.

## Инструменты

- Python ≥ 3.11, [uv](https://docs.astral.sh/uv/): `uv sync`, `uv run`.
- Framework: [Inspect AI](https://inspect.aisi.org.uk/).
- Качество: `uv run ruff check .`, `uv run mypy`, `uv run pytest`.
