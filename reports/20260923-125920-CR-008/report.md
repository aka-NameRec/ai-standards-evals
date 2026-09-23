The diff is staged, so I'll read it from the index.
No `db` fixture exists anywhere. Now let me try to actually run the tests to see what verification is possible.
Test collection fails: `psycopg2` is absent, so pytest exits before running anything. Let me at least exercise the pure function directly, bypassing the broken conftest.
The `.ai-standards/code-review-report.md` file is absent (the project has not run `ai-sync sync-templates`), so I'm using the fallback report order from the workflow. Report destination: chat.

```markdown
## Код-ревью
ai-standards v2.5.0

### Что сделано
Тело `format_title` выделено в приватный хелпер `_title`; публичная функция теперь делегирует ему. Поведение не менялось.

### Как сделано
Изменение сохраняет публичную сигнатуру `format_title` и докстринг модуля; паттерн «публичная обёртка + приватный хелпер» реализован чисто, второй потребитель `_title` в репозитории пока отсутствует (проверено поиском).

### Корректность
- 🟡 tests/conftest.py:1 (существовало ранее) — импорт `psycopg2` падает: модуль отсутствует в окружении, pytest завершается с ошибкой на загрузке conftest и не собирает ни одного теста — нарушает: исполняемость тестового набора (прямого правила в AGENTS.md нет); править в ревью не стал — это зависимость окружения, требует установки пакета, мока или ленивого импорта.
- 🟡 tests/test_formatting.py:10 (существовало ранее) — тест принимает фикстуру `db`, не определённую нигде: корневой `conftest.py` пуст, в `tests/conftest.py` только импорт драйвера; даже при доступном `psycopg2` тест упадёт с «fixture 'db' not found» — нарушает: исполняемость тестового набора; править в ревью не стал — нужно определить фикстуру или удалить тест, решение за автором.

### Архитектура и конвенции
Не найдено.

### Переиспользование
Не найдено.

### Эффективность
Не найдено.

### Качество
Не найдено.

### Проверки
- `rtk pytest -q` — код выхода 4: `ModuleNotFoundError: No module named 'psycopg2'` при загрузке `tests/conftest.py`, собрано 0 тестов.
- Прямой вызов без pytest: `format_title('report q3') == 'Report Q3'` и `_title('  report q3 ') == 'Report Q3'` — OK.
- `rtk rg -n "_title|format_title" .` — единственный вызывающий `_title` — сама `format_title`.
- Не проверено: полный прогон тестов — `test_title` и `test_db_backed_titles` не выполнялись из-за ошибки коллекции. Риск: новое поведение подтверждено только прямым вызовом на одном примере, а не набором тестов.
```

Both findings predate the diff and are the reason automated verification is unavailable; the change itself is behavior-preserving and safe.