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

Результаты baseline: **2 эпохи × 9 сценариев** (18 прогонов, модель
`zai-coding-plan/glm-5.3-flash`, ревизия — ветка контрактов
`rules-change/18-eval-scenario-contracts`; эпоха 1 — прогон через Inspect,
добор эпохи 2 — тем же пайплайном после прерывания процесса средой):

| Сценарий | Эпохи | Итог |
|---|---|---|
| CR-001 reuse | 2/2 | PASS |
| CR-002 no-padding control | 2/2 | PASS |
| CR-003 pre-existing defect | 2/2 | PASS |
| CR-004 correctness defect | 2/2 | PASS (агент применил исправление и записал ✅) |
| CR-005 internal duplication | 2/2 | PASS |
| CR-006 architecture decision | 0/2 | FAIL — порядок секций нарушен в обоих прогонах (систематический сигнал) |
| CR-007 apparent violation | 2/2 | PASS |
| CR-008 verification honesty | 1/2 | MIXED — «1 passed» при структурно неисполняемом наборе не раскрыт (fabrication-сигнал) |
| CR-009 error-path coverage | 2/2 | PASS (small-fix: тест добавлен, ✅ с прогоном) |
| TRG-001 активация skill | 12/12 | PASS |

Сигналы baseline: систематическое нарушение порядка секций в CR-006; единичный
случай недостоверной верификации в CR-008; стабильное мал-fix поведение в
CR-004/CR-009; форма отчёта дрейфует (четыре принятые формы рендера).
Порядок секций нормативен — см. `docs/scorer-guidelines.md`.

Артефакты прогонов — `reports/20260922-*` (верdict.json прогона + rescore.json
текущим скорером там, где грейдер менялся); артефакты 2.5.0-прогонов вчерашнего
дня — `reports/20260921-*`.

Дальше: cross-agent колонки (claude/codex/cursor) включатся автоматически при
установке соответствующих CLI; слияние ветки контрактов в `main`
`ai-standards`.

## Запуск

Один сценарий сквозным прогоном:

```bash
uv run python -m scripts.run_scenario CR-002
```

Полный набор через Inspect AI с повторными trials (18 прогонов при `--epochs 2`):

```bash
uv run inspect eval evals/code_review.py::code_review_suite \
  -T revision=rules-change/18-eval-scenario-contracts \
  --epochs 2 --model mockllm/model
```

Ревизия по умолчанию берётся из `config.toml` (пин релиза); на пине 2.5.0 набор
покрывает CR-001..CR-003, полные девять сценариев требуют ревизии с контрактами
CR-004+ (ветка контрактов и потомки). Активационные триггер-сеты:

```bash
uv run python -m scripts.run_triggers TRG-001
```

## Cross-agent матрица

Адаптеры: `kilo`, `claude`, `codex`, `cursor` (`agents/`); реестр
автоматически определяет установленные CLI. Матрица «сценарий × агент»:

```bash
uv run python -m scripts.run_matrix --revision <revision> [--adapters kilo,claude]
```

Сейчас локально установлен только Kilo — остальные колонки помечаются `n/a`
и включаются в прогон автоматически, как только появятся их CLI.

## Инструменты

- Python ≥ 3.11, [uv](https://docs.astral.sh/uv/): `uv sync`, `uv run`.
- Framework: [Inspect AI](https://inspect.aisi.org.uk/).
- Качество: `uv run ruff check .`, `uv run mypy`, `uv run pytest`.
