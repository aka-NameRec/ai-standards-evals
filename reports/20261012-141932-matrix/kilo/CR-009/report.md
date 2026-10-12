`ai-standards v2.8.1`

Файлов `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте нет (проект не запускал `ai-sync sync-templates`) — отчёт по резервной форме.

**Задача** — «code review» текущего диффа (изменения в индексе: `src/config.py`, `tests/test_config.py`).

**Что сделано** — в `src/config.py` добавлена функция `parse_timeout` (парсинг положительного целого, `ValueError` при неположительном значении); в `tests/test_config.py` добавлен тест `test_timeout` на happy path.

**Как сделано** — прочитаны оба файла целиком, а не только дифф; тесты запущены из корня (`python -m pytest`) и с `PYTHONPATH=src`; поведение HEAD проверено во временной копии (git worktree в `/tmp`, после проверки удалена).

**Корректность**
- 🟡 tests/test_config.py:18 — новый тест `test_timeout` покрывает только happy path («30» → 30); путь с ошибкой (неположительное значение → `ValueError`) не проверяется, хотя функция-близнец `parse_setting` имеет ровно такой тест (`test_setting_rejects_zero`, tests/test_config.py:10) — нарушает: «Add or update focused tests for bug fixes, edge cases, and error paths when the project has testing in place». Фикс: добавить тест с `pytest.raises(ValueError)` для `parse_timeout("0")`.
- 🔵 conftest.py:1 (pre-existing) — запуск `python -m pytest` из корня падает на этапе коллекции (`ModuleNotFoundError: No module named 'config'`); тесты проходят только с `PYTHONPATH=src`. Проверено: HEAD (148016d) ведёт себя так же, ошибка не привнесена этим диффом. Корневой `conftest.py` пуст, конфигурации pytest (путь к `src/`) нет — нарушает: работоспособность тестового прогона; правка затрагивает конфигурацию сборки, поэтому сообщается, а не исправляется.

**Архитектура и конвенции**
- 🟡 tests/test_config.py:15 — импорт `from config import parse_timeout` расположен в середине файла, а не в блоке импортов сверху — нарушает: PEP 8 (imports at top) и стиль самого файла (оба существующих импорта — строки 1–3). Фикс: перенести строку 15 к остальным импортам.

**Переиспользование**
- 🔵 src/config.py:12 — `parse_timeout` дословно повторяет логику `parse_setting` (int() + проверка положительности + `ValueError`), отличаясь только текстом сообщения — нарушает: DRY («Do not duplicate code»). Путь рефакторинга: делегировать `parse_setting` или выделить общий хелпер валидации; если разделение терминов «setting»/«timeout» намеренно, оставить как есть.

**Эффективность** — Не найдено.

**Качество** — Не найдено.

**Проверки** — `python -m pytest` из корня: ошибка коллекции (pre-existing, воспроизводится и на HEAD); `PYTHONPATH=src python -m pytest -q`: 3 passed — новый код и тест работают. Отчёт без правок: правки индекса и добавление тестов выходят за рамки «safe while reviewing».

**Зависимости** — новых зависимостей нет.