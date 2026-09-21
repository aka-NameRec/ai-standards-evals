"""Tests for mechanical report-shape checks."""

from __future__ import annotations

from scorers.report_shape import check, check_no_padding

GOOD_REPORT = """ai-standards 2.5.0-2026-09-21

## What Was Done

Reviewed the staged diff of the fixture change.

## How It Was Done

Read the changed files and the surrounding code; no edits were made.

## Correctness

None found.

## Architecture & Conventions

None found.

## Reuse

None found.

## Efficiency

None found.

## Quality

None found.

## Verification

The change was reviewed by reading only. Tests were not run.
"""

RU_REPORT = """Предисловие перед отчётом.

```
ai-standards v2.5.0

## Код-ревью

### Что сделано
Переименована переменная цикла; добавлен тест на одиночный элемент.

### Как сделано
Изменение следует существующему стилю обоих файлов.

### Корректность
Не найдено.

### Архитектура и конвенции
Не найдено.

### Переиспользование
Не найдено.

### Эффективность
Не найдено.

### Качество
Не найдено.

### Проверки
`python -m pytest -v` — 2 passed; тесты запускались в фикстуре напрямую.
```
"""

MISORDERED_REPORT = """ai-standards 2.5.0-2026-09-21

## What Was Done

Did things.

## How It Was Done

Read code.

## Correctness

None found.

## Reuse

None found.

## Architecture & Conventions

None found.

## Efficiency

None found.

## Quality

None found.

## Verification

Not run.
"""


LABEL_FORM_REPORT = """ai-standards v2.5.0

## Код-ревью

Что сделано: добавлен новый файл src/pricing.ts с функцией formatPrice.

Как сделано: логика написана с нуля; изменения только в индексе.

### Корректность
Не найдено.

### Архитектура и конвенции
Не найдено.

### Переиспользование
🟡 src/pricing.ts:1 — formatPrice является копией formatMoney из src/money.ts:1 —
нарушает: DRY.

### Эффективность
Не найдено.

### Качество
Не найдено.

### Проверки
`npm test` — не выполнено: vitest не установлен. Проверено чтением.
"""


BARE_FORM_REPORT = """ai-standards v2.5.0

## Код-ревью

Что сделано
Добавлен новый модуль src/pricing.ts с функцией formatPrice.

Как сделано
Семантика повторяет существующий formatMoney из src/money.ts.

Корректность
Не найдено.

Архитектура и конвенции
Не найдено.

Переиспользование
🟡 src/pricing.ts:1 — formatPrice дублирует formatMoney — нарушает: DRY.

Эффективность
Не найдено.

Качество
Не найдено.

Проверки
Тесты не запускались; проверено чтением.
"""


BOLD_FORM_REPORT = """ai-standards v2.5.0

## Код-ревью

**Что сделано**
Добавлена функция parse_timeout в src/config.py.

**Как сделано**
Повторяет проверенный паттерн parse_setting.

### Корректность
Не найдено.

### Архитектура и конвенции
Не найдено.

### Переиспользование
Не найдено.

### Эффективность
Не найдено.

### Качество
- ✅ tests/test_config.py:18 — error path не покрыт → исправлено: тест добавлен.

### Проверки
Все 4 теста проходят (запускались напрямую).
"""


def test_bold_form_report_passes() -> None:
    assert check(BOLD_FORM_REPORT).ok


def test_bare_form_report_with_findings_passes() -> None:
    assert check(BARE_FORM_REPORT).ok


def test_label_form_report_with_findings_passes() -> None:
    assert check(LABEL_FORM_REPORT).ok


def test_english_clean_report_passes() -> None:
    assert check(GOOD_REPORT).ok
    assert check_no_padding(GOOD_REPORT).ok


def test_russian_clean_report_passes() -> None:
    assert check(RU_REPORT).ok
    result = check_no_padding(RU_REPORT)
    assert result.ok, result.failures


def test_shape_check_detects_missing_section() -> None:
    report = GOOD_REPORT.replace("## Efficiency\n\nNone found.\n\n", "")

    result = check(report)

    assert not result.ok
    assert "missing section: Efficiency" in result.failures


def test_shape_check_detects_out_of_order_sections() -> None:
    result = check(MISORDERED_REPORT)

    assert not result.ok
    assert "required sections are out of order" in result.failures


def test_shape_check_rejects_verdict_section_and_missing_version() -> None:
    report = GOOD_REPORT.replace("ai-standards 2.5.0-2026-09-21", "") + "\n## Verdict\n\nBad.\n"

    result = check(report)

    assert not result.ok
    assert any("forbidden heading" in failure for failure in result.failures)
    assert any("version" in failure for failure in result.failures)


def test_no_padding_rejects_manufactured_findings_english() -> None:
    report = GOOD_REPORT.replace(
        "## Correctness\n\nNone found.",
        "## Correctness\n\n\U0001f534 src/stats.py:5 — the loop is suspicious.",
    )

    result = check_no_padding(report)

    assert not result.ok
    assert any("manufactured finding" in failure for failure in result.failures)
    assert any("does not state 'None found.'" in failure for failure in result.failures)


def test_no_padding_rejects_manufactured_findings_russian() -> None:
    report = RU_REPORT.replace(
        "### Качество\nНе найдено.",
        "### Качество\n\U0001f7e1 стоило бы добавить docstring везде.",
    )

    result = check_no_padding(report)

    assert not result.ok
    assert any("manufactured finding" in failure for failure in result.failures)
