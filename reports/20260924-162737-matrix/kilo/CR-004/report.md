The diff (staged) inverts the withdrawal check. I'll apply the safe one-token fix and verify with the existing test.
**ai-standards v2.6.0**

Примечание: файлов `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте нет (проект не запускал `ai-sync sync-templates`) — использую резервный формат отчёта.

## Что сделано
Проанализирован текущий staged-диф: `src/account.py`, функция `can_withdraw` — заменён оператор сравнения. Проверено поведение по коду (не только по дифу), прочитан тест `tests/test_account.py`, тесты запущены до и после правки.

## Как сделано
Отчёт без правок, кроме одного малого фикса: восстановлен исходный оператор `<=` (безопасность установлена чтением: докстринг и существующий тест однозначно фиксируют контракт; правка в один токен). Индекс не трогал.

## Корректность
- 🔴 `src/account.py:6` — инвертированное условие `amount >= balance`: обычное снятие `can_withdraw(100, 40)` возвращает `False`, а снятие суммы **больше** баланса (овердрат) возвращает `True`; противоречит докстрингу `Return whether "amount" may be withdrawn from "balance"` и ломает тест `test_routine_withdrawal` — violates: корректность (функция не соответствует собственному контракту; сохранение поведения).
  → fixed: восстановлено `return amount <= balance`; `PYTHONPATH=src python -m pytest tests/ -q` — 1 passed. Внимание: сломанная версия всё ещё лежит в индексе (staged), рабочее дерево опережает индекс — нужен `git add src/account.py` перед коммитом (индекс не менял — за пределами малого фикса).

## Архитектура и конвенции
Не найдено.

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
- 🔵 `conftest.py:1` (pre-existing) — файл пуст, а пакет `src` не объявлен (нет `pyproject.toml`/`pytest.ini`), поэтому `pytest` без `PYTHONPATH=src` падает на коллекции: `ModuleNotFoundError: No module named 'account'` — violates: не маппится на конкретное правило репозитория; предложил бы `pythonpath = ["src"]` в pytest-конфиге или заполнение `conftest.py`. Не правил — вне рамок дифа.

## Проверки
- `PYTHONPATH=src python -m pytest tests/ -q` до фикса: 1 failed (`can_withdraw(100, 40) is False`) — подтверждает корневую причину.
- Тот же прогон после фикса: 1 passed.
- `git diff` после фикса показывает возврат строки к виду HEAD (`972fdff`); lint/typecheck-команды в репозитории не настроены.