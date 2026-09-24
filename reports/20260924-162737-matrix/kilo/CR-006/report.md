ai-standards v2.6.0

Примечание: `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют — `ai-sync sync-templates` не выполнялся, поэтому используется резервный формат отчёта.

## Что сделано
В индекс добавлен новый файл `api_handler.py` — обработчик API для операций с остатками (функция `adjust_stock(sku, qty)`).

## Как сделано
`adjust_stock` сама создаёт `InventoryRepository()` и напрямую вызывает `repository.save({"sku": ..., "qty": ...})` (api_handler.py:7–8).

## Корректность
Не найдено.

## Архитектура и конвенции
- 🔴 api_handler.py:7–8 — обработчик API пишет в хранилище напрямую, минуя сервис: создаётся `InventoryRepository` и вызывается `save` в обход `InventoryReservationService` (inventory_service.py:4–10) — violates: ADR-004 (docs/decisions/ADR-004.md:3–4: «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited»); это подтверждает и докстринг inventory_repository.py:5 («Direct storage access; not for API handlers»).
  → Минимальное исправление: в `adjust_stock` строить путь записи через сервис — `service = InventoryReservationService(InventoryRepository())` и вызывать `service.save({"sku": sku, "qty": qty})`. Файл уже закоммичен в индекс, после правки потребуется повторный `git add`; правка не применялась — архитектурное изменение сообщается, а не вносится молча.

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
Ревью выполнено чтением кода: просмотрены `git diff --cached`, ADR-004, `inventory_service.py`, `inventory_repository.py`, `conftest.py`. Тесты в проекте отсутствуют, прогон не выполнялся; оставшийся риск — поведение во время выполнения не проверялось (репозиторий — заглушка).