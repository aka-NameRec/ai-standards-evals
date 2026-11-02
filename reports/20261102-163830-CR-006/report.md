`ai-standards v2.8.2`

Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (проект не запускал `ai-sync sync-templates`), поэтому использую резервную форму отчёта.

## Что сделано

В индекс добавлен новый файл `api_handler.py` (8 строк): функция `adjust_stock(sku, qty)` для корректировки остатков на складе.

## Как сделано

Функция создаёт `InventoryRepository()` напрямую и вызывает `repository.save({"sku": sku, "qty": qty})`.

## Корректность

Не найдено. Синтаксис проверен (`py_compile` — OK); логика записи соответствует сигнатуре репозитория.

## Архитектура и конвенции

- 🔴 `api_handler.py:7-8` — API-обработчик выполняет запись напрямую в `InventoryRepository`, минуя сервисный слой — violates: `docs/decisions/ADR-004.md`: «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited» (см. также docstring самого репозитория — inventory_repository.py:5 «not for API handlers»). Запись должна идти через `InventoryReservationService` (inventory_service.py:4). Конкретный способ внедрения (создавать сервис внутри функции, принимать его параметром или держать модульный синглтон) — решение автора; фиксирую, не правлю, поскольку изменение затрагивает связывание слоёв и публичный контракт модуля.
- 🔵 `api_handler.py:8` — элемент склада передаётся как неструктурированный словарь — violates: правило Python-стека «Keep structured data explicit across module boundaries; do not pass loose dictionaries when the shape is stable and meaningful». Форма `{"sku", "qty"}` стабильна и осмысленна; уместнее типизированная модель (`@dataclass`). Отмечаю как необязательное: текущий интерфейс `InventoryReservationService.save(item: dict)` (inventory_service.py:10) сам принимает словарь, поэтому полноценное исправление требует правки и сервисного слоя — вне рамок текущего diff.

## Переиспользование

Не найдено отдельного дублирования: дубликатом является сам факт обхода готового пути записи `InventoryReservationService`, что уже отражено находкой выше.

## Эффективность

Не найдено.

## Качество

Не найдено. Стиль (docstring, типизация публичной границы) соответствует существующим файлам проекта.

## Проверки

- `git diff HEAD` просмотрен полностью (единственный staged-файл `api_handler.py`).
- `python3 -m py_compile api_handler.py inventory_service.py inventory_repository.py` — OK.
- ADR-004, `inventory_service.py`, `inventory_repository.py` открыты и сверены с diff; claim о нарушении проверен по тексту ADR, а не только по названиям файлов.

## Зависимости

Новые зависимости не добавляются; `api_handler.py` импортирует только локальный `inventory_repository`.