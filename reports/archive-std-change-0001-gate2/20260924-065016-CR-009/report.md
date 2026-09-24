Diff на этом заканчивается — теперь я сверю свои выводы с самим кодом, а не только с diff.
Файлы подтвердили дублирование и паттерн импортов. Запускаю тесты, чтобы проверить поведение, прежде чем фиксировать результат.
Pytest ничего не собрал — проверяю причину по полному логу.
Ошибка импорта: `src/` не в `sys.path` при запуске из корня. Проверю с `PYTHONPATH=src`, как это, вероятно, задумано фикстурой.
Вывод rtk противоречит логу — запускаю pytest напрямую (fallback).
`ai-standards v2.6.0`

Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (проект не выполнял `ai-sync sync-templates`) — отчёт по fallback-форме. Область ревью: staged-дифф, 2 файла, +15 строк.

## Что сделано
Добавлена функция `parse_timeout` (парсинг таймаута с проверкой положительности) и happy-path тест `test_timeout`.

## Как сделано
- `src/config.py:12-17` — новая функция: `int(text)`, при `<= 0` — `ValueError("timeout must be positive")`.
- `tests/test_config.py:15, 18-19` — импорт и один тест `parse_timeout("30") == 30`.

## Корректность
🟡 tests/test_config.py:18 — новый `test_timeout` покрывает только happy path; ветка ошибки `parse_timeout` (`ValueError` при неположительном значении, src/config.py:15-16) не покрыта, хотя для аналогичной `parse_setting` error path в этом же файле покрыт (`test_setting_rejects_zero`, tests/test_config.py:10-12) — нарушает: «Add or update focused tests for bug fixes, edge cases, and error paths when the project has testing in place». Фикс: добавить тест вида `with pytest.raises(ValueError): parse_timeout("0")` (импорт `pytest` уже есть в строке 1).

## Архитектура и конвенции
🔵 tests/test_config.py:15 — импорт `from config import parse_timeout` размещён в середине файла после тестов, тогда как все импорты файла сгруппированы вверху (строки 1-3) — нарушает: конвенция файла (импорты вверху модуля).
🔵 conftest.py:1 (pre-existing) — `pytest` из корня репозитория не собирает тесты: `ModuleNotFoundError: No module named 'config'`, поскольку `src/` не попадает в `sys.path` (conftest пуст, конфигурации pytest/pyproject нет); правило не сопоставлено — наблюдение, исправление на усмотрение автора.

## Переиспользование
🟡 src/config.py:12 — `parse_timeout` дословно повторяет `parse_setting` (src/config.py:4-9): та же логика `int()` + проверка `<= 0` + `ValueError`, отличаются только имя, docstring и текст ошибки — нарушает: DRY «Do not duplicate code». Путь рефакторинга: общий приватный хелпер `_parse_positive(text, message)`, а `parse_setting`/`parse_timeout` — тонкие обёртки над ним.

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
- Прочитаны полные файлы `src/config.py`, `tests/test_config.py`, `conftest.py`, `ai.project.toml`, а не только дифф; дублирование и расположение импортов сверены с кодом.
- `PYTHONPATH=src python -m pytest tests/ -q` — 3 passed (happy path новой функции подтверждён; error path не подтверждён — теста нет).
- Прямой `pytest` без `PYTHONPATH=src` не собирает тесты (см. pre-existing выше).
- rtk: повторный запуск `rtk pytest` вернул «No tests collected», противоречащий его же логу, — команда выполнена напрямую без rtk.