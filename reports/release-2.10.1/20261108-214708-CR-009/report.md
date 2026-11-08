`ai-standards` code review готов. Замечание: файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (`ai-sync sync-templates` не выполнялся), поэтому использую резервный формат из инструкций.

```markdown
# Code Review — ai-standards v2.10.1

## Что сделано
Добавлена функция `parse_timeout` в `src/config.py` и тест `test_timeout` в `tests/test_config.py` (изменения в индексе, не закоммичены).

## Как сделано
- `src/config.py:12` — новая функция `parse_timeout(text: str) -> int`: парсит целое, бросает `ValueError` при `value <= 0`.
- `tests/test_config.py:18` — тест `test_timeout` с одним happy-path-кейсом `parse_timeout("30") == 30`.

## Корректность
- 🟡 tests/test_config.py:18 — `test_timeout` покрывает только happy-path; путь ошибки `parse_timeout("0")` / отрицательного значения, бросающий `ValueError` (src/config.py:15-16), не протестирован — нарушает: General Engineering Principles («Add or update focused tests for bug fixes, edge cases, and error paths when the project has testing in place») и собственную конвенцию репозитория — соседний `test_setting_rejects_zero` (tests/test_config.py:10) проверяет именно этот путь для идентичной по структуре `parse_setting`. Проверено: `parse_timeout("0")` действительно бросает `ValueError`, теста на это нет.

## Архитектура и конвенции
- 🔵 tests/test_config.py:15 — импорт `from config import parse_timeout` расположен в середине файла, после тестов — нарушает: PEP 8 E402 (module level import not at top of file); существующий импорт из того же модуля уже есть в блоке импортов сверху (tests/test_config.py:3), новый нужно объединить с ним.

## Переиспользование
- 🟡 src/config.py:12 — `parse_timeout` дословно дублирует `parse_setting` (src/config.py:4-9), отличается только текст ошибки («must be positive» → «timeout must be positive») — нарушает: DRY («Do not duplicate code»). Проверено: обе функции открыты, тела идентичны кроме сообщения и имён параметра/переменной. Вариант рефакторинга: обобщить в одну функцию с параметром `label`/`error_message` (например, `parse_positive_int(text, label="setting")`), если семантически различные имена нужны как часть публичного API — оставить тонкие обёртки над общей реализацией.

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
- `PYTHONPATH=src python -m pytest tests -v` — 3 passed (все тесты, включая новый, зелёные). Примечание: импорт `from config import ...` требует `src` в `PYTHONPATH` — паттерн существовал до диффа (pre-existing), при запуске без него — `ModuleNotFoundError`.
```

Итог: 🔴 — 0, 🟡 — 2 (отсутствующий тест пути ошибки и дублирование `parse_setting`), 🔵 — 1 (импорт в середине файла). Правки не вносил — по умолчанию ревью только сообщает; скажите, если применить исправления.