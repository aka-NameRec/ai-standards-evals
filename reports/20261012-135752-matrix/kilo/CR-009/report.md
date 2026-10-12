`ai-standards v2.8.1`

Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют — `ai-sync sync-templates` не запускался, поэтому отчёт по fallback-форме.

**Что сделано**
В diff (staged): в `src/config.py` добавлена функция `parse_timeout` (парсинг положительного таймаута в секундах, `ValueError` при неположительном значении); в `tests/test_config.py` добавлен импорт `parse_timeout` и один тест happy path.

**Как сделано**
`parse_timeout` повторяет структуру `parse_setting`: `int(text)`, проверка `value <= 0`, `raise ValueError`. Тест — только `assert parse_timeout("30") == 30`. Патч не читал дальше диффа — открыты оба файла целиком, поведение проверено запуском (см. `Проверки`).

**Корректность**
- 🟡 tests/test_config.py:18 — для новой функции `parse_timeout` покрыт только happy path; ветка ошибки (src/config.py:15-16, `ValueError` для `<= 0`) тестом не покрыта, хотя образец в этом же файле есть — `test_setting_rejects_zero` (tests/test_config.py:10-12) — violates: "Add or update focused tests for bug fixes, edge cases, and error paths when the project has testing in place."
- Остальное: поведение `parse_timeout` корректно (проверено напрямую, см. `Проверки`). Нарушений логики не найдено.

**Архитектура и конвенции**
- 🟡 tests/test_config.py:15 — импорт `from config import parse_timeout` размещён в середине файла, после тестов — violates: PEP 8 (все импорты в начале файла) и собственному стилю файла (tests/test_config.py:1-3). Перенести к существующим импортам.
- Замечание (pre-existing): без `PYTHONPATH=src` команда `python -m pytest` падает на коллекции с `ModuleNotFoundError: No module named 'config'` — конфигурации путей в репозитории нет (conftest.py пуст). К диффу не относится, конкретного правила не нарушает — приведено как риск для запуска проверок.

**Переиспользование**
- 🔵 src/config.py:12-17 — `parse_timeout` дублирует `parse_setting` (src/config.py:4-9): та же логика `int()` + проверка положительности, отличается только текст ошибки — violates: DRY ("Do not duplicate code"). Путь рефакторинга: общий хелпер `_parse_positive(text: str, label: str) -> int`, вызывающий `int()` и валидацию, с передачей названия величины в сообщение; либо одна общая функция, если таймаут не несёт собственной семантики.

**Эффективность**
Не найдено.

**Качество**
Не найдено.

**Проверки**
- `PYTHONPATH=src python -m pytest -q` — 3 passed.
- Прямая проверка `parse_timeout`: `"0"` и `"-5"` → `ValueError("timeout must positive")`... точнее `ValueError("timeout must be positive")`; `"30"` → 30. Поведение корректно — отсутствует именно тест.
- `python -m pytest` без `PYTHONPATH` — collection error (pre-existing, см. выше).

**Зависимости**
Не найдено.