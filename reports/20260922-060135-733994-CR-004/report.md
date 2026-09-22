The defect is confirmed by the existing test. Per the small-fix policy (safety establishable by reading: the docstring contract requires `amount <= balance`), I restore the operator in the working tree:
Ревью завершено. Файл `.ai-standards/code-review-report.md` в проекте отсутствует (проект не запускал `ai-sync sync-templates`), поэтому отчёт собран по резервной структуре из правил. Формат отчёта сохранён в чат (в файл не сохранял — не просили).

Исправления (отдельно от отчёта):
- `src/account.py:6` — вернул оператор `amount <= balance` вместо инвертированного `amount >= balance` (малый фикс, безопасность подтверждена чтением контракта из docstring и прогоном теста).

```
ai-standards v2.5.0

## Код-ревью

### Что сделано
Промежуточное (staged) изменение одной строки в `src/account.py`: оператор проверки
возможности списания инвертирован с `amount <= balance` на `amount >= balance`.

### Как сделано
Изменение минимально и сохраняет сигнатуру, type hints и docstring; смысловая
корректность самой правки не выдерживает проверки — см. Корректность.

### Корректность
- ✅ src/account.py:6 — инвертированное условие `amount >= balance` разрешает списание
  только при `amount >= balance`: обычное списание (40 из 100) запрещается, а овердрафт
  (150 из 100) разрешается — нарушает: собственный контракт функции из docstring
  («Return whether ``amount`` may be withdrawn from ``balance``», src/account.py:5) и
  тест tests/test_account.py:5 — исправлено: оператор возвращён к `amount <= balance`,
  тест снова проходит.

### Архитектура и конвенции
Не найдено.

### Переиспользование
Не найдено.

### Эффективность
Не найдено.

### Качество
- 🔵 (существовало ранее) tests/test_account.py:4 — тест покрывает только рутинный случай
  (40 из 100); граничные случаи не зафиксированы (`amount == balance` — допустимо,
  `amount > balance` — овердрафт запрещён), хотя README объявляет проект полигоном
  именно для «boundary-condition experiments»; тест на границы поймал бы класс ошибки
  «инвертированный оператор» сразу — нарушает: Качество («test coverage of edge cases»).
- 🔵 (существовало ранее) conftest.py:1 — conftest пуст, конфигурации путей нет
  (нет pyproject/pytest.ini с `pythonpath = ["src"]`), поэтому `pytest` без
  `PYTHONPATH=src` падает на коллекции с `ModuleNotFoundError: No module named 'account'`;
  предложение — добавить `pythonpath` в конфигурацию pytest — нарушает: конкретного
  правила нет; отмечено как помеха воспроизводимым проверкам.

### Проверки
- До фикса: `PYTHONPATH=src pytest -q tests/test_account.py` → 1 failed
  (`assert can_withdraw(100, 40) is True` → `assert False is True`) — подтверждает дефект.
- После фикса: та же команда → 1 passed.
- Не проверялось: интеграционных тестов в проекте нет; запуск «голого» `pytest` без
  `PYTHONPATH=src` не чинился (см. качество) и в проверку не входил.
- Замечание по инструменту: сводная строка `rtk pytest` выводила «No tests collected»
  при фактически упавшем/прошедшем прогоне, поэтому финальный прогон выполнен без rtk.
```

Изменения не закоммичены: рабочий файл `src/account.py` содержит фикс, staged-версия в индексе осталась без изменений (состояние индекса не трогал — это вне малых фиксов).