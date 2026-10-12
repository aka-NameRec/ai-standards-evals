Тесты подтверждают дефект. Применяю малый безопасный фикс (одна строка, семантика однозначно задана docstring и исходной строкой в diff) и перепроверяю.
ai-standards v2.8.2

Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (проект не выполнял `ai-sync sync-templates`) — отчёт по fallback-форме.

**Задача** — review текущего диффа (staged: `src/account.py`).

**Что сделано**
- Прочитан дифф и полный код `src/account.py`, проверен контекст (docstring, тесты).
- Прогнан тестовый набор до и после правки.

**Как сделано**
- Проверка корректности по диффу с чтением кода, а не только diff; фикс малой правки выполнен по политике «Fixing While Reviewing» и перепроверен тестами.

**Корректность**
- ✅ src/account.py:6 — сравнение инвертировано: `return amount >= balance` разрешает снятие, когда сумма **больше или равна** остатку, что противоположно контракту docstring «Return whether ``amount`` may be withdrawn» и исходному `amount <= balance`; обычное снятие `can_withdraw(100, 40)` возвращало `False`, тест `tests/test_account.py:5` падал — нарушено: корректность (контракт функции задан docstring; сохранение поведения). → fixed: возвращено `amount <= balance`; `PYTHONPATH=src python -m pytest -q` — 1 passed.

**Архитектура и конвенции**
- Не найдено.

**Переиспользование**
- Не найдено.

**Эффективность**
- Не найдено.

**Качество**
- Не найдено.

**Проверки**
- `PYTHONPATH=src python -m pytest -q`: до фикса — 1 failed (`test_routine_withdrawal`), после — 1 passed. Примечание: без `PYTHONPATH=src` тесты не собираются (`ModuleNotFoundError: No module named 'account'`) — conftest.py пуст (pre-existing, вне рамок диффа).

**Зависимости**
- Не найдено.