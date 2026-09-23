Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (проект не выполнял `ai-sync sync-templates`) — использую резервную форму отчёта.

---

**ai-standards v2.6.0**

## Задача
Code review текущего staged-диффа (новый файл `api_handler.py`, +8 строк).

## Что было сделано
- Просмотрен staged-дифф: новый модуль `api_handler.py` с функцией `adjust_stock`.
- Прочитаны смежные файлы целиком (не только дифф): `inventory_repository.py`, `inventory_service.py`, `docs/decisions/ADR-004.md`.
- Проверена история коммитов: ADR-004 и `InventoryReservationService` добавлены в коммите `3174c87`, то есть раньше рассматриваемого изменения.

## Как это было сделано
- Проходы по порядку: Correctness → Architecture & Conventions → Reuse → Efficiency → Quality; каждый вывод сверен с кодом файлов, а не только с диффом.

## Correctness
None found.

## Architecture & Conventions
- 🔴 `api_handler.py:8` — API-обработчик пишет напрямую в репозиторий (`repository.save(...)` через созданный на строке 7 `InventoryRepository()`), минуя единый путь записи — violates: ADR-004 «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited.» Исправление: в `adjust_stock` создавать `InventoryReservationService(InventoryRepository())` и вызывать `service.save({"sku": sku, "qty": qty})`; прямое обращение к `InventoryRepository` из обработчика убрать.
- 🟡 `api_handler.py:6` — входные параметры `sku`/`qty` не валидируются на границе приложения: отрицательный `qty` или пустой `sku` беспрепятственно доходят до записи (в репозитории `save` — заглушка, проверок нет нигде по цепочке) — violates: правило Python Stack «Parse and validate untrusted input at the application boundary before it reaches business logic». Минимальное исправление: проверить `qty > 0` и непустой `sku` в начале `adjust_stock` с понятным `ValueError`.

## Reuse
None found. (Дублирования нет; напротив — существующий `InventoryReservationService` не переиспользован, что уже отражено находкой 🔴 выше.)

## Efficiency
None found.

## Quality
None found.

## Verification
Проверено чтением кода: подтверждено, что `InventoryReservationService` существует (`inventory_service.py:4`) и принимает репозиторий в конструкторе; подтверждено коммит-логом, что ADR-004 старше диффа (нарушение внесено этим изменением, не pre-existing). Запускать нечего: в проекте нет тестов (`conftest.py` пуст), `InventoryRepository.save` — заглушка; исправления находок не применялись (репортинг по умолчанию).

## Dependencies
Исправления затрагивают только `api_handler.py` (импорт `inventory_service` уже существует в проекте); внешних зависимостей, миграций и изменений контрактов не требуется.