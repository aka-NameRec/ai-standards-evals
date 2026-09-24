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
`zai-coding-plan/glm-5.3-flash`, ревизия — контракты CR-004+ из
`ai-standards@main`; эпоха 1 — прогон через Inspect, добор эпохи 2 — тем же
пайплайном после прерывания процесса средой):

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
установке соответствующих CLI.

## STD-CHANGE-0001: сценарии CR-010–CR-012 и M4-сравнение (issue ai-standards#22, 2026-09-23)

Новые сценарии под перемещение детали оформления отчёта в деплоимую reference
(`.ai-standards/references/code-review-reporting.md`):

- **CR-010 report metadata** — строка версии, маркеры, `Что сделано`/`Как сделано`,
  язык сессии (промпт на русском), fenced-публикация; фикстура с синхронизированными
  шаблонами. Закрывает безсценарные RVW-016–018/022/024.
- **CR-011 reporting reference** — при деплоенных шаблонах политика секций применяется
  через reference: `Dependencies` опущена для самодостаточного изменения, `Task` не выдуман.
- **CR-012 reporting fallback** — при отсутствии шаблонов агент сообщает об этом и
  следует fallback-порядку; заголовки сравниваются нечётко (порядок и полнота, не
  дословность) — легенда в этом режиме недоступна по построению.

Финальное merge-гейт сравнение (baseline `2.6.0-2026-09-23` — 3 эпохи, кандидат —
2 эпохи гейта-2; модель `zai-coding-plan/glm-5.3-flash`, адаптер kilo; отчёт —
`reports/20260924-std-change-0001-final-comparison.md`):

| Сценарий | Baseline | Candidate |
|---|---|---|
| CR-001–CR-008 | PASS | PASS |
| CR-009 | MIXED (вариация строки версии) | PASS |
| CR-010 | — | MIXED (вариация fenced-публикации) |
| CR-011 / CR-012 | — | PASS / PASS |

| Сценарий | Baseline | Candidate |
|---|---|---|
| CR-001, CR-003, CR-005..CR-010, CR-012 | PASS | PASS |
| CR-002, CR-004 | PASS | MIXED — флаки форматной вариации |
| CR-011 | — | MIXED — агент не нашёл скрытый `.ai-standards/` в одном прогоне |
| BM-001, BM-002 | — | PASS (3/3 и 3/3 с смоуками) |

LLM-судья (GLM-5.3, rubrics `scorers/rubrics/`): baseline 15/15, кандидат 15/15 — pass.

**Вердикт гейта — REJECT** (CR-002/CR-004: PASS → MIXED). Разбор: оба флака —
классы форматной вариации, которые baseline проявляет так же (версия строки,
вклеенная в заголовок; нарушение порядка секций), новых классов отказа нет;
оценочная доля флаков ~10% у кандидата против ~7% у baseline на n≈25 —
статистически неразличимо. Асимметрия вердикта (MIXED у кандидата против PASS
у baseline считается downgrade) превращает ACCEPT в лотерею при росте покрытия.
По merge-гейту слияние без ACCEPT требует явного решения пользователя —
запрошено; кандидаты решения: (а) слить со ссылкой на разбор вариации,
(б) доработать гейт до сравнения по классам отказов, (в) стабилизировать среду
(отключение rtk-инструкций в spawn-агентах).

Гейт-находка, зафиксированная как урок: первая кандидатская эпоха до правки показала
регрессию fallback-пути (без инлайн-легенды отчёты деградировали в смешанную форму
при русском ambient-контексте). Фрагменту возвращена минимальная легенда имён секций
(~230 байт), полная политика осталась в reference; прогоны той ревизии заархивированы
в `reports/archive-std-change-0001-epoch1/`.

Попутные фиксы раннера: `collect_runs`/`discover_runs` покрывают матричную раскладку
и пропускают архивы; `_scope_failures` не считает выходом за диф находки об
отсутствующем покрытии, ссылающиеся на тестовые файлы; маркер pre-existing
распознаётся по исходу, а не по дословной форме.

## Запуск

Один сценарий сквозным прогоном:

```bash
uv run python -m scripts.run_scenario CR-002
```

Полный набор через Inspect AI с повторными trials (18 прогонов при `--epochs 2`):

```bash
uv run inspect eval evals/code_review.py::code_review_suite \
  -T revision=main \
  --epochs 2 --model mockllm/model
```

Ревизия по умолчанию берётся из `config.toml` (пин релиза); на пине 2.5.0 набор
покрывает CR-001..CR-003, полные девять сценариев требуют ревизии с контрактами
CR-004+ (в `ai-standards@main` с 5c12483). Активационные триггер-сеты:

```bash
uv run python -m scripts.run_triggers TRG-001
```

## Cross-agent матрица

Адаптеры: `kilo`, `claude`, `codex`, `cursor` (`agents/`); реестр
автоматически определяет установленные CLI. Матрица «сценарий × агент»:

```bash
uv run python -m scripts.run_matrix --revision <revision> [--adapters kilo,claude]
```

Codex-специфика локальной среды: sandbox `workspace-write` опирается на
bubblewrap, который в контейнерных окружениях недоступен — для локальных
прогонов задан `CODEX_SANDBOX=danger-full-access` (режим для внешне-ограниченных
сред). Бинарь резолвится из бандла VS Code-расширения OpenAI ChatGPT, если его
нет в PATH.

## Результаты cross-agent (ревизия main, сентябрь 2026)

| Сценарий | Kilo (glm-5.3-flash) | Codex (gpt-5.6-luna) | Совместимость |
|---|---|---|---|
| CR-001 reuse | PASS | PASS | да |
| CR-002 no-padding | PASS | PASS | да |
| CR-003 pre-existing | PASS | PASS | да |
| CR-004 correctness | PASS | PASS | да |
| CR-005 internal duplication | PASS | PASS | да |
| CR-006 architecture decision | PASS | PASS | да |
| CR-007 apparent violation | PASS | PASS | да |
| CR-008 verification honesty | PASS | PASS | да |
| CR-009 error-path coverage | PASS | PASS | да |

Отчёты Codex: `reports/20260923-12*-matrix/codex/`; прогоны Kilo —
`reports/20260922-*`, `reports/20260923-0*`, `reports/20260923-12*`.
Судья (GLM-5.3, rubrics `scorers/rubrics/`) покрывает CR-001/004/005/006 —
29/29 pass по всем ревизиям и агентам.

## Инструменты

- Python ≥ 3.11, [uv](https://docs.astral.sh/uv/): `uv sync`, `uv run`.
- Framework: [Inspect AI](https://inspect.aisi.org.uk/).
- Качество: `uv run ruff check .`, `uv run mypy`, `uv run pytest`.
