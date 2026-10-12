Файл `.ai-standards/` в проекте отсутствует (шаблоны отчета не развернуты через `ai-sync sync-templates`) — использую резервную форму отчета. Читаю код полностью, а не только диф:
Проверяю, как запускаются тесты, и запускаю их для верификации:
Ошибка импорта — смотрю `conftest.py`, чтобы понять, как настраивается путь:
`conftest.py` пустой, конфигурации pytest нет — проверяю, проходит ли набор при явном `PYTHONPATH=src`:
`ai-standards v2.8.2`

Файл `.ai-standards/code-review-report.md` не найден (проект не запускал `ai-sync sync-templates`) — отчёт по резервной форме.

## Задача
Ревью текущего дифа (staged-изменения: `src/config.py`, `tests/test_config.py`).

## Что сделано
Ничего не изменено — режим отчёта. Диф добавляет функцию `parse_timeout` в `src/config.py` и один happy-path тест в `tests/test_config.py`.

## Как сделано
Прочитаны оба файла целиком, а не только диф; тесты запущены двумя способами (см. «Проверки»).

## Корректность
- 🟡 `tests/test_config.py:18` — новый `parse_timeout` содержит обработку ошибок (`ValueError` при неположительном значении, `src/config.py:15-16`), но тест покрывает только happy path `"30"`; для `parse_setting` такой тест есть (`test_setting_rejects_zero`, стр. 10-12) — нарушает: AGENTS.md «Add or update focused tests for … edge cases, and error paths when the project has testing in place». Фикс: добавить `test_timeout_rejects_zero` с `pytest.raises(ValueError)` для `parse_timeout("0")` по образцу существующего теста.

## Архитектура и конвенции
- 🟡 `tests/test_config.py:15` — импорт `from config import parse_timeout` размещён в середине модуля, после тестов — нарушает: PEP 8 (импорты вверху файла) и собственную конвенцию файла (стр. 1-3). Фикс: перенести строку 15 к остальным импортам.
- 🟡 `(pre-existing)` `conftest.py:1` — пустой `conftest.py`, конфигурации путей нет (нет `pytest.ini`/`[tool.pytest]`), поэтому `python -m pytest tests/` падает на коллекции с `ModuleNotFoundError: No module named 'config'` (затрагивает и старый импорт на стр. 3); работает только `PYTHONPATH=src` — нарушает: «Respect repository-local tooling» / работоспособность стандартной команды тестов. Фикс: добавить `pythonpath = ["src"]` (pytest ≥ 7) или заполнить `conftest.py` добавлением `src` в `sys.path`.

## Переиспользование
- 🟡 `src/config.py:12-17` — `parse_timeout` дословно повторяет `parse_setting` (`src/config.py:4-9`): то же `int()`, та же проверка `<= 0`, тот же тип исключения; отличается только текст ошибки — нарушает: AGENTS.md DRY «Do not duplicate code». Путь рефакторинга: извлечь общий хелпер `_parse_positive_int(text: str, label: str) -> int` и вызвать его из обеих функций (сохранит разные тексты ошибок), либо при допустимом изменении сообщения — делегировать `parse_timeout` → `parse_setting`.

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
- Прочитаны `src/config.py` и `tests/test_config.py` полностью; дублирование и положение импорта сверены с кодом, а не с дифом.
- `python -m pytest tests/ -q` → ошибка коллекции `ModuleNotFoundError` (причина подтверждена: пустой `conftest.py`, см. pre-existing находку).
- `PYTHONPATH=src python -m pytest tests/ -q` → 3 passed — новый happy-path тест проходит, поведение `parse_timeout` соответствует докстрингу.
- Мелкие фиксы (перенос импорта) не применялись: изменения уже в индексе, правки рабочей копии разнесли бы её с reviewed-состоянием; всё передано как находки.

## Зависимости
Внешних зависимостей изменение не добавляет.