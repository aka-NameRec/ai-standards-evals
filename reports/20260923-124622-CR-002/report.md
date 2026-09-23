The report shape file `.ai-standards/code-review-report.md` is absent — the project has not run `ai-sync sync-templates`; falling back to the default order specified in the rules. Now I will get the staged diff.
rtk вернул «No tests collected» — похоже, он не передал путь; запускаю напрямую по каталогу тестов.
Проверки пройдены: оба теста зелёные. Изменение — переименование локальной переменной в `mean` и добавленный тест; отчёт по умолчанию публикую в чате.

````markdown
# Код-ревью

ai-standards v2.5.0

## Что сделано
В `stats.mean` переименована локальная переменная цикла `data` → `payload`; в `tests/test_stats.py` добавлен тест `test_mean_single_value` на список из одного элемента.

## Как сделано
Новый тест следует стилю существующего `test_mean`; логика `mean` не менялась. Нарушений конвенций и повтора кода в изменении нет.

## Корректность
Не найдено.

## Архитектура и конвенции
Не найдено.

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
- `pytest tests -v` — 2 passed (`test_mean`, `test_mean_single_value`). Примечание: `rtk pytest` без аргумента собрал 0 тестов (rootdir вышел за пределы фикстуры), проверка выполнена прямым запуском.
- Линт и типизация не запускались: в проекте не настроены соответствующие команды.
````