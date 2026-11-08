```markdown
# Code Review

ai-standards 2.10.1

## Задача
Не указана. Ревью текущего staged-диффа (`src/account.py`).

## Что сделано
Изменено одно выражение в `can_withdraw`: `amount <= balance` → `amount >= balance`.

## Как сделано
Инверсия оператора сравнения в единственной строке функции; docstring и сигнатура не менялись.

## Корректность
- 🔴 src/account.py:6 — оператор сравнения инвертирован: теперь снятие разрешено, только если `amount >= balance`, т.е. ровно когда средств не хватает; обычное снятие меньшей суммы возвращает `False`. Противоречит контракту docstring «Return whether ``amount`` may be withdrawn from ``balance``» — violates: Preserve existing behavior unless the user explicitly requests a change; контракт функции задан её docstring. Подтверждено прогоном теста: `test_routine_withdrawal` (`assert can_withdraw(100, 40) is True`) падает — `False is True`. Вернуть `return amount <= balance`.

## Архитектура и конвенции
Не найдено.

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
- 🟡 tests/test_account.py:1 (pre-existing) — `from account import can_withdraw` при расположении модуля в `src/`: голый прогон `python -m pytest tests/` падает на сборке с `ModuleNotFoundError: No module named 'account'`, тесты запускаются только с `PYTHONPATH=src` — violates: тесты должны запускаться стандартной командой проекта; предложить `pythonpath = ["src"]` в pytest-конфигурации как follow-up.

## Проверки
- `python -m pytest tests/ -q` — сборка падает (`ModuleNotFoundError`, см. Качество).
- `PYTHONPATH=src python -m pytest tests/ -q` — 1 failed: `test_routine_withdrawal`, `can_withdraw(100, 40)` вернул `False` вместо `True`. Дифф не прошёл проверку.

## Зависимости
Секция опущена: изменение самодостаточно, зависимости не затронуты.
```

Не найдено `.ai-standards/code-review-report.md` — проект не запускал `ai-sync sync-templates`, поэтому отчёт собран по fallback-форме из инструкций.

Блокирующий дефект: правка в индексе инвертирует логику `can_withdraw`. Исправление (возврат `amount <= balance` в src/account.py:6) затрагивает состояние git-индекса, поэтому по правилам ревью оно сообщено, а не применено — применю по отдельной просьбе.