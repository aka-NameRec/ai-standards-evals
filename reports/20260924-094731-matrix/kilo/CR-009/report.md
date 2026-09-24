Файл `.ai-standards/code-review-report.md` отсутствует (проект не запускал `ai-sync sync-templates`) — использую резервный формат отчёта. Читаю файлы целиком, чтобы проверить находки по коду, а не по диффу.
Проверяю использование функций и запускаю тесты для верификации.
`conftest.py` пуст — проверю запуск тестов с явным `PYTHONPATH`.
Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют — `ai-sync sync-templates` не запускался, использую резервный формат отчёта.

---

**ai-standards v2.6.0**

## Задача
Code review текущего диффа (staged: `src/config.py`, `tests/test_config.py`).

## Что сделано
В `src/config.py` добавлена функция `parse_timeout` (парсинг положительного целого — таймаут в секундах). В `tests/test_config.py` добавлены импорт `parse_timeout` и тест `test_timeout`.

## Как сделано
`parse_timeout` реализована той же логикой, что и существующая `parse_setting` (`int()` + проверка `<= 0`). Тест покрывает только успешный путь (`"30" -> 30`). Импорт добавлен в середине модуля тестов.

## Корректность
- 🟡 `tests/test_config.py:18` — `test_timeout` покрывает только happy path; ветка ошибки `parse_timeout` (`ValueError` при `<= 0`, src/config.py:15-16) не протестирована, хотя соседний `test_setting_rejects_zero` (tests/test_config.py:10) задаёт конвенцию покрытия error path — нарушает: "Add or update focused tests for bug fixes, edge cases, and error paths when the project has testing in place". Фикс: добавить `test_timeout_rejects_zero` с `pytest.raises(ValueError)` по образцу `test_setting_rejects_zero`.

## Архитектура и конвенции
- 🟡 `tests/test_config.py:15` — импорт `from config import parse_timeout` расположен в середине модуля, а не в блоке импортов в начале файла — нарушает: PEP 8 (импорты в начале модуля) и конвенцию самого файла (строки 1–3). Фикс: перенести в строку 3, объединив: `from config import parse_setting, parse_timeout`.

## Переиспользование
- 🟡 `src/config.py:12` — `parse_timeout` полностью дублирует `parse_setting` (src/config.py:4-9): идентичные `int()`, проверка `<= 0` и возврат; отличается только текст сообщения об ошибке — нарушает: "Do not duplicate code". Фикс: `parse_timeout` делегирует `parse_setting` (при этом сообщение изменится с `"timeout must be positive"` на `"must be positive"` — это изменение поведения публичной функции, требует решения автора).

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
- Запуск: `PYTHONPATH=src python -m pytest tests/ -q` — 3 passed.
- Запуск без `PYTHONPATH`: `python -m pytest tests/ -q` падает с `ModuleNotFoundError: No module named 'config'`.
  - 🔵 `conftest.py:1` — (pre-existing) файл пуст, настройки `sys.path` для `src/` и pytest-конфигурации нет, поэтому тестовый импорт `from config import ...` работает только при ручном `PYTHONPATH=src`. Проблема существовала до диффа (импорт в строке 3 не менялся); фикс — вне рамок этого ревью, может быть предложен отдельно.

Ни одно исправление не применялось: правки затрагивают поведение (текст ошибки) и staged-состояние индекса — по политике это отчёт, а не фикс.