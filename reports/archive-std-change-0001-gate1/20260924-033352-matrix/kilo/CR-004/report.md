**ai-standards v2.6.0**

В проекте нет каталога `.ai-standards/` (файлы `code-review-report.md` и `references/code-review-reporting.md` отсутствуют — `ai-sync sync-templates` не запускался), поэтому отчёт по fallback-форме из инструкций. Ревьюируется текущий diff: staged-изменение `src/account.py` (1 файл, ±1).

## Что сделано
В `can_withdraw` изменён оператор сравнения: `return amount <= balance` → `return amount >= balance`.

## Как сделано
Однострочная правка условия возврата в `src/account.py`, других изменений в диффе нет.

## Корректность
- 🔴 src/account.py:6 — условие инвертировано: `amount >= balance` разрешает снятие только когда снимают весь баланс или больше него, а обычное снятие (40 из 100) отклоняется; нужно вернуть `amount <= balance` — violates: задокументированный контракт `can_withdraw` (docstring в src/account.py:5: «Return whether ``amount`` may be withdrawn from ``balance``») и правило «Preserve existing behavior unless the user explicitly requests a change»; существующий тест tests/test_account.py:5 на этом падает.

Не исправляю: дефект находится в уже staged-изменении (состояние git-индекса — зона «report, not fix»), правку (`<=` вместо `>=`) должен внести автор, поправив staged-версию.

## Архитектура и конвенции
Не найдено.

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
- `PYTHONPATH=src pytest tests/ -q` → 1 failed: `test_routine_withdrawal` — `assert False is True`, где `False = can_withdraw(100, 40)`. Подтверждает корневую причину из 🔴-находки.
- (pre-existing, вне диффа) без `PYTHONPATH=src` сбор тестов падает: `ModuleNotFoundError: No module named 'account'` — в репозитории нет pytest-конфигурации путей, пустой `conftest.py` в корне её не добавляет. К дефекту диффа не относится; исправление — по отдельной задаче.