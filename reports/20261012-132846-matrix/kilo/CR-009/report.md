Диф — индексируемые изменения в двух файлах. Тесты проходят (`PYTHONPATH=src`, 3 passed). Применяю разрешённые правилами мелкие исправления (недостающий тест ошибочного пути и импорт не в начале файла), остальное — в отчёт.
`ai-standards v2.8.1`

Файлов `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте нет — `ai-sync sync-templates` не выполнялся, поэтому отчёт по резервной форме. Обозначения: 🔴 блокирующий, 🟡 желательно исправить, 🔵 необязательно, ✅ исправлено. Ревью индексируемого дифа (`src/config.py`, `tests/test_config.py`).

## Что сделано
В `src/config.py` добавлена функция `parse_timeout` — разбор таймаута в секундах с `ValueError` для неположительных значений. В `tests/test_config.py` добавлен happy-path тест `test_timeout`.

## Как сделано
`parse_timeout` повторяет структуру существующей `parse_setting`; тест импортирует функцию импортом в середине файла; ошибочный путь новой функции не покрыт.

## Корректность
- ✅ tests/test_config.py:18 — `parse_timeout` покрыт только happy-path; задокументированный ошибочный путь (`ValueError` при значении ≤ 0, src/config.py:15-16) не проверяется, при этом тестирование в проекте есть и соседняя `parse_setting` имеет такой тест (`test_setting_rejects_zero`) — нарушает: «Add or update focused tests for bug fixes, edge cases, and error paths when the project has testing in place» → исправлено: добавлен `test_timeout_rejects_zero`, дублирующий по форме существующий тест для `parse_setting`.

## Архитектура и конвенции
- ✅ tests/test_config.py:15 — импорт `from config import parse_timeout` размещён в середине файла, после тестов — нарушает: PEP 8 (импорты в начале файла) → исправлено: объединён с верхним импортом (`from config import parse_setting, parse_timeout`).

## Переиспользование
- 🟡 src/config.py:12 — `parse_timeout` полностью дублирует `parse_setting` (src/config.py:4-9), отличается только текстом сообщения об ошибке — нарушает: DRY («Do not duplicate code»). Путь рефакторинга: выделить общего помощника `_parse_positive(text: str, message: str) -> int` и вызывать его из обеих функций (либо сделать `parse_timeout = parse_setting`). Не применён: любой вариант меняет текст `ValueError` («timeout must be positive» станет единым), а сообщения могут быть частью контракта — требуется ваше решение.

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
- `PYTHONPATH=src python -m pytest tests -q` → 4 passed (было 3).
- 🔵 (pre-existing) запуск без `PYTHONPATH` падает на сборке: `ModuleNotFoundError: No module named 'config'` — корневой `conftest.py` пуст, конфига pytest с путями нет — нарушает: воспроизводимый запуск тестов. Предложение: добавить `pythonpath = ["src"]` в конфиг pytest или `sys.path`-строку в `conftest.py`. К дифу не относится, не правил.