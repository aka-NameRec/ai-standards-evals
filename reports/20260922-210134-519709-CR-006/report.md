Файл `.ai-standards/code-review-report.md` в проекте отсутствует — отчёт собран по резервному формату из правил. Диф: один новый staged-файл `api_handler.py`. Назначение: чат.

```markdown
ai-standards v2.5.0

## Код-ревью

**Что сделано:** Добавлен `api_handler.py` с функцией `adjust_stock(sku, qty)`, которая сохраняет изменение инвентаря через `InventoryRepository.save()`.

**Как сделано:** Одна типизированная функция с докстрингом, в стиле существующих модулей; переиспользуется существующий `InventoryRepository`.

### Корректность
- Не найдено.

### Архитектура и конвенции
- 🔴 api_handler.py:7 — API-обработчик пишет в инвентарь напрямую через `InventoryRepository`, минуя сервис — нарушает: docs/decisions/ADR-004.md («All inventory writes must go through InventoryReservationService. Direct repository writes from API handlers are prohibited»); подтверждается docstring в inventory_repository.py:5 («not for API handlers») → оставлено как есть: провести запись через `InventoryReservationService` (inventory_service.py:4), например `InventoryReservationService(InventoryRepository()).save(...)` или получить готовый сервис из точки сборки.
- 🔵 api_handler.py:6 — `qty` принимается без проверки: отрицательные и нулевые значения беспрепятственно попадают в путь записи — нарушает: правило Python-стека «Parse and validate untrusted input at the application boundary before it reaches business logic» → оставлено как есть: добавить валидацию на границе (в обработчике либо в сервисе записи — размещение решить автору).

### Переиспользование
- Не найдено.

### Эффективность
- Не найдено.

### Качество
- Не найдено.

**Проверки:** Прочитаны диф (`git diff --cached`), `api_handler.py`, `inventory_repository.py`, `inventory_service.py`, `docs/decisions/ADR-004.md`, `ai/project-rules.md`. Код не запускался: тестов в репозитории нет (`conftest.py` пуст, файлов `test_*.py` не найдено), поэтому прогонять нечего.
```

Блокирующих проблем одна: находка 🔴 прямо запрещена ADR-004, исправление локальное и не требует изменений в других модулях.