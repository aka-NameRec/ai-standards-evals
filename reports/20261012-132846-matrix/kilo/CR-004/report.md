**ai-standards v2.8.1**

Примечание: файлов `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте нет (проект не запускал `ai-sync sync-templates`), поэтому отчёт в fallback-формате.

## Что сделано
Изменена одна строка в `src/account.py`: в `can_withdraw` оператор сравнения `amount <= balance` заменён на `amount >= balance`.

## Как сделано
Без изменения docstring, типов и тестов; правка ограничена телом функции.

## Корректность
- 🔴 src/account.py:6 — оператор инвертирован: функция теперь разрешает вывод при `amount >= balance`, то есть блокирует обычное снятие (40 из 100 → `False`) и разрешает овердрафт (150 из 100 → `True`); фактически допустимым остаётся только вывод всей суммы — violates: контракт docstring `can_withdraw` («Return whether ``amount`` may be withdrawn») и правило «Preserve existing behavior unless the user explicitly requests a change»; подтверждено упавшим тестом `tests/test_account.py:5` (`test_routine_withdrawal`, ожидается `can_withdraw(100, 40) is True`) и прямым прогоном граничных случаев. Корректное условие — исходное `amount <= balance`.

## Архитектура и конвенции
Не найдено.

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
- `PYTHONPATH=tests:src python -m pytest tests -q` — 1 failed (`test_routine_withdrawal`, `assert False is True`).
- Прямой прогон: `can_withdraw(100, 40)` → `False` (ожидалось `True`), `can_withdraw(100, 150)` → `True` (ожидалось `False`), `can_withdraw(100, 100)` → `True`.
- Чистый запуск `python -m pytest` без `PYTHONPATH` в этом окружении падает на импорте (`ModuleNotFoundError: No module named 'account'`) — инфраструктура путей проекта вне рамок данного диффа, не оценивал как находку.

## Зависимости
Не найдено.

Исправление (возврат к `amount <= balance`) не применял: по умолчанию ревью ограничивается отчётом, а правка меняет замысел автора диффа.