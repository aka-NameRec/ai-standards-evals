# Guidelines для scorers

Иерархия scoring (раздел 10 спецификации #18). Использовать максимально сильный
детерминированный oracle; LLM judge не применяется к фактам, проверяемым механически.

```text
deterministic assertion
    ↓
repository/environment inspection
    ↓
static analysis / parser / AST
    ↓
structured heuristic
    ↓
LLM grader
    ↓
human review
```

## Примеры соответствия

- обязательные разделы отчёта присутствуют → parser формы отчёта;
- review изменил исходные файлы → `git diff`;
- существующий helper использован → анализ source/AST;
- tests pass → test runner;
- finding действительно описывает architecture violation → LLM grader с rubric;
- неоднозначный boundary case → human-calibrated LLM grader.

## Ожидаемые исходы

Ожидания фикстуры описываются в терминах `must` / `must_not` / `optional`
(манифест фикстуры; раздел 13 спецификации). Инварианты судят исход, никогда — формулировки.

## Статус

Каркас; практические рекомендации дополняются при реализации scorers v0.1.
