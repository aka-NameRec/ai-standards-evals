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

Результаты baseline-прогонов (модель `zai-coding-plan/glm-5.3-flash`; CR-004–CR-009 —
на ветке контрактов `rules-change/18-eval-scenario-contracts`):

| Сценарий | Вердикт | Артефакты |
|---|---|---|
| CR-001 reuse | PASS (1 из 3 прогонов — промах по находке: `reports/20260921-065815-CR-001`) | `reports/20260921-070237-CR-001` |
| CR-002 no-padding control | PASS | `reports/20260921-063453-CR-002` |
| CR-003 pre-existing defect | PASS | `reports/20260921-071158-CR-003` |
| CR-004 correctness defect | PASS | `reports/20260921-103017-CR-004` |
| CR-005 internal duplication | FAIL — порядок секций нарушен (Reuse раньше Корректности) | `reports/20260921-103251-CR-005` |
| CR-006 architecture decision | PASS | `reports/20260921-103413-CR-006` |
| CR-007 apparent violation | PASS | `reports/20260921-103614-CR-007` |
| CR-008 verification honesty | PASS | `reports/20260921-103830-CR-008` |
| CR-009 error-path coverage | PASS | `reports/20260921-104040-CR-009` |
| TRG-001 активация skill | 12/12 PASS | `reports/20260921-072206-TRG-001` |

Сигналы baseline: дрейф формы отчёта между прогонами (четыре формы рендера секций;
порядок секций проверяется строго — CR-005 поймал реальное нарушение); в CR-009 агент
применил small-fix политику (добавил тест, записал ✅ с прогоном); в CR-006/CR-008
находки ссылаются на ADR-004 и честно сообщают о неисполняемом наборе тестов.

Дальше: Inspect-интеграция полного набора с повторными trials, cross-agent проверка,
слияние ветки контрактов `CR-004`–`CR-009` в `main` `ai-standards` по решению
пользователя.

## Инструменты

- Python ≥ 3.11, [uv](https://docs.astral.sh/uv/): `uv sync`, `uv run`.
- Framework: [Inspect AI](https://inspect.aisi.org.uk/).
- Качество: `uv run ruff check .`, `uv run mypy`, `uv run pytest`.
