The mid-file import is a small fix that is safe by inspection (moving it to the existing import block changes nothing semantically), so I apply it and record it as a ✅ finding:
`ai-standards v2.9.0`

Примечание: `.ai-standards/code-review-report.md` и `.ai-standards/references/` в проекте отсутствуют — `ai-sync sync-templates` не выполнялся, отчёт по резервной форме. `ai.project.toml` запрашивает версию `feature/27-cherry-pick-assessment`, сгенерированный файл — v2.9.0.

**Задача:** ревью текущего диффа (staged: `src/config.py`, `tests/test_config.py`) — новая функция `parse_timeout` и тест к ней.

**Что сделано**
- Добавлена `parse_timeout` (src/config.py:12) — парсинг таймаута в секундах с `ValueError` для неположительных значений.
- Добавлен `test_timeout` (tests/test_config.py:15) — только happy path.

**Как сделано**
- `parse_timeout`: `int(text)` + проверка `value <= 0` с `ValueError("timeout must be positive")`.
- Тест: `assert parse_timeout("30") == 30`.

**Корректность**
- 🟡 tests/test_config.py:15 — `test_timeout` покрывает только happy path; путь ошибки новой `parse_timeout` (src/config.py:15-16, `ValueError` при `<= 0`, заявлен в docstring) не проверяется ни одним тестом, хотя для аналога `parse_setting` он покрыт (`test_setting_rejects_zero`) — нарушает: General Engineering Principles → «Add or update focused tests for … edge cases, and error paths when the project has testing in place». Фикс: добавить тест с `pytest.raises(ValueError)` для `parse_timeout("0")` (и опционально `"-5"`).
- ✅ tests/test_config.py:3 — импорт `parse_timeout` стоял посреди файла (после тестов), разделяя импорты одного модуля — нарушает: PEP 8 (импорты в начале файла) → fixed: объединён с существующим импортом из `config` в строке 3; правка в working tree, требуется повторный `git add`.

**Архитектура и конвенции**
- Не найдено.

**Переиспользование**
- 🔵 src/config.py:12-17 — `parse_timeout` почти дословно дублирует `parse_setting` (src/config.py:4-9): та же связка `int()` + проверка положительности, отличается только текст сообщения — нарушает: DRY («Do not duplicate code»). Путь рефакторинга: делегировать `parse_setting`, если текст «timeout must be positive» не критичен, либо выделить общий парсер положительного целого с параметром-меткой для сообщения. Не критично: функции по 6 строк, расхождение сообщений может быть намеренным.

**Эффективность**
- Не найдено.

**Качество**
- Не найдено.

**Проверки**
- `PYTHONPATH=src python -m pytest tests/ -q` — 3 passed (после применения ✅-правки).
- 🟡 (pre-existing) conftest.py:1 — без `PYTHONPATH=src` сборка тестов падает: `ModuleNotFoundError: No module named 'config'` (conftest пуст, конфига pytest с `pythonpath` нет); на HEAD (до диффа) воспроизводится так же. Предлагается follow-up: добавить `pythonpath = ["src"]` в конфиг pytest или заполнить conftest.

**Зависимости**
- Изменений зависимостей нет (только stdlib).