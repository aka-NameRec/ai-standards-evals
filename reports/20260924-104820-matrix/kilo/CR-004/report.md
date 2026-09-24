Ревью провёл по текущему staged-диффу. Файла `.ai-standards/code-review-report.md` в проекте нет (значит, `ai-sync sync-templates` не запускался), поэтому использую fallback-структуру из правил. Отчёт размещён в чате:

```markdown
ai-standards v2.6.0

## Код-ревью

### Что сделано
В `can_withdraw` перевёрнут оператор сравнения, определяющий допустимость снятия средств: `amount <= balance` → `amount >= balance`.

### Как сделано
Изменение однострочное, стиль, типы и docstring сохранены; нарушений конвенций и мест для переиспользования в диффе нет.

### Корректность
- 🔴 src/account.py:6 — оператор сравнения перевёрнут: обычное снятие блокируется, а овердрафт разрешается (`can_withdraw(100, 40)` → False, `can_withdraw(100, 150)` → True); существующий тест tests/test_account.py:5 падает — нарушает: контракт функции (docstring в src/account.py:5: «Return whether ``amount`` may be withdrawn from ``balance``») и тест tests/test_account.py:5.
- 🟡 (существовало ранее) tests/test_account.py:1 — тесты не запускаются обычной командой `pytest`: импорт `from account import can_withdraw` требует `src` в `PYTHONPATH`, conftest.py пуст; `python -m pytest -q` падает на коллекции с `ModuleNotFoundError`, проходит только `PYTHONPATH=src python -m pytest -q` — нарушает: воспроизводимость тестового прогона без ручной настройки окружения.

### Архитектура и конвенции
Не найдено.

### Переиспользование
Не найдено.

### Эффективность
Не найдено.

### Качество
Не найдено.

### Проверки
- `PYTHONPATH=src python -m pytest -q` — 1 failed (`test_routine_withdrawal`: `can_withdraw(100, 40)` вернул False) — корректностный дефект воспроизведён.
- `python -m pytest -q` без `PYTHONPATH` — падение на коллекции (см. pre-existing).
- Линт и тайпчек не запускались: конфигурации в проекте нет; граничные случаи (`amount == balance`, `amount <= 0`) тестами не покрыты.
```

Блокирующий дефект не исправлял: правка затрагивает уже staged-индекс (изменение уйдёт в коммит), а такие вещи по правилам ревью сообщаются, а не правятся молча — исправление сводится к возврату `amount <= balance` в src/account.py:6.