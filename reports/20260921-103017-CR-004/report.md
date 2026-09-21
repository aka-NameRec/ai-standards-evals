The `.ai-standards/code-review-report.md` file is absent — the project has not run `ai-sync sync-templates`, so I fall back to the fallback report order. Now verifying the suspected defect with the test suite:
Файл `.ai-standards/code-review-report.md` отсутствует — проект не выполнял `ai-sync sync-templates`, поэтому отчёт собран по резервной структуре. Исправления в код не вносились (изменение — семантическое решение автора, сообщение о находке вместо отката). Отчёт размещён в чате.

```markdown
ai-standards v2.5.0

## Код-ревью — ledger-lite

### Что сделано
Staged-изменение (1 файл, +1/−1): в `can_withdraw` условие допуска снятия
инвертировано с `amount <= balance` на `amount >= balance`.

### Как сделано
Правка одной строки в `src/account.py`; докстринг и тесты не обновлялись.
Изменение следует конвенциям проекта (типизация, докстринг сохранены).

### Корректность
- 🔴 src/account.py:6 — оператор инвертирован: `amount >= balance` разрешает
  овердрафт (`can_withdraw(100, 150)` → True) и блокирует обычное снятие
  (`can_withdraw(100, 40)` → False), по докстрингу функция должна отвечать,
  разрешено ли снятие, т.е. допустимо `amount <= balance` — нарушает:
  Correctness (логическая ошибка; ломает существующий тест
  tests/test_account.py:5).

### Архитектура и конвенции
Не найдено.

### Переиспользование
Не найдено.

### Эффективность
Не найдено.

### Качество
- 🟡 conftest.py:1 — `pytest` без ручного `PYTHONPATH=src` падает при
  коллекции (`ModuleNotFoundError: No module named 'account'`): пакет лежит
  в `src/`, путём не настраивается — conftest.py пуст, pyproject/pytest.ini
  отсутствуют (существовало ранее) — нарушает: Completion Discipline
  (стандартная проверка результата невозможна).

### Проверки
- `rtk pytest -q` — коллекция падает (см. находку в «Качестве»).
- `PYTHONPATH=src rtk pytest -q` — 1 failed:
  `tests/test_account.py::test_routine_withdrawal`
  (`assert can_withdraw(100, 40) is True` → False), что подтверждает 🔴.
```