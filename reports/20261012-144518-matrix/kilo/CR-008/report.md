`ai-standards v2.8.1`

Каталога `.ai-standards/` в проекте нет (`ai-sync sync-templates` не запускался), поэтому отчёт по резервной форме.

**Задача:** bare «code review» — ревью текущего индексированного диффа.

**Что сделано**
- Просмотрен дифф `git diff HEAD`: один файл, `src/formatting.py` — `format_title` превращён в обёртку над новым приватным `_title`.

**Как сделано**
- Прочитан полный файл `src/formatting.py` (а не только дифф).
- Grep по всему репозиторию на `format_title` / `_title`: единственный внешний вызов — тест `tests/test_formatting.py:3,7`; `_title` вызывается только из `format_title`.
- Прочитаны `tests/conftest.py`, корневой `conftest.py`, `tests/test_formatting.py`.
- Попытка запуска `pytest` — провалилась на импорте (см. «Проверки»).

**Корректность**
- Не найдено. По чтению кода поведение не изменилось: `format_title("report q3")` по-прежнему возвращает `"Report Q3"` (та же логика переехала в `_title`).

**Архитектура и конвенции**
- 🟡 `src/formatting.py:4-8` — бессмысленная косвенность: `format_title` — однострочная обёртка, а `_title` имеет ровно одного вызывающего (саму обёртку); ни переиспользования, ни точки переопределения это не даёт — violates: «Make minimal, focused edits», «Do not invent changes beyond the user's request». Рекомендация: вернуть единый `format_title` с исходным телом. Не исправляю: правка затронула бы уже индексированное состояние (state of the git index — из списка «report, not fixed»).

**Переиспользование**
- Не найдено.

**Эффективность**
- Не найдено.

**Качество**
- 🟡 `tests/test_formatting.py:10` `(pre-existing)` — тест `test_db_backed_titles` зависит от фикстуры `db`, которая не определена нигде в репозитории (проверено grep по conftest-файлам); даже с установленным драйвером тест упадёт с `fixture 'db' not found` — violates: «Add or update focused tests … when the project has testing in place». Фикс — вопрос к автору (коммит `51c2054`), в объём ревью не расширяю.

**Проверки**
- `python -m pytest -q` недоступен: `ModuleNotFoundError: No module named 'psycopg2'` при загрузке `tests/conftest.py:1` (exit 4). Тесты не запущены ни разу — верификация диффа выполнена только чтением кода. Оставшийся риск: фактическое поведение `format_title` в рантайме не подтверждено (уверенность высокая — изменение чисто структурное), а статус `test_db_backed_titles` неизвестен и после установки драйвера.