Файлы `.ai-standards/` отсутствуют — упрощённый формат отчёта. Изменения в `src/account.py` staged; смотрю `git diff --cached` и сам файл.
Diff найден — правка одной строки в `can_withdraw`. Проверяю код, а не только diff: смотрю структуру репозитория, тесты и вызовы функции.
Тест `test_routine_withdrawal` asserts `can_withdraw(100, 40) is True` — против нового кода это должно падать. Проверяю запуском.
Тест подтвердил дефект (в сводке rtk «No tests collected» — вводящий в заблуждение; в полном логе: `1 failed`, `can_withdraw(100, 40)` вернул `False`).

Примечание: файл `.ai-standards/code-review-report.md` в проекте отсутствует (`ai-sync sync-templates` не запускался), поэтому отчёт по резервному формату из правил.

---

# Code review — `ai-standards v2.6.0`

## Задача
Ревью текущего staged-диффа (запрос «code review», объём не сужён).

## Что сделано
В `src/account.py` изменена одна строка в `can_withdraw`: `return amount <= balance` → `return amount >= balance`. Изменение staged, не закоммичено (поверх `92d706d feat: withdrawal rule`).

## Как сделано
Правка инвертирует оператор сравнения в единственном return функции; сигнатура, docstring и типы не менялись.

## Корректность
🔴 src/account.py:6 — условие вывода средств инвертировано: обычное снятие запрещено, овердрафт разрешён (`can_withdraw(100, 40)` → `False`, `can_withdraw(100, 150)` → `True`) — violates: контракт docstring «Return whether ``amount`` may be withdrawn from ``balance``» (src/account.py:5) и существующий тест tests/test_account.py:5, который теперь падает. Исправление: вернуть `return amount <= balance`. Фиксировать текущее состояние нельзя.

## Архитектура и конвенции
Не найдено.

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
🔵 conftest.py:1 — `pytest` из корня репозитория собирает 0 тестов; тесты выполняются только с `PYTHONPATH=src` (conftest.py пуст, конфигурации путей нет) — violates: явного правила проекта нет; противоречит общему принципу, что стандартный запуск тестов работает из корня. `(pre-existing)`, к этому диффу не относится.

## Проверки
- `PYTHONPATH=src pytest tests -q` → `1 failed`: `test_routine_withdrawal — assert False is True`, где `False = can_withdraw(100, 40)` — корневая причина (инверсия сравнения в src/account.py:6) подтверждена на самом вероятном пути отказа.
- Прогон фикса не выполнялся (правка не применяется без явного запроса автора).

## Зависимости
Блокирует commit: staged-изменение ломает существующий тест. Единственное изменение — откат строки src/account.py:6 к `amount <= balance`; других зависимостей нет.