Файл `.ai-standards/code-review-report.md` отсутствует — проект не запускал `ai-sync sync-templates`, поэтому использую резервный формат отчёта. Смотрю диф:
Тест подтверждает ожидаемое поведение. Запускаю его для верификации:
ai-standards v2.6.0

Примечание: файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (не выполнялся `ai-sync sync-templates`) — отчёт по резервной форме.

## Задача
Не указана — выполнен ревью текущего staged-диффа.

## Что сделано
Просмотрен staged-дифф (`src/account.py`, 1 строка), файл прочитан целиком, поведение сверено с докстрингом и существующим тестом.

## Как сделано
- `git status`, `git diff --cached` — граница ревью.
- Чтение `src/account.py`, `tests/test_account.py`, `conftest.py`.
- Прогон тестов `pytest tests/ -q` с `PYTHONPATH=src` — подтверждено падение.

## Correctness
- 🔴 `src/account.py:6` — оператор сравнения инвертирован: `amount >= balance` возвращает `True` ровно тогда, когда снятие невозможно (например, `can_withdraw(100, 150)` → `True`, а `can_withdraw(100, 40)` → `False`), то есть контракт из докстринга «Return whether ``amount`` may be withdrawn from ``balance``» нарушен — violates: Preserve existing behavior / задокументированный контракт функции; подтверждено падением `tests/test_account.py:5` (`assert can_withdraw(100, 40) is True` → `False`). Корректное выражение: `return amount <= balance`. Не исправляю: правка меняет состояние git-индекса пользователя.
- 🟡 `tests/test_account.py:1` (pre-existing) — тесты не запускаются без ручного `PYTHONPATH=src`: `ModuleNotFoundError: No module named 'account'`, `conftest.py` пуст — violates: Keep file and module structure coherent and predictable.

## Architecture & Conventions
Не найдено.

## Reuse
Не найдено.

## Efficiency
Не найдено.

## Quality
Не найдено.

## Verification
- Прогон `PYTHONPATH=src pytest tests/ -q` — 1 failed: `test_routine_withdrawal`, `assert False is True`, что подтверждает находку Correctness и корневую причину (инверсия оператора в `src/account.py:6`).
- Без `PYTHONPATH=src` сборка тестов падает на импорте — см. находку (pre-existing) выше.

## Dependencies
Изменений зависимостей нет.