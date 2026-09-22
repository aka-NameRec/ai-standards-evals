Ревью провёл по текущему (staged) диффу. Файл `.ai-standards/code-review-report.md` в проекте отсутствует — проект не запускал `ai-sync sync-templates`, поэтому использую резервный формат из правил. Отчёт размещаю в чате (файл не создавал).

```markdown
# Код-ревью
ai-standards v2.5.0

## Что сделано
Добавлен (staged, ещё не закоммичен) файл `api_handler.py` с функцией `adjust_stock(sku, qty)`, которая сохраняет `{"sku", "qty"}` напрямую через `InventoryRepository`.

## Как сделано
Стиль и конвенции соблюдены: докстринг модуля, тайп-хинты на публичной функции, именование в духе остального кода. Однако для записи не переиспользован существующий сервисный слой — см. находку ниже.

## Корректность
Не найдено.

## Архитектура и конвенции
- 🔴 api_handler.py:7 — API-обработчик пишет в инвентарь напрямую через `InventoryRepository`, минуя единый путь записи `InventoryReservationService` (существует в `inventory_service.py` и принимает репозиторий в конструкторе) — нарушает: ADR-004 (docs/decisions/ADR-004.md:3–4: «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited»), а также докстринг `InventoryRepository` (inventory_repository.py:5: «not for API handlers»). Исправление: в `adjust_stock` создавать `InventoryReservationService(InventoryRepository())` и вызывать `service.save({"sku": sku, "qty": qty})`, импортировав сервис из `inventory_service`.

## Переиспользование
Не найдено (помимо корня находки выше — обход существующего сервиса).

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
Код проверен чтением: `api_handler.py`, `inventory_repository.py`, `inventory_service.py`, `docs/decisions/ADR-004.md`. Автоматические проверки не запускались: в репозитории нет тестов (`conftest.py` пуст, тестовых файлов нет) и не настроены линтер/тайпчекер.
```

Итог: одна блокирующая находка 🔴 — прямая запись в репозиторий из API-обработчика нарушает ADR-004; исправление локальное и сформулировано в находке.