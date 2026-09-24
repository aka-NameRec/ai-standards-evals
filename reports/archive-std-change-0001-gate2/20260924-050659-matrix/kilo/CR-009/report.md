Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` отсутствуют — использую fallback-формат из правил. Получаю дифф:
Запускаю тесты для проверки текущего состояния:
Коллекция тестов падает: `ModuleNotFoundError: No module named 'config'`. Проверяю, как тесты запускаются с `PYTHONPATH=src`, и историю коммитов:
`ai-standards v2.6.0`

Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (проект не запускал `ai-sync sync-templates`) — отчёт в fallback-формате из правил. Ревью текущего диффа: 2 staged-файла (`src/config.py`, `tests/test_config.py`).

## Задача
Bare-запрос «code review» — ревью текущего диффа. Дифф добавляет `parse_timeout` в `src/config.py` и happy-path тест для него.

## Что сделано
- `src/config.py:12-17` — новая функция `parse_timeout(text) -> int`: парсинг целого, ошибка `ValueError` при `<= 0`.
- `tests/test_config.py:15-19` — импорт `parse_timeout` посреди файла и тест `test_timeout` (только happy path).

## Как сделано
- Функция повторяет паттерн существующей `parse_setting`; тест повторяет стиль существующих тестов. Type hints и docstring присутствуют.

## Корректность
Не найдено. `parse_timeout` ведёт себя как заявлено в docstring — проверено запуском (см. Проверки).

## Архитектура и конвенции
- 🟡 tests/test_config.py:15 — импорт `from config import parse_timeout` размещён посреди файла, разрывая импорты одного модуля на два места (строка 3 и строка 15) — нарушает: PEP 8 (E402, импорты вверху файла); нужно объединить в `from config import parse_setting, parse_timeout` в верхнем блоке импортов.
- 🟡 conftest.py:1 — файл пуст, `src/` не в `sys.path`: `pytest tests -q` падает при коллекции (`ModuleNotFoundError: No module named 'config'` на tests/test_config.py:3), тесты запускаются только с `PYTHONPATH=src` (не задокументировано) — нарушает: работоспособность тестового запуска по умолчанию; путь фикса — добавить в пустой `conftest.py` `sys.path.insert`/`pythonpath` в pytest-конфиге. `(pre-existing)` — падение возникает на строке 3, которую дифф не менял.

## Переиспользование
- 🟡 src/config.py:12 — `parse_timeout` дословно дублирует `parse_setting` (src/config.py:4-9): тот же `int()`, та же проверка `<= 0`, то же исключение `ValueError`, отличается только текст сообщения — нарушает: DRY («Do not duplicate code»); проверено чтением обеих функций; путь фикса — делегировать в `parse_setting` (с осознанным решением по тексту сообщения, которое при этом изменится) или выделить общий хелпер.

## Эффективность
Не найдено.

## Качество
- 🟡 tests/test_config.py:18 — для новой `parse_timeout` нет теста error-path: docstring (src/config.py:13) и код (src/config.py:15-16) обещают `ValueError` при неположительном значении, но покрыт только happy path — нарушает: «Add or update focused tests for … edge cases, and error paths when the project has testing in place»; путь фикса — добавить `test_timeout_rejects_zero` по образцу существующего `test_setting_rejects_zero` (tests/test_config.py:10-12).

## Проверки
- Прочитаны оба файла целиком, не только дифф; обе версии `parse_setting`/`parse_timeout` сверены построчно.
- `pytest tests -q` (как есть): ошибка коллекции `ModuleNotFoundError: No module named 'config'` — воспроизведено, падение на неизменённой строке 3 (pre-existing).
- `PYTHONPATH=src python -m pytest tests -q`: **3 passed** — код диффа работает, но ошибка `parse_timeout("0")`/отрицательных значений тестами не покрыта, что подтверждает находку из «Качество».
- Замечание: `rtk pytest` в этом окружении сводит вывод к «No tests collected» даже для успешного прогона — итог получен прямым запуском без rtk.
- Файлы не изменялись: все находки требуют решения автора (изменение текста ошибки, добавление теста, конфиг запуска).

## Зависимости
Не добавлялись: дифф использует только стандартную библиотеку; манифеста зависимостей в проекте нет.