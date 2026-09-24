The staged diff inverts the withdrawal rule. The fix is a one-operator revert whose safety follows from reading alone (the docstring contract plus the committed test), so per the small-fix policy I apply it and record it as ✅.
ai-standards v2.6.0

Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют — `ai-sync sync-templates` не запускался, поэтому отчёт по резервному формату из правил.

## Что сделано
Проанализирован текущий диф (staged-изменение `src/account.py`); проверка по коду, а не только по диффу; тесты запущены.

## Как сделано
- `git status`, `git diff HEAD`, чтение `src/account.py` и `tests/test_account.py`.
- Прогон тестов (`PYTHONPATH=src python -m pytest -q`) до и после фикса.

## Корректность
- ✅ src/account.py:6 — оператор сравнения в дифе инвертирован: `amount >= balance` отвергает обычное снятие (40 при балансе 100) и разрешает овердрафт (150 при балансе 100), нарушая контракт докстринга «Return whether ``amount`` may be withdrawn from ``balance``» (src/account.py:5) и ломая тест `test_routine_withdrawal` (tests/test_account.py:5, падение подтверждено прогоном) — violates: сохранение существующего поведения / контракт докстринга → fixed: восстановлено `amount <= balance`; `PYTHONPATH=src python -m pytest -q` — 1 passed.
- 🟡 (pre-existing) conftest.py:1 — пустой `conftest.py` не добавляет `src` в `sys.path`, поэтому `pytest` без `PYTHONPATH=src` падает на импорте `from account import ...` (tests/test_account.py:1, ModuleNotFoundError подтверждён) — violates: воспроизводимость тестового прогона без ручных переменных окружения.

## Архитектура и конвенции
Не найдено.

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
- `PYTHONPATH=src python -m pytest -q`: до фикса 1 failed, после фикса 1 passed.
- Чистый `python -m pytest -q` не собирает тесты (см. pre-existing находку) — оставлено как есть, правка вне рамок ревью.

## Зависимости
- Фикс одной строки, зависимостей не добавляет; pre-existing проблему с путями тестов можно устранить отдельной правкой `conftest.py` по запросу.