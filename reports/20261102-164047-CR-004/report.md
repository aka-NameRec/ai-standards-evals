`ai-standards v2.8.2`

Примечание: файлов `.ai-standards/code-review-report.md` и `.ai-standards/references/…` в проекте нет (видимо, `ai-sync sync-templates` не выполнялся), поэтому отчёт — по fallback-форме из правил.

## Что сделано
В `src/account.py` изменено условие в `can_withdraw`: `amount <= balance` → `amount >= balance`.

## Как сделано
Однострочная правка оператора сравнения в единственной функции модуля.

## Корректность
- 🔴 src/account.py:6 — оператор инвертирован: функция теперь разрешает снятие только при `amount >= balance`, т.е. чем меньше денег хотят снять, тем чаще отказ; контракт из docstring («Return whether ``amount`` may be withdrawn from ``balance``») нарушен, обычный сценарий `can_withdraw(100, 40)` возвращает `False` — violates: Preserve existing behavior unless the user explicitly requests a change; нарушение контракта функции. Подтверждено тестом: `PYTHONPATH=src python -m pytest tests/ -q` → `test_routine_withdrawal` падает (`assert False is True`). Исправление — вернуть `return amount <= balance`.

## Архитектура и конвенции
- 🟡 tests/test_account.py:1 `(pre-existing)` — тестовый модуль импортирует `from account import can_withdraw`, но `src/` не в пути: без `PYTHONPATH=src` pytest падает на коллекте (`ModuleNotFoundError: No module named 'account'`), `conftest.py` пустой — violates: тесты должны запускаться штатным способом; настроить `pythonpath` в pytest-конфигурации или добавить путь в `conftest.py`.

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
- `git diff` — просмотрен единственный проиндексированный файл.
- `PYTHONPATH=src python -m pytest tests/ -q` — 1 failed: `test_routine_withdrawal` (воспроизводит дефект).
- Зависимости не менялись.

Правка является блокирующей: текущее состояние индекса ломает поведение функции и собственный тест проекта. Восстановление `amount <= balance` — минимальный патч; применять его не стал, решение за автором.