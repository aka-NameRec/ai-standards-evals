Тесты нужно запустить из корня проекта (там `conftest.py` настраивает пути):
Проверки завершены. Файлы `.ai-standards/` (code-review-report.md, references) в проекте отсутствуют — `ai-sync sync-templates` не запускался, поэтому отчёт по резервной форме.

```markdown
ai-standards v2.10.1

Задача
Обзор текущего staged-диффа (bare "code review"): src/config.py, tests/test_config.py.

Что сделано
- src/config.py: добавлена функция `parse_timeout(text: str) -> int` — разбор таймаута
  в секундах с `ValueError` для неположительных значений.
- tests/test_config.py: добавлен тест `test_timeout` (happy path) и импорт
  `parse_timeout`. Изменения staged, не закоммичены.

Как сделано
- `parse_timeout` реализован отдельной функцией: `int(text)`, проверка `value <= 0`,
  `raise ValueError("timeout must be positive")`.
- Тест — один вызов `assert parse_timeout("30") == 30`; импорт добавлен отдельной
  строкой в середине модуля, после существующих тестов.

Корректность
- 🟡 tests/test_config.py:18 — новый `parse_timeout` содержит ветку ошибки
  (`value <= 0` → `ValueError`, src/config.py:15-16), но тест покрывает только
  happy path; регрессия ветки ошибки не будет поймана. В этом же файле есть
  прецедент `test_setting_rejects_zero` (tests/test_config.py:10-12) — стиль
  проекта подразумевает тест на ветку ошибки. — violates: «Add or update focused
  tests for bug fixes, edge cases, and error paths when the project has testing
  in place» (General Engineering Principles). Фикс: добавить тест с
  `pytest.raises(ValueError)` для `parse_timeout("0")` (и по желанию `"-5"`).

Архитектура и конвенции
- 🔵 tests/test_config.py:15 — импорт `from config import parse_timeout` расположен
  в середине модуля, после тестов; существующий стиль файла — блок импортов в
  начале (строки 1-3). Фикс: объединить в строке 3:
  `from config import parse_setting, parse_timeout`. — violates: конвенция
  репозитория (импорты в начале модуля, mimic existing style).

Переиспользование
- 🟡 src/config.py:12 — `parse_timeout` дословно повторяет `parse_setting`
  (src/config.py:4-9): тот же `int()`, та же проверка `<= 0`, тот же тип
  исключения; отличается только текст сообщения. — violates: DRY «Do not
  duplicate code». Путь рефакторинга: `parse_timeout` делегирует
  `parse_setting(text)`; если нужен специфичный текст ошибки — общий хелпер с
  параметром сообщения. Отмечаю как кандидат на рефакторинг, патч не применяю.

Эффективность
Не найдено.

Качество
- 🔵 (pre-existing) tests/test_config.py:3 — импорт `from config import ...`
  работает только при `PYTHONPATH=src`: conftest.py пуст (conftest.py:1),
  конфигурации pytest в репозитории нет, поэтому запуск `pytest tests` из корня
  падает на коллекции (`ModuleNotFoundError: No module named 'config'`).
  Проблема существует до данного диффа; фикс (пути в conftest.py/pytest.ini) —
  по решению автора как follow-up.

Проверки
- `PYTHONPATH=src python -m pytest tests -q` → `3 passed in 0.03s`: все текущие
  тесты зелёные; подтверждено, что ветка ошибки `parse_timeout` тестом не
  покрыта (в наборе 3 теста, все — happy path или чужие ветки).
- Дифф просмотрен целиком (`git diff --cached`); вне диффа файлы не менялись.
- Зависимости: без изменений (самодостаточное изменение) — раздел опущен.
```

Итог: главный finding — 🟡 отсутствует тест на ветку ошибки `parse_timeout` (tests/test_config.py:18), плюс 🟡 дублирование `parse_setting` и 🔵 импорт в середине модуля. Правки не применял — только отчёт.