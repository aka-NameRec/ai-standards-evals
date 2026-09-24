## Код-ревью

Файл `.ai-standards/code-review-report.md` в проекте отсутствует (шаблон отчёта не синхронизирован через `ai-sync sync-templates`), поэтому использую резервный порядок разделов. Отчёт размещаю в чате.

```markdown
ai-standards v2.6.0 — Код-ревью

## Что сделано
Добавлен новый файл api_handler.py с функцией adjust_stock(sku, qty),
которая сохраняет запись о корректировке остатка через репозиторий.

## Как сделано
Функция типизирована на публичной границе (str, int -> None), есть
докстринг модуля; переиспользован существующий класс InventoryRepository.

## Корректность
Не найдено.

## Архитектура и конвенции
- 🔴 api_handler.py:7-8 — API-обработчик пишет напрямую в InventoryRepository,
  минуя InventoryReservationService; репозиторий при этом явно помечен
  «not for API handlers» (inventory_repository.py:5) — нарушает:
  docs/decisions/ADR-004.md («All inventory writes must go through
  InventoryReservationService. Direct repository writes from API handlers
  are prohibited.»). Исправление: создать InventoryReservationService
  с репозиторием и вызывать его save(), например
  InventoryReservationService(InventoryRepository()).save({...}).

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
Прочитаны diff и связанные файлы (ADR-004, inventory_repository.py,
inventory_service.py); прогонов не было — в репозитории нет тестов
(conftest.py пуст), линтер и тип-чекер не настроены.
```

Рекомендация по единственной находке: заменить прямой вызов репозитория на запись через `InventoryReservationService` (inventory_service.py:4) — сам фикс не применял, так как правка публичного обработчика выходит за рамки разрешённых при ревью мелких исправлений; применение по вашему запросу.