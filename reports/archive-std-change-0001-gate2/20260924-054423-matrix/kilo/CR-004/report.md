Проверю failure path — запущу тесты.
Тест не собрался из-за пути импорта. Запущу с явным `PYTHONPATH` из корня фикстуры:
`ai-standards v2.6.0`

Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (шаблоны не синхронизированы через `ai-sync sync-templates`) — отчёт по fallback-форме.

## Корректность

- 🔴 src/account.py:6 — условие вывода инвертировано: `amount >= balance` разрешает снять больше остатка (`can_withdraw(100, 150)` → `True`) и запрещает обычное частичное снятие (`can_withdraw(100, 40)` → `False`); по докстрингу функция должна отвечать, допустимо ли снятие `amount` с баланса `balance`, т.е. `amount <= balance` — violates: контракт `can_withdraw` (docstring src/account.py:5) и правило сохранения существующего поведения; подтверждено падением существующего теста tests/test_account.py:5 (`assert can_withdraw(100, 40) is True` → `assert False is True`).

## Качество

- 🔵 tests/test_account.py:1 (pre-existing) — тесты не собираются штатным `pytest` из корня: пустой conftest.py не добавляет `src` в путь, нужен `PYTHONPATH=src` — violates: не маппится на конкретное правило; замечено при верификации, к данному diff не относится.

## Что сделано

В staged-изменениях один файл: src/account.py — изменено возвращаемое выражение `can_withdraw`.

## Как сделано

В src/account.py:6 сравнение `amount <= balance` заменено на `amount >= balance`.

## Архитектура и конвенции

Не найдено.

## Переиспользование

Не найдено.

## Эффективность

Не найдено.

## Проверки

- `git diff --cached`: 1 файл, 1 строка — просмотрен полностью.
- Тесты (`PYTHONPATH=src pytest tests -q`): 1 failed — `test_routine_withdrawal`, падение воспроизводит корневую причину (инвертированное условие). Без `PYTHONPATH=src` — ошибка сбора (`ModuleNotFoundError: No module named 'account'`), см. 🔵 выше.

## Зависимости

Внешних зависимостей и миграций нет. Исправление — вернуть `<=` в src/account.py:6; после этого тест tests/test_account.py:5 проходит (проверено чтением, прогон на исправленном коде не выполнялся, т.к. правка не применялась). Изменение уже в индексе, поэтому правку не применял — решает автор.