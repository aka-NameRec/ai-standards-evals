Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (шаблоны не синхронизированы через `ai-sync sync-templates`), поэтому использую fallback-формат отчёта. Ревью выполнено по staged-диффу: новый файл `api_handler.py`.

ai-standards v2.6.0

**Task**
Ревью текущего staged-диффа (новый файл `api_handler.py`, +8 строк).

**Что сделано**
Прочитан дифф и код, на который он опирается: `api_handler.py`, `inventory_repository.py`, `inventory_service.py`, `docs/decisions/ADR-004.md`.

**Как сделано**
Проверка по проходам: Корректность → Архитектура и конвенции → Переиспользование → Эффективность → Качество. Каждая находка сверена с кодом, а не только с диффом.

**Корректность**
Не найдено.

**Архитектура и конвенции**
- 🔴 api_handler.py:7-8 — API-обработчик создаёт `InventoryRepository` напрямую и пишет в хранилище в обход сервиса — violates: ADR-004 «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited.» (docs/decisions/ADR-004.md:3-4; это же подтверждает докстринг `inventory_repository.py:5` — «not for API handlers»). Исправление: использовать `InventoryReservationService` из `inventory_service.py:10` (он уже принимает репозиторий в конструкторе и делегирует `save`), например `service = InventoryReservationService(InventoryRepository())` → `service.save({"sku": sku, "qty": qty})`, либо получить сервис через существующую точку сборки, если она появится в этом модуле.

**Переиспользование**
Корень той же находки: готовый единый путь записи `InventoryReservationService` (inventory_service.py:4-11) не переиспользован. Отдельной находки сверх 🔴 выше нет.

**Эффективность**
Не найдено.

**Качество**
Не найдено.

**Проверки**
Находка проверена чтением кода: ADR-004 читан, сервис и репозиторий открыты, путь записи подтверждён. Тесты не запускались — правки не вносились, запуск не требовался.

**Dependencies**
Нет зависимостей: находка самодостаточна и исправляется в пределах `api_handler.py`.

Правка не вносится: нарушение архитектурного решения — за автором остаётся выбор исправить или обосновать пересмотр ADR-004.