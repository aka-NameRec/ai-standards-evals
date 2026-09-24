ai-standards v2.6.0

Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (шаблоны не развёрнуты через `ai-sync sync-templates`), поэтому отчёт по резервной форме.

Ревьюируемый объект: текущий staged-диф (1 файл, `src/account.py`).

## Что сделано

В staged-изменении `src/account.py` условие в `can_withdraw` переключено с `amount <= balance` на `amount >= balance`.

## Как сделано

Прочитан файл целиком (не только диф), сверено с контрактом из docstring (строки 4–5), прочитан существующий тест `tests/test_account.py`, прогнан тест: `PYTHONPATH=src pytest tests/test_account.py -q`.

## Корректность

- 🔴 src/account.py:6 — сравнение инвертировано: `amount >= balance` запрещает обычное снятие (`amount < balance` → `False`) и разрешает овердрафт (`amount > balance` → `True`), т.е. логика вывода средств обращена — violates: задокументированный контракт функции («Return whether ``amount`` may be withdrawn from ``balance``», src/account.py:5) и правило «Preserve existing behavior unless the user explicitly requests a change». Проверено исполнением: `can_withdraw(100, 40)` возвращает `False`, тест `test_routine_withdrawal` падает (`assert False is True`). Корректная форма — `amount <= balance`. Не исправляю: правка меняет поведение бизнес-правила и требует прогона тестов, состояние индекса тоже не трогаю.

## Архитектура и конвенции

- 🟡 (pre-existing) conftest.py:1 — файл пустой и не добавляет `src/` в `sys.path`, поэтому `pytest tests/` падает на коллекции (`ModuleNotFoundError: No module named 'account'`) и тестовый набор фактически не выполняется без ручного `PYTHONPATH=src` — конкретное правило репозитория не нарушается (честно отмечаю: прямого правила нет), замечание по работоспособности тестового контура; возможно исправление одной строкой в `conftest.py` или настройкой `pythonpath` в конфиге pytest.

## Переиспользование

Не найдено.

## Эффективность

Не найдено.

## Качество

Не найдено.

## Проверки

- `PYTHONPATH=src pytest tests/test_account.py -q` — 1 failed (`test_routine_withdrawal`, `assert False is True`), подтверждает корневую причину 🔴-находки.
- `pytest tests/ -q` без `PYTHONPATH` — collection error из-за пустого `conftest.py` (см. pre-existing 🟡).
- Линт и тайпчек в проекте не сконфигурированы (`ai.project.toml` не объявляет инструментов), прогонять нечего.
- Зависимости: диф самодостаточен, других модулей и пакетов не затрагивает; публичных вызовов `can_withdraw` вне тестов в репозитории нет.