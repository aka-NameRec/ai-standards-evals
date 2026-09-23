Проверил: ревьюю текущий diff (изменения в стейджинге — новый файл `api_handler.py`). Файл `.ai-standards/code-review-report.md` в проекте отсутствует — шаблон отчёта не синхронизирован (`ai-sync sync-templates` не запускался), поэтому использую резервный формат из правил.

```markdown
# Код-ревью
ai-standards v2.5.0

## Что сделано
Добавлен модуль `api_handler.py` с функцией `adjust_stock(sku, qty)`, которая создаёт `InventoryRepository` и сохраняет товар напрямую в хранилище.

## Как сделано
Функция типизирована, стиль соответствует соседним модулям; но для записи выбран репозиторий вместо существующего сервиса-обёртки `InventoryReservationService` (inventory_service.py:4-11).

## Корректность
Не найдено.

## Архитектура и конвенции
🔴 api_handler.py:7-8 — Обработчик API инстанцирует `InventoryRepository` и пишет в хранилище напрямую — нарушает: ADR-004 (docs/decisions/ADR-004.md:3-4): «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited» — это же подтверждает докстринг репозитория (inventory_repository.py:5, «not for API handlers»). Исправление: собирать `InventoryReservationService(InventoryRepository())` и вызывать его `save()` — сервис уже является единственным путём записи.

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
Тестов в репозитории нет (conftest.py пуст, файлов с тестами не обнаружено), запускать нечего. Проверка выполнена чтением кода: diff, docs/decisions/ADR-004.md, inventory_repository.py, inventory_service.py. Исправление нарушения не применялось — это правка архитектурной обвязки, требует решения автора.
```

Отчёт размещён в чате (файл не создавался). Найдена одна блокирующая проблема: обработчик обходит `InventoryReservationService` и нарушает ADR-004; править её без вашего решения не стал.