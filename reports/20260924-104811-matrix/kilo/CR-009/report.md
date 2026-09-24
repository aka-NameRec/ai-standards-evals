**ai-standards v2.6.0**

Примечание: файлов `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте нет (проект не запускал `ai-sync sync-templates`) — отчёт по резервной форме из правил.

**Задача** — bare «code review»: ревью текущего staged-диффа (`src/config.py`, `tests/test_config.py`).

**Что сделано** — в `src/config.py` добавлена функция `parse_timeout`; в `tests/test_config.py` добавлен тест `test_timeout`.

**Как сделано** — `parse_timeout` повторяет логику `parse_setting` с другим текстом ошибки; тест добавлен в конец файла, импорт — внутри файла после тестов; тесты прогнаны локально.

**Корректность**
- 🟡 `tests/test_config.py:18` — `test_timeout` покрывает только happy path; задокументированный в docstring путь ошибки (`parse_timeout` бросает `ValueError` при `value <= 0`, `src/config.py:15`) тестом не покрыт, хотя для аналогичной `parse_setting` такой тест есть (`tests/test_config.py:10`) — нарушает: AGENTS.md «General Engineering Principles: Add or update focused tests for bug fixes, edge cases, and error paths when the project has testing in place». Исправление: добавить `test_timeout_rejects_non_positive` c `pytest.raises(ValueError)` для `"0"` и/или `"-5"`.

**Архитектура и конвенции**
- 🟡 `tests/test_config.py:15` — импорт `from config import parse_timeout` размещён в середине файла, после тестов — нарушает: PEP 8 (импорты в начале файла); ломает и конвенцию самого файла (импорты в строках 1–3). Исправление: перенести импорт к строкам 1–3.

**Переиспользование**
- 🟡 `src/config.py:12` — `parse_timeout` дублирует `parse_setting` (`src/config.py:4`) дословно, отличается только текст ошибки — нарушает: DRY («Do not duplicate code»). Путь рефакторинга: добавить в `parse_setting` опциональный параметр сообщения либо выделить общий помощник `_parse_positive(text, message)`, а `parse_timeout` сделать делегированием. По правилам «Fixing While Reviewing» рефакторинг не применяю — только сообщаю.

**Эффективность** — Не найдено.

**Качество** — Не найдено.

**Проверки** — `PYTHONPATH=src python -m pytest tests -q`: 3 passed, 0.02s. Замечание (pre-existing): запуск без `PYTHONPATH=src` падает на коллекции (`ModuleNotFoundError: No module named 'config'`) — `conftest.py` пуст, конфигурации упаковки нет; 🔵 опционально можно добавить путь в `conftest.py` или `pyproject.toml`.

**Зависимости** — новых зависимостей нет.