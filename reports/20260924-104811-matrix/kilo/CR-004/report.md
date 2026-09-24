`.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют — похоже, `ai-sync sync-templates` не запускался, поэтому использую резервный формат отчёта.

---

ai-standards v2.6.0

## Задача
Code review текущего диффа (staged-изменение в `src/account.py`).

## Что сделано
Изменён оператор сравнения в `can_withdraw`: `amount <= balance` → `amount >= balance`.

## Как сделано
Однострочная правка условия возврата; логика докстринга («можно ли снять `amount` с `balance`») не пересматривалась.

## Корректность
- 🔴 `src/account.py:6` — условие инвертировано: `amount >= balance` вместо `amount <= balance`. Обычное снятие теперь блокируется (`can_withdraw(100, 40) → False`), а снятие суммы больше баланса разрешается (`can_withdraw(100, 150) → True`) — violates: контракт докстринга `can_withdraw` («Return whether ``amount`` may be withdrawn from ``balance``»); подтверждено упавшим тестом `tests/test_account.py:5`.

## Архитектура и конвенции
- 🔵 `conftest.py:1` (pre-existing) — файл пуст и не добавляет `src` в `sys.path`, проект не упакован, поэтому `python -m pytest` падает на этапе коллекции (`ModuleNotFoundError: No module named 'account'`); тесты запускаются только с ручным `PYTHONPATH=src` — violates: воспроизводимость запуска тестов (AGENTS.md: «Add or update focused tests… when the project has testing in place» предполагает, что тесты запускаются). Может быть исправлено отдельным фоллоу-апом.

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
- Прочитан итоговый код `src/account.py`, а не только дифф.
- `PYTHONPATH=src python -m pytest -q` — 1 failed: `test_routine_withdrawal` (`can_withdraw(100, 40)` вернул `False`), что эмпирически подтверждает дефект. Без `PYTHONPATH` коллекция падает (см. pre-existing замечание).

## Зависимости
Новых зависимостей нет; на поведение ничего кроме `src/account.py` не влияет.

---

Исправление (возврат к `amount <= balance`) не применял — по умолчанию ревью только сообщает о проблемах; правка тривиальна и безопасна, если попросите — применю.