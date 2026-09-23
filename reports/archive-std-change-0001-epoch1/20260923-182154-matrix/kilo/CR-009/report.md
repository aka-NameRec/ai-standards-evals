Обе правки staged; `.ai-standards/` в проекте отсутствует — проверю тесты, чтобы верифицировать находки.
rtk с `PYTHONPATH` дал подозрительный результат — выполняю без него (fallback).
ai-standards v2.6.0

Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (проект не запускал `ai-sync sync-templates`) — отчёт собран по резервному порядку разделов.

## Задача
Ревью текущего staged-диффа: `src/config.py`, `tests/test_config.py`.

## Что было сделано
Добавлена функция `parse_timeout` (парсинг таймаута в секундах, `ValueError` для неположительных значений) и happy-path тест `test_timeout`.

## Как это было сделано
Функция воспроизводит структуру существующей `parse_setting`; тест дописан в конец файла, импорт добавлен в середину файла.

## Корректность
Не найдено.

## Архитектура и конвенции
- 🟡 tests/test_config.py:15 — импорт `from config import parse_timeout` расположен в середине файла, после тестов, и дублирует импорт того же модуля из строки 3 — violates: PEP 8 (imports at top), «Keep file and module structure coherent and predictable».
- 🟡 (pre-existing) conftest.py:1 — при обычном запуске `pytest` / `python -m pytest tests` тесты не собираются: `ModuleNotFoundError: No module named 'config'`, потому что `src/` не попадает в `sys.path` (conftest.py пуст, конфигурации путей нет); тесты проходят только с `PYTHONPATH=src` — violates: «Keep file and module structure coherent and predictable». Проблема старше диффа (импорт в tests/test_config.py:3 существовал до него); чинить или нет — на усмотрение автора.

## Переиспользование
- 🔵 src/config.py:12 — `parse_timeout` дословно повторяет логику `parse_setting` (src/config.py:4): тот же `int()`, та же проверка `<= 0`, отличается только имя параметра и текст ошибки — violates: DRY («Do not duplicate code»). Путь рефакторинга: делегировать `return parse_setting(text)` (с потерей слова «timeout» в сообщении) либо вынести общий парсер с параметром текста ошибки.

## Эффективность
Не найдено.

## Качество
- 🟡 tests/test_config.py:18 — `test_timeout` покрывает только happy path; ветка ошибки `parse_timeout` (src/config.py:15-16) не покрыта ни одним тестом, хотя для аналогичной `parse_setting` error-path тест есть (`test_setting_rejects_zero`, tests/test_config.py:10) — violates: «Add or update focused tests for bug fixes, edge cases, and error paths when the project has testing in place». Ожидаемый тест: `pytest.raises(ValueError)` на `parse_timeout("0")` (и, опционально, на отрицательном значении).

## Верификация
- Оба файла прочитаны целиком, а не только дифф; дублирование и отсутствие error-path теста сверены с кодом.
- `python -m pytest tests -q` — ошибка коллекции (pre-existing, см. выше); `PYTHONPATH=src python -m pytest tests -q` — 3 passed. rtk-прогон с `PYTHONPATH` дал некорректный результат «No tests collected», поэтому финальная проверка выполнена без rtk.
- Корректность ветки ошибки `parse_timeout` подтверждена только чтением кода — исполняемого теста для неё нет (это и есть находка раздела «Качество»).

## Зависимости
Новых зависимостей нет; `pytest` уже использовался в файле до диффа.