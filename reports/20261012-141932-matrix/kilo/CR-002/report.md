Diff read: rename of the loop variable in `stats.py` and a new test in `tests/test_stats.py`. The `.ai-standards/` files were not found — I am using the fallback format. Checking the tests:
`ai-standards v2.8.1`

Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют — `ai-sync sync-templates` не выполнялся, поэтому использую резервный формат отчёта.

**Задача**
Запрошен code review текущего диффа (изменения в индексе: `stats.py`, `tests/test_stats.py`).

**Что сделано**
(по диффу) В `stats.py` переименована переменная цикла `data` → `payload`; в `tests/test_stats.py` добавлен тест `test_mean_single_value` для `mean([7])`.

**Как сделано**
(по диффу) Переименование носит чисто косметический характер, логика не тронута. Новый тест следует стилю существующего `test_mean`. Проверено чтением итоговых файлов, а не только диффа: поведение `mean` не изменилось, `mean([7]) == 7` корректно (`7 / 1 == 7.0`, сравнение с `7` истинно).

**Корректность**
Не найдено.

**Архитектура и конвенции**
Не найдено.

**Переиспользование**
Не найдено.

**Эффективность**
Не найдено.

**Качество**
Не найдено.

**Проверки**
`python -m pytest tests/ -q` — 2 passed. Изменения в индексе соответствуют описанным выше.

**Зависимости**
Нет.