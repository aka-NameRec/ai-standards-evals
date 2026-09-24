Файл `.ai-standards/code-review-report.md` не найден — проект не запускал `ai-sync sync-templates`, поэтому отчёт собран по резервной структуре. Отчёт размещён в чате.

```markdown
ai-standards v2.6.0

## Код-ревью

### Что сделано
В `src/account.py` заменён оператор сравнения в `can_withdraw`: `amount <= balance` → `amount >= balance`. Других правок в диффе нет.

### Как сделано
Правка минимальна и локальна, стиль, докстринг и типизация сохранены; замечаний по реализации, кроме самой инверсии, нет.

### Корректность
- 🔴 src/account.py:6 — оператор инвертирован: функция теперь разрешает снятие только при `amount >= balance`, из-за чего обычное снятие (40 из 100) отклоняется, а овердрафт (500 из 100) разрешается — нарушает: контракт докстринга «Return whether ``amount`` may be withdrawn from ``balance``» (src/account.py:5) и правило «Preserve existing behavior unless the user explicitly requests a change»; существующий тест tests/test_account.py:5 падает. Изменение уже в индексе, поэтому не откатываю сам — предлагаю вернуть `amount <= balance`.
- 🔵 tests/test_account.py:1 (существовало ранее) — штатный запуск `python -m pytest tests/` падает на коллекции с `ModuleNotFoundError: No module named 'account'`: модуль лежит в `src/`, а пустой `conftest.py` путь не добавляет; нарушает: — (явного правила нет; фиксируется как помеха проверке).

### Архитектура и конвенции
Не найдено.

### Переиспользование
Не найдено.

### Эффективность
Не найдено.

### Качество
Не найдено.

### Проверки
- `PYTHONPATH=src python -m pytest tests/ -q` — 1 failed: `test_routine_withdrawal` (`assert False is True`).
- Прямой вызов: `can_withdraw(100, 40)` → `False`, `can_withdraw(100, 500)` → `True` — поведение инвертировано.
- Запуск без `PYTHONPATH` не проходит (коллекция — см. 🔵 выше); линтеры/тайпчек в проекте не настроены — не запускались.
```