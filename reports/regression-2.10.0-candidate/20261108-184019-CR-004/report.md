`ai-standards v2.9.0`

Файл `.ai-standards/code-review-report.md` не найден — проект не запускал `ai-sync sync-templates`, поэтому отчёт по fallback-форме.

## Что сделано

В индексе одно изменение: `src/account.py:6` — условие в `can_withdraw` заменено с `amount <= balance` на `amount >= balance`.

## Как сделано

Изменение однострочное: инвертирован оператор сравнения без других правок.

## Корректность

- 🔴 `src/account.py:6` — условие инвертировано: `amount >= balance` разрешает вывод только при сумме, большей или равной балансу. Обычный вывод `can_withdraw(100, 40)` возвращает `False`, а овердрафт `can_withdraw(100, 150)` — `True`; это нарушает контракт docstring «Return whether ``amount`` may be withdrawn from ``balance``» и ломает существующий тест `tests/test_account.py:5` — violates: Preserve existing behavior unless the user explicitly requests a change (изменение семантики без запроса).

## Архитектура и конвенции

Не найдено.

## Переиспользование

Не найдено.

## Эффективность

Не найдено.

## Качество

- 🟡 `conftest.py:1` (pre-existing) — `conftest.py` пустой, а тест импортирует `from account import can_withdraw` при src-раскладке; `python -m pytest` из корня падает с `ModuleNotFoundError: No module named 'account'`, тесты запускаются только через `PYTHONPATH=src` — violates: General Engineering Principles — verification must be task-appropriate and runnable (тестовый прогон не работает стандартной командой).

## Проверки

- С изменением: `PYTHONPATH=src python -m pytest` — `1 failed` (`test_routine_withdrawal`, `assert False is True`).
- На базовой версии (изменение временно убрано через `git stash --staged` и возвращено обратно): `1 passed` — подтверждает, что дефект внесён именно этим изменением.
- Граничные пробы с изменением: `can_withdraw(100, 40) → False`, `can_withdraw(100, 100) → True`, `can_withdraw(100, 150) → True`.
- Состояние индекса восстановлено (`git add src/account.py` после stash pop), артефакты прогонов (`__pycache__`) удалены.

## Зависимости

Не найдено.

Рекомендуемое исправление: вернуть `return amount <= balance` в `src/account.py:6`. Изменение не применял — правка находится в вашем индексе под коммит.