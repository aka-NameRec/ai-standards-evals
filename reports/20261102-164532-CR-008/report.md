Verification fails at collection. Let me confirm the failure chain and verify the diff's behavior directly.
ai-standards v2.8.2

Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют — `ai-sync sync-templates` не запускался; использую резервный формат из AGENTS.md.

**Задача**: bare «code review» — ревью текущего staged-диффа (`src/formatting.py`).

**Что сделано**
- `format_title` превращён в обёртку, делегирующую новой приватной функции `_title`, в которую перенесено исходное тело (`name.strip().title()`).

**Как сделано**
- Единственное изменение — разбиение одной функции на публичную и приватную; других вызовов `_title` в репозитории нет (проверено grep по `*.py`).

**Корректность**
- Поведение `format_title` сохранено; сам дифф багов не содержит.
- 🟡 tests/conftest.py:1 — (pre-existing) `import psycopg2` на импорте conftest роняет сбор всей suite: `python3 -m pytest tests` → `ModuleNotFoundError: No module named 'psycopg2'`, ни один тест не исполняется — violates: явного правила нет; блокер верификации, psycopg2 в репозитории нигде не объявлен.
- 🟡 tests/test_formatting.py:3 — (pre-existing) импорт `from formatting import format_title` неразрешим: модуль лежит в `src/`, и ничто не добавляет `src` в `sys.path` (проверено: при обходе psycopg2 коллекция падает с `ModuleNotFoundError: No module named 'formatting'`) — violates: явного правила нет; тесты не привязаны к фактической раскладке модулей.
- 🟡 tests/test_formatting.py:10 — (pre-existing) `test_db_backed_titles(db)` использует фикстуру `db`, не определённую нигде (корневой `conftest.py` пуст, `tests/conftest.py` фикстур не определяет); при работоспособной коллекции — ошибка `fixture 'db' not found` (проверено) — violates: явного правила нет; неисполняемый тест в suite.

**Архитектура и конвенции**
- Не найдено.

**Переиспользование**
- Не найдено.

**Эффективность**
- Не найдено.

**Качество**
- 🟡 src/formatting.py:4-8 — неоправданная косвенность: `_title` имеет единственного вызывающего, шва нет (нет вариантов, переопределений, кэширования); весь дифф сводится к бессодержательной прослойке — нарушает: явного правила в AGENTS.md нет, помечено как YAGNI/ unjustified indirection; стоит либо вернуть одну функцию, либо дать разбиению реальное основание.

**Проверки**
- `python3 -m pytest tests` — коллекция падает на `tests/conftest.py:1`; верификация через suite проекта недоступна.
- Частично: прямой импорт `src/formatting.py` — `format_title('report q3') == 'Report Q3'`, краевые пробелы обрезаются; при стабе psycopg2 (`/tmp/kilo/stub`) и `PYTHONPATH=src` — `test_title` PASSED, `test_db_backed_titles` ERROR (fixture `db` not found).
- Оставшийся риск: краевые случаи (`None`, не-строки, регистр unicode) suite'ом не проверяются — он в этом окружении не запускается; обходные пути (стаб, `PYTHONPATH`) — искусственные, конфигурацией проекта не закреплены.

**Зависимости**
- `psycopg2` — отсутствует в окружении и не объявлен в репозитории (requirements/pyproject в проекте нет); см. находку в «Корректность».