The pytest run collected from the wrong root and `src` isn't on the import path (conftest.py is empty). Retrying from the fixture directory with `PYTHONPATH=src`:
Оба прохода завершены: дефект подтверждён существующим тестом. Файл `.ai-standards/code-review-report.md` в проекте отсутствует (шаблоны не синхронизированы через `ai-sync sync-templates`), поэтому отчёт собран по резервной структуре из правил. Отчёт размещён в чате (в код-блоке).

```markdown
ai-standards v2.6.0

## Код-ревью

### Что сделано
В `can_withdraw` оператор сравнения изменён с `<=` на `>=`: функция теперь разрешает снятие только когда сумма не меньше баланса.

### Как сделано
Однострочное изменение, существующий стиль модуля (типизация, docstring) сохранён.

### Корректность
- 🔴 src/account.py:6 — условие инвертировано: `amount >= balance` блокирует обычное снятие (`can_withdraw(100, 40)` → `False`) и разрешает овердрафт (`can_withdraw(100, 150)` → `True`) — нарушает: контракт функции (docstring «Return whether ``amount`` may be withdrawn from ``balance``» — снятие допустимо лишь при `amount <= balance`) и тест tests/test_account.py:5

### Архитектура и конвенции
Не найдено.

### Переиспользование
Не найдено.

### Эффективность
Не найдено.

### Качество
Не найдено.

### Проверки
- `PYTHONPATH=src python -m pytest -q` — 1 failed: `test_routine_withdrawal` (`assert False is True`, tests/test_account.py:5); дефект воспроизведён существующим тестом, правку не вносил — изменение уже в индексе git, исправление остаётся за автором.
- Без `PYTHONPATH=src` тесты не собираются (`ModuleNotFoundError: No module named 'account'`, conftest.py пуст) — упаковку и пути импорта не проверял; проверены только `src/account.py` и его тест.
```

Найден один блокирующий дефект: инвертированное условие в src/account.py:6 ломает правило снятия средств и валит существующий тест.