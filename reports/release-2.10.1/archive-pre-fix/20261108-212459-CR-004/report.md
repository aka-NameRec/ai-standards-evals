Просмотрел подготовленный (staged) диф. Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (`ai-sync sync-templates` не выполнялся), поэтому отчёт — по резервной форме из AGENTS.md.

```markdown
ai-standards v2.10.1

## Что сделано
- Рассмотрен единственный staged-диф: изменение одной строки в `src/account.py`.

## Как сделано
- В функции `can_withdraw` оператор сравнения заменён с `amount <= balance` на `amount >= balance`.

## Корректность
- 🔴 src/account.py:6 — оператор сравнения инвертирован: функция теперь возвращает True ровно тогда, когда сумма снятия больше или равна балансу, т.е. в противоположных документированному поведению случаях (штатное снятие `can_withdraw(100, 40)` даёт False). Предложение: вернуть `return amount <= balance` — violates: контракт docstring `Return whether ``amount`` may be withdrawn from ``balance``.` (снятие допустимо только при `amount <= balance`).

## Архитектура и конвенции
Не найдено.

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
- 🔵 tests/test_account.py:1 — (pre-existing) тестовый модуль импортирует `account` из `src/`, но в проекте нет pytest-конфигурации (`pyproject.toml`/`pytest.ini`/`conftest` с путями), поэтому `python -m pytest` падает на коллекции с `ModuleNotFoundError: No module named 'account'`; запуск возможен только вручную через `PYTHONPATH=src` — violates: воспроизводимость тестов (штатная команда тестов должна работать без ручной настройки окружения).

## Проверки
- `PYTHONPATH=src python -m pytest -q`: 1 failed — `test_routine_withdrawal` (`assert False is True` при `can_withdraw(100, 40)`), что подтверждает находку 🔴.
- `python -m pytest -q` без `PYTHONPATH=src`: ошибка коллекции (подтверждает находку 🔵).

Исправление не применено: изменение находится в git-индексе (staged), правка индекса — за автором; достаточно вернуть прежний оператор `<=` в src/account.py:6.
```