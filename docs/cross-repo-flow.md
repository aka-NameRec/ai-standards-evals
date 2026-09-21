# Cross-repo flow изменений

Связь изменений `ai-standards` и `ai-standards-evals` без атомарного multi-repository commit.
Разделы 7–8 спецификации (issue aka-NameRec/ai-standards#18), сверенной с фактическим
состоянием стандартов: https://github.com/aka-NameRec/ai-standards/issues/18#issuecomment-5755833038

## Общий идентификатор change set

Изменение нормативного поведения связывается идентификатором `STD-CHANGE-XXXX`
(сквозная нумерация; заводится в PR `ai-standards`).

### PR в `ai-standards`

```yaml
change: STD-CHANGE-0042

rules:
  - RVW-009            # правила rule_map.toml, затронутые изменением

behavior_changes:
  - clarify handling of defects that predate the reviewed change

eval_impact:
  behavior_changed: true
  existing_coverage_sufficient: false
  required_evals:
    - CR-003           # сценарии docs/scenarios/, затронутые изменением
```

### PR в `ai-standards-evals`

```yaml
change: STD-CHANGE-0042

implements:
  - CR-003             # реализованные фикстуры/раннеры/scorers

covers:
  - RVW-009            # покрытые правила
```

## Eval impact analysis

```text
Меняет ли изменение наблюдаемое поведение?
    нет  → новый eval не требуется; существующий coverage всё равно прогоняется
    да   → достаточно ли существующего coverage?
              да  → прогнать regression suite
              нет → добавить или изменить eval, затем прогнать regression suite
```

Новая фикстура оправдана, когда: меняется наблюдаемое поведение; обнаружен ранее
непокрытый failure mode; существующие сценарии не различают compliant/non-compliant
поведение; меняется граница routing/activation; реальная регрессия получает постоянную защиту.

## Релизный гейт `ai-standards`

1. Перед предполагаемым релизом в этом репозитории выполняется full regression suite
   candidate-ревизии стандартов против baseline.
2. Прогон привязан к ревизии: тег `<version>-<date>` (совпадает с `meta.toml` `[release]`
   и пином `ai_standards_version`).
3. Machine-readable отчёт сохраняется в `reports/`, рядом — человекочитаемое сравнение
   по behaviors (не один global score).
4. Критерий прохождения: отсутствие необъяснённых поведенческих регрессий относительно
   baseline; критические сценарии (`must`-инварианты) проходят.
5. Намеренные изменения поведения легитимны при выполненном eval impact analysis
   (`STD-CHANGE-XXXX` + `required_evals`).
6. В `ai-standards` Release Workflow дополняется шагом release verification до
   `bump-version tag`: проверка наличия и вердикта отчёта для целевой версии.

## Базовая линия

Релиз `ai-standards` **2.5.0** (тег `2.5.0-2026-09-21`): контракт формата сценариев
(`docs/scenarios/scenario-format.md`) и `rule_map.toml` (52 правила).
