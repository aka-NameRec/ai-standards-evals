Проверка завершена. Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют — шаблоны не развёрнуты (`ai-sync sync-templates` не выполнялся), поэтому отчёт по fallback-форме из инструкций.

```markdown
ai-standards v2.10.1

Task: не указан явно — выполнено ревью текущего diff (staged-изменение в src/formatting.py).

Что сделано
- Ревью staged-изменения `src/formatting.py` (единственный файл в diff): `format_title` разбит на публичную обёртку и приватную `_title` с исходным телом `name.strip().title()`.
- Проверка контекста: tests/test_formatting.py, tests/conftest.py, корневой conftest.py; попытка запуска тестов.

Как сделано
- Прочитан весь diff (`git diff HEAD`) и все Python-файлы проекта (4 файла).
- Запуск `python -m pytest -q` — не выполнен, см. «Проверки».
- Ручная проверка поведения `format_title` интерпретатором без pytest.

Корректность
- Не найдено. Поведение `format_title` сохранено (`"report q3"` → `"Report Q3"`, strip сохранён) — подтверждено ручной проверкой.

Архитектура и конвенции
- Не найдено. Типизация публичной границы (`name: str -> str`) сохранена.

Переиспользование
- Не найдено.

Эффективность
- Не найдено.

Качество
- 🟡 tests/conftest.py:1 — безусловный `import psycopg2` на этапе импорта conftest делает весь тестовый набор неп запускаемым в средах без драйвера (pre-existing, присутствует уже в HEAD, коммит c252e4c) — нарушений явных правил из свода нет; следствие: блокируется вся тестовая верификация. Вариант: перенести импорт/скип в fixtures с `pytest.importorskip`.
- 🔵 src/formatting.py:8 — `_title` — приватная обёртка с единственным вызывающим (`format_title`) и без второго использования, полиморфизма или кэширования: ненужный уровень косвенности — явное правило из свода не нарушается, отмечено как наблюдение качества. Вариант: вернуть тело в `format_title` (безопасно по чтению).

Проверки
- `python -m pytest -q` — недоступен: `ModuleNotFoundError: No module named 'psycopg2'` при импорте tests/conftest.py:1 (pre-existing). Оставшийся риск: путь pytest (`test_title`, `test_db_backed_titles`, fixture `db`) не проверен.
- Выполнено частично: ручная проверка `format_title('report q3') == 'Report Q3'` и сохранения strip — пройдена.

Зависимости — раздел опущен: изменение самодостаточно (только stdlib).
```