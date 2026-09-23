The report shape file `.ai-standards/code-review-report.md` is absent — the project hasn't run `ai-sync sync-templates`. Falling back to the default section order. The changes are staged; let me read the staged diff and the full files.
Pytest didn't collect anything; retrying with an explicit path.
```
ai-standards v2.6.0

## Код-ревью

### Что сделано
В `stats.mean()` переименована локальная переменная цикла `data` → `payload`; в `tests/test_stats.py` добавлен тест `test_mean_single_value` для случая из одного элемента.

### Как сделано
Правка минимальная и сводится к двум правкам в двух файлах; новый тест повторяет стиль существующего `test_mean`, реализация `mean()` не менялась, новых зависимостей нет.

### Корректность
Не найдено.

### Архитектура и конвенции
Не найдено.

### Переиспользование
Не найдено.

### Эффективность
Не найдено.

### Качество
Не найдено.

### Проверки
`pytest tests/test_stats.py -v` — 2 passed (`test_mean`, `test_mean_single_value`). Линтер не запускался — в проекте нет его конфигурации. Поведение `mean([])` (ZeroDivisionError) не проверялось и не менялось — существовало ранее и для хелпера допустимо.
```

Отчёт выведен в чат (в файл не сохранял — не просили). Примечание: `rtk pytest` дважды вернул «No tests collected», поэтому тесты запущены обычным `pytest` — результат выше подтверждён без rtk.