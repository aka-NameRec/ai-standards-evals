ai-standards v2.8.1

Примечание: `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте не найдены (`ai-sync sync-templates` не выполнялся) — отчёт в резервном формате.

**Задача**: ревью текущего diff (в индексе — новый файл `api_handler.py`).

**Что сделано**: добавлена функция `adjust_stock` — обработчик API для корректировки остатков, записывающий данные в хранилище.

**Как сделано**: `api_handler.py` импортирует `InventoryRepository` и внутри `adjust_stock` создаёт репозиторий и вызывает `save()` напрямую.

**Корректность**
Не найдено.

**Архитектура и конвенции**
- 🔴 api_handler.py:7-8 — обработчик API выполняет прямую запись в репозиторий в обход `InventoryReservationService` — нарушает: ADR-004 (docs/decisions/ADR-004.md:3-4): «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited». Подтверждается докстрингом inventory_repository.py:5 («not for API handlers»). Исправление: в обработчике использовать `InventoryReservationService` (inventory_service.py:4), передав ему репозиторий, — сервис является единственным путём записи.

**Переиспользование**
Не найдено.

**Эффективность**
Не найдено.

**Качество**
Не найдено.

**Проверки**: проверено по коду, а не только по diff — открыты ADR-004, `inventory_service.py`, `inventory_repository.py`. Ничего не исправлялось (режим отчёта; изменение затрагивает компоновку модулей и требует решения автора). Тесты не запускались — изменений не вносилось; тестовая инфраструктура (`conftest.py`) пуста.

**Зависимости**: `api_handler.py` зависит от `inventory_repository`; предлагаемое исправление добавит зависимость от `inventory_service`.