Файлы `.ai-standards/` в проекте отсутствуют — использую fallback-формат отчёта. Проверяю, как запускаются тесты:
Запустил из неверной директории. Повторяю из корня фикстуры:
Ревью завершено. Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (шаблоны не синхронизированы), поэтому отчёт в fallback-формате.

---

**ai-standards v2.6.0**

## Что сделано

Проверен текущий staged-диф (2 файла, +15): в `src/config.py` добавлена функция `parse_timeout()`, в `tests/test_config.py` — happy-path тест `test_timeout`. Существующее поведение не изменялось.

## Как сделано

Прочитаны оба изменённых файла целиком, а также `parse_setting()` (src/config.py:4) и соседние тесты для проверки дублирования и конвенций. Запущен тестовый прогон.

## Корректность

- 🟡 tests/test_config.py:18 — `test_timeout` покрывает только happy path («30» → 30); заявленный в docstring контракт «raises ValueError for non-positive input» (src/config.py:13) не проверен ни одним тестом, тогда как для аналогичной `parse_setting` error path покрыт (`test_setting_rejects_zero`, tests/test_config.py:10) — violates: «Add or update focused tests for bug fixes, edge cases, and error paths when the project has testing in place». Фикс: добавить тест `parse_timeout("0")` (и/или отрицательного значения) через `pytest.raises(ValueError)`.

## Архитектура и конвенции

- 🟡 tests/test_config.py:15 — импорт `from config import parse_timeout` размещён в середине файла после тестов, вместо объединения с существующим верхним импортом `from config import parse_setting` (tests/test_config.py:3) в одну строку — violates: PEP 8 (imports at top of file) и конвенция самого файла.

## Переиспользование

- 🟡 src/config.py:12 — `parse_timeout` дословно повторяет тело `parse_setting` (src/config.py:4–9), отличаясь только текстом ошибки — violates: DRY, «Do not duplicate code». Путь рефакторинга: делегировать `parse_timeout` → `parse_setting` либо вынести общий хелпер с параметром сообщения; текущие тесты текст ошибки не проверяют, так что делегирование безопасно (меняется только текст: «must be positive» вместо «timeout must be positive»).

## Эффективность

Не найдено.

## Качество

Не найдено.

## Проверки

- `PYTHONPATH=src python -m pytest -q` из корня проекта: **3 passed**. Запуск без `PYTHONPATH=src` падает на коллекции (`ModuleNotFoundError: No module named 'config'`) — это ограничение компоновки, существовавшее до дифа (pre-existing), сюда не относится.
- Ничего не исправлял — все три находки требуют тестового прогона для подтверждения или затрагивают staged-состояние индекса, поэтому только отчёт.
- Замечание по инструменту: `rtk pytest` дважды неверно отобразил результат («No tests collected» при фактически пройденных тестах); прогоны перепроверены прямым `python -m pytest`.

## Зависимости

Новые зависимости не добавлены. Тесты зависят от `src` в `PYTHONPATH` (pytest-конфигурация в репозитории не закреплена — pre-existing).