В диагностированном дефекте подтверждена корневая причина: тест падает на текущей (staged) версии. Применяю допустимый малый фикс — возврат исходного сравнения — и проверяю.
`ai-standards v2.8.1`

Файл `.ai-standards/code-review-report.md` в проекте отсутствует (проект не запускал `ai-sync sync-templates`), поэтому отчёт — по fallback-форме из правил.

**Что сделано**
В ревью — текущий diff (staged): в `can_withdraw` сравнение `amount <= balance` заменено на `amount >= balance`.

**Как сделано**
Изменение инвертирует предикат права снятия средств; больше в diff ничего нет.

**Корректность**
- ✅ src/account.py:6 — инвертированное сравнение `amount >= balance` вместо `amount <= balance` ломает контракт функции (docstring: «Return whether ``amount`` may be withdrawn from ``balance``»): обычное снятие `can_withdraw(100, 40)` возвращало `False` — нарушает: контракт функции (docstring) и существующий тест tests/test_account.py:5 → fixed: вернул `amount <= balance` (минимальный патч, безопасность подтверждена чтением контракта и прогоном теста).
- 🟡 tests/test_account.py:1 (pre-existing) — без `PYTHONPATH=src` сборка тестов падает (`ModuleNotFoundError: No module named 'account'`): модуль лежит в `src/`, конфигурации pytest с `pythonpath` нет, корневой `conftest.py` пуст. Нарушаемого правила в AGENTS.md нет — фиксирую как инфраструктурный дефект, мешающий проверке; это не часть diff.

**Архитектура и конвенции**
Не найдено.

**Переиспользование**
Не найдено.

**Эффективность**
Не найдено.

**Качество**
Не найдено.

**Проверки**
`PYTHONPATH=src python -m pytest -q`: до фикса — 1 failed (`assert False is True` в test_routine_withdrawal), после фикса — 1 passed. Корневая причина подтверждена прогоном теста. Фикс внесён только в рабочее дерево: индекс по-прежнему содержит дефектную строку (`git status` показывает `MM` для src/account.py) — restage/commit остаётся за автором.