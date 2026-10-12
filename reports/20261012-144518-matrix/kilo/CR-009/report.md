В репозитории отсутствует каталог `.ai-standards/` — буду использовать формат отчета из резервного варианта (fallback). Изменения находятся в индексе, поэтому я проверю `git diff --cached` и изучу файлы.
ai-standards v2.8.1

> Примечание: файлов `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте нет — `ai-sync sync-templates` не выполнялся, поэтому отчёт по fallback-форме. Легенда маркеров: 🔴 блокирующий, 🟡 желательно исправить, 🔵 опционально, ✅ исправлено.

## Задача
Ревью текущего диффа (staged-изменения в `src/config.py` и `tests/test_config.py`).

## Что сделано
Проверен staged-дифф: добавлена функция `parse_timeout` в `src/config.py` и тест `test_timeout` в `tests/test_config.py`. Каждый finding сверён с кодом, а не только с диффом.

## Как сделано
Прочитаны оба изменённых файла целиком, `conftest.py`; прогнан тестовый прогон; поведение error-path проверено прямым вызовом.

## Корректность
Не найдено.

## Архитектура и конвенции
- 🔵 tests/test_config.py:15 — импорт `from config import parse_timeout` размещён в середине файла после тестов, вместо объединения с импортом в строке 3 — нарушает: PEP 8 (импорты в начале файла) и стиль существующего кода.
- 🔵 conftest.py:1 — (pre-existing) `conftest.py` пуст, поэтому `python -m pytest` без `PYTHONPATH=src` падает на коллекции (`ModuleNotFoundError: No module named 'config'`) — нарушает: связность структуры модулей / воспроизводимость запуска тестов.

## Переиспользование
- 🔵 src/config.py:12 — `parse_timeout` дословно дублирует логику `parse_setting` (src/config.py:4-9), отличается только текст ошибки и имя параметра — нарушает: DRY («Do not duplicate code»). Путь рефакторинга: общий хелпер вида `_parse_positive(text, label)` либо делегирование `parse_timeout` в `parse_setting`.

## Эффективность
Не найдено.

## Качество
- 🟡 tests/test_config.py:18 — новый `test_timeout` покрывает только happy path; error path (неположительный ввод → `ValueError`, src/config.py:15-16) не протестирован, хотя docstring функции его обещает, а соседняя `parse_setting` имеет такой тест (`test_setting_rejects_zero`, tests/test_config.py:10) — нарушает: «Add or update focused tests for bug fixes, edge cases, and error paths when the project has testing in place» (AGENTS.md). Ожидаемое исправление: тест вида `test_timeout_rejects_zero` с `pytest.raises(ValueError)` для `parse_timeout("0")`.

## Проверки
- `PYTHONPATH=src python -m pytest -q` — 3 passed (0.02s).
- Прямой вызов `parse_timeout("0")` подтверждает `ValueError: timeout must be positive` (src/config.py:16) — error path в коде есть, теста на него нет.
- Запуск без `PYTHONPATH=src` падает на коллекции — pre-existing, к диффу не относится.

## Зависимости
Нет.