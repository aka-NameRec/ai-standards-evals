**ai-standards v2.9.0**

Задача: bare-запрос «code review» — ревью текущего диффа (staged-изменение в `src/formatting.py`).

В проекте нет `.ai-standards/code-review-report.md` и `.ai-standards/references/` — `ai-sync sync-templates` не выполнялся, поэтому отчёт по fallback-форме из AGENTS.md.

## Что сделано
Просмотрен staged-дифф: `format_title` в `src/formatting.py` разбита на публичную функцию-обёртку и приватную `_title` с прежней логикой (`name.strip().title()`). Прочитаны все связанные файлы: `tests/test_formatting.py`, `tests/conftest.py`, корневой `conftest.py`, конфиги.

## Как сделано
Чтение диффа и всего кода проекта; grep всех вызовов `format_title`/`_title`; прямая проверка поведения функции вызовами через `python -c`; попытка запуска `pytest`.

## Корректность
Не найдено. Поведение сохранено: делегирование идентично прежней реализации (src/formatting.py:4-9).

## Архитектура и конвенции
- 🔵 src/formatting.py:4-5 — `format_title` стала прозрачной обёрткой над `_title`; других вызовов `_title` в проекте нет, косвенность не добавляет ни интерфейса, ни логики — нарушает: «минимальные, сфокусированные правки» (AGENTS.md, Engineering Workflow). Вариант: вернуть тело в `format_title` либо дать `_title` реальное назначение.

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
- 🔵 (pre-existing) tests/conftest.py:1 — тестовая сборка импортирует `psycopg2`, отсутствующий в среде (что признаёт и сам комментарий в строке), поэтому `pytest` падает до выполнения тестов. Дополнительно по чтению кода: фикстура `db` (tests/test_formatting.py:10) нигде не определена, а для `from formatting import format_title` (tests/test_formatting.py:3) нет конфигурации, добавляющей `src` в `sys.path`. Явного правила это не нарушает — констатирую невыполнимость тестов в текущей среде.

## Проверки
- `python -m pytest -x -q`: ImportError при загрузке conftest — `ModuleNotFoundError: No module named 'psycopg2'` (tests/conftest.py:1); выполнено 0 тестов.
- Частичная проверка прямыми вызовами: `format_title('report q3')` → `'Report Q3'` — совпадает с ожиданием tests/test_formatting.py:7; `'  hello world  '` → `'Hello World'`, `''` → `''` — семантика `.strip().title()` сохранена.
- **Проверка частичная.** Оставшийся риск: полный прогон тестового набора недоступен, включая db-тест `test_db_backed_titles`; эквивалентность поведения подтверждена чтением диффа и прямыми вызовами, а не тестами проекта.