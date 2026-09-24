Тест должен отловить дефект — проверяю.
## Код-ревью — eval-fixture (cr-004-real-correctness-defect)

ai-standards v2.6.0

Отчёт размещён в чате (файл не создавался — шаблон `.ai-standards/code-review-report.md` в проекте отсутствует, использован резервный формат из правила Code Review).

```markdown
# Код-ревью — eval-fixture

ai-standards v2.6.0

## Что сделано

В `src/account.py` в функции `can_withdraw` оператор сравнения изменён с
`amount <= balance` на `amount >= balance`.

## Как сделано

Изменение минимальное (одна строка), docstring сохранён; переиспользовать или
упростить здесь нечего — функция самодостаточна.

## Корректность

- 🔴 src/account.py:6 — условие инвертировано: `can_withdraw(100, 40)` теперь
  возвращает `False` (обычное снятие 40 из 100 запрещено), а
  `can_withdraw(100, 500)` — `True` (разрешён овердрафт 500 при балансе 100).
  Контракт задан docstring на src/account.py:5 («Return whether ``amount`` may
  be withdrawn from ``balance``») — должно быть `amount <= balance`.
  Нарушает: Корректность — соответствие документированному контракту функции.

## Архитектура и конвенции

- 🟡 conftest.py:1 — (существовало ранее) пустой `conftest.py` и отсутствие
  pytest-конфигурации (`pythonpath`/`rootdir`): `pytest -q` без `PYTHONPATH=src`
  падает на сборке с `ModuleNotFoundError: No module named 'account'`, и юнит-тест
  не выполняется вовсе. Нарушает: Проверки — тесты должны запускаться штатным
  способом без ручной настройки окружения.

## Переиспользование

Не найдено.

## Эффективность

Не найдено.

## Качество

Не найдено.

## Проверки

- `PYTHONPATH=src rtk pytest -q` → 1 failed
  (`tests/test_account.py::test_routine_withdrawal`, `assert False is True`) —
  существующий тест подтверждает корректностный дефект 🔴.
- Голый `pytest -q` → ошибка сбора (`ModuleNotFoundError: No module named
  'account'`) — см. находку 🟡; сборку и запуск в CI не проверял (конфигурации CI
  в репозитории нет).
```

Находка 🔴 — сам смысл ревьюируемого изменения, поэтому возвращать оператор самовольно не стал: помечено как блокирующее, исправление — за автором (`amount <= balance`).