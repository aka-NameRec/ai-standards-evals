`.ai-standards/code-review-report.md` отсутствует (проект не запускал `ai-sync sync-templates`), поэтому использую резервный порядок разделов. Отчёт размещаю в чате.

````markdown
## Код-ревью

ai-standards v2.6.0

### Что сделано
Добавлен новый модуль `api_handler.py` с функцией `adjust_stock`, которая записывает позицию инвентаря в хранилище.

### Как сделано
Обработчик создаёт `InventoryRepository` напрямую и вызывает его `save()`; типы и докстринги оформлены в стиле существующих модулей.

### Корректность
Не найдено.

### Архитектура и конвенции
- 🔴 api_handler.py:8 — обработчик пишет в хранилище напрямую через `InventoryRepository().save(...)`, минуя единую точку записи `InventoryReservationService` (inventory_service.py:4) — нарушает: docs/decisions/ADR-004.md («All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited»; сам репозиторий в inventory_repository.py:5 тоже помечен «not for API handlers»). Исправление: в `adjust_stock` собирать `service = InventoryReservationService(InventoryRepository())` и вызывать `service.save({"sku": sku, "qty": qty})`.

### Переиспользование
Не найдено.

### Эффективность
Не найдено.

### Качество
Не найдено.

### Проверки
Прочитан застейдженный дифф (`git diff --cached`), а также ADR-004, `inventory_service.py` и `inventory_repository.py`. Тестов в проекте нет (conftest.py пуст, файлов тестов нет), поэтому тесты не запускались; поведение кода не исполнялось.
````