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
  раннер триггер-сетов `python -m scripts.run_triggers`, Inspect-обвязка
  `evals/code_review.py`;
- структурный грейдер находок (маркеры, локации, границы диффа, pre-existing-метки)
  и двуязычный (EN/RU) механический скорер формы отчёта (`scorers/`).

Результаты baseline-прогона на 2.5.0 (модель `zai-coding-plan/glm-5.3-flash`):

| Сценарий | Вердикт | Артефакты |
|---|---|---|
| CR-002 no-padding control | PASS | `reports/20260921-063453-CR-002` |
| CR-001 reuse | PASS (1 из 3 прогонов — промах по находке: `reports/20260921-065815-CR-001`) | `reports/20260921-070237-CR-001` |
| CR-003 pre-existing defect | PASS | `reports/20260921-071158-CR-003` |
| TRG-001 активация skill | 12/12 PASS | `reports/20260921-072206-TRG-001` |

Замечен сигнал: форма отчёта дрейфует между прогонами (заголовки/метки/порядок
секций) — порядок секций проверяется строго, оформление принимается в трёх формах.

Дальше: контракты `CR-004`–`CR-009` в `ai-standards` (ветка
`rules-change/18-eval-scenario-contracts`) и их реализация здесь, Inspect-интеграция
полного набора, cross-agent проверка.

## Инструменты

- Python ≥ 3.11, [uv](https://docs.astral.sh/uv/): `uv sync`, `uv run`.
- Framework: [Inspect AI](https://inspect.aisi.org.uk/).
- Качество: `uv run ruff check .`, `uv run mypy`, `uv run pytest`.
