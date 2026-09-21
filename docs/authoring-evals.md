# Авторство evals

Как добавить новую поведенческую проверку. Статус: каркас; расширяется по мере
реализации v0.1.

## Где живёт что

- **Контракт сценария** — в `ai-standards`, `docs/scenarios/<ID>-<slug>.md` (+ `.ru.md`),
  по контракту `scenario-format.md`: Fixture, Enabled Features, Prompt, Expected Observable
  Invariants, Forbidden Outcomes, опционально Scoring Rubric. Привязка правил — через
  `rule_map.toml`.
- **Исполнение** — здесь: материализация фикстуры (`fixtures/`), запись датасета
  (`datasets/`), задача Inspect AI (`evals/`), scorers (`scorers/`).

## Поток добавления нового eval

```text
требование или наблюдаемый failure
    → выделить observable behavior
    → оформить контракт сценария в ai-standards (STD-CHANGE-XXXX, см. cross-repo-flow.md)
    → спроектировать минимальный различающий fixture
    → переиспользовать существующую фикстуру, если возможно
    → выбрать сильнейший практичный scorer
    → прогнать на baseline
    → убедиться, что сценарий не тривиален
    → добавить как regression eval
```

## Требования к сценарию

- Проверяет поведение, а не формулировки: `fixture + task + observable invariant +
  forbidden outcome`, не exact response matching.
- Изолирует один или несколько значимых failure modes; различает compliant и
  non-compliant поведение.
- Достаточно мал для понимания, достаточно реалистичен, чтобы не быть карикатурным.
- Отношение сценарий-к-правилам — many-to-many; одна фикстура на каждое предложение
  `AGENTS.md` не создаётся.

## Обязательные типы в suite (milestone v0.1)

- контекст вне diff; Git history (base → candidate); вознаграждение отсутствия finding;
  граница routing/activation (activation trigger set).
