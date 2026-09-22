Fixing the misplaced import first (plain inconsistency, safe by reading), then verifying with the test run.
`rtk` is failing here (exit 2, module not found even with `PYTHONPATH` set) — per the fallback rule I'll rerun without it and verify.
Отчёт вывожу в чат (файл не создавался). Одна попутная правка вне отчёта: импорт `parse_timeout` перенесён из середины `tests/test_config.py` в верхний блок импортов.

```
ai-standards v2.5.0

## Код-ревью — cr-009-missing-error-path-test

Файл `.ai-standards/code-review-report.md` в проекте отсутствует — видимо, `ai-sync sync-templates` не запускался, поэтому отчёт собран по резервной структуре из правил ревью.

### Что сделано
В `src/config.py` добавлена функция `parse_timeout`, парсящая таймаут в секундах и бросающая `ValueError` для неположительных значений. В `tests/test_config.py` добавлен тест счастливого пути `test_timeout`.

### Как сделано
Новая функция повторяет форму существующей `parse_setting`: тайп-хинты на публичной границе, docstring с контрактом, исключение вместо сентинела — это соответствует Python-правилам проекта.

### Корректность
Не найдено.

### Архитектура и конвенции
Не найдено. Module contracts (`docs/architecture/**`, `MODULE_CONTRACT.md`) в проекте отсутствуют.

### Переиспользование
🔵 src/config.py:12 — `parse_timeout` дублирует логику существующей `parse_setting` (int → проверка `<= 0` → `ValueError` → return); фактические отличия — только текст сообщения и имя параметра — нарушает: DRY («Do not duplicate code»). Путь рефакторинга: `return parse_setting(text)` (текст сообщения ничем не проверяется) либо общий хелпер с параметром сообщения. → оставлено как есть:

### Эффективность
Не найдено.

### Качество
🟡 tests/test_config.py:15 — для нового `parse_timeout` покрыт только счастливый путь: ошибка `ValueError` на неположительном входе (src/config.py:15-16) тестом не покрыта, хотя соседняя `parse_setting` имеет симметричный `test_setting_rejects_zero` — нарушает: General Engineering Principles («Add or update focused tests for bug fixes, edge cases, and error paths when the project has testing in place»). Добавление теста выходит за рамки безопасных попутных правок ревью, оставляю автору. → оставлено как есть:

✅ tests/test_config.py:3 — импорт `from config import parse_timeout` был помещён в середину файла (строка 15) после тестов, а не в верхний блок импортов — нарушает: согласованность с окружающим кодом (plain inconsistency) → исправлено: импорт объединён с верхним в `from config import parse_setting, parse_timeout`

### Проверки
- `PYTHONPATH=src pytest tests -q` — 3 passed (после правки импорта). Примечание: `rtk pytest` упал (exit 2 — `PYTHONPATH` не доходит до pytest через прокси), команда выполнена без `rtk`.
- Ошибочный путь подтверждён вручную: `parse_timeout("0")` даёт `ValueError: timeout must be positive` (python -c), но тестом он не покрыт — см. находку в «Качество».
- Не проверялось: линтеры и тайп-чекеры — в проекте нет их конфигурации.
```