The report shape file is missing — I will use the fallback structure. I'm looking at the staged changes.
The change is verified against the code, not just the diff. I'll check the project structure for contracts and run the tests.
The tests didn't collect — I'll check why.
The result from `rtk pytest` looks suspicious (tests exist but weren't collected). I'm running it without rtk — the fallback rule applies.
Проверки завершены. Все находки проверены по коду — отчёт ниже.

Примечания:
- Файл `.ai-standards/code-review-report.md` отсутствует — проект не запускал `ai-sync sync-templates`, поэтому отчёт собран по fallback-структуре.
- `rtk pytest` ошибочно сообщил «No tests collected»; запущено без rtk, результат корректный.
- Назначение отчёта: чат (fenced code block).

```
ai-standards v2.5.0

## Код-ревью

Что сделано: в stats.py переименована переменная цикла mean (data → payload), поведение не менялось; в тесты добавлен test_mean_single_value с проверкой среднего для одного значения.

Как сделано: изменение самодокументируемое — косметическое переименование и один новый тест в существующем стиле файла; конвенции проекта соблюдены, нарушений переиспользования и дублирования нет.

Корректность
- Не найдено.

Архитектура и конвенции
- Не найдено.

Переиспользование
- Не найдено.

Эффективность
- Не найдено.

Качество
- Не найдено.

Проверки
- pytest -q — 2 passed (обе функции тестов, включая новый тест). Линт и типизация не запускались — команды в репозитории не настроены.
- Замечание: rtk pytest выдал «No tests collected», что противоречит факту; результат подтверждён прямым запуском pytest.
```