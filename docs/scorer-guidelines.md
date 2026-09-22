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

## Порядок секций отчёта — нормативен (решение по CR-005)

Порядок разделов отчёта задан workflow («…fall back to this order: Task,
What Was Done, How It Was Done, then findings under Correctness, …») и
проверяется строго: перестановка секций — это несоответствие форме (RVW-015,
RVW-030), а не вопрос оформления. Baseline CR-005 поймал реальное нарушение
этого порядка агентом — именно такие дрейфы набор и обязан фиксировать.
При этом рендеринг форм гиброчен: заголовок (`## Name`), метка (`Name:`),
«голая» строка (`Name`) и жирная метка (`**Name**`) принимаются как одна и та
же секция; язык секций следует языку чата (EN/RU словари). Локация-файл без
строки допустима, когда строки нет (RVW-010: «a line when one is available»).

## Статус

Каркас; практические рекомендации дополняются при реализации scorers v0.1.
