`ai-standards v2.8.1`

Обзор: в индексе один новый файл — `api_handler.py`. Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (`ai-sync sync-templates` не запускался), поэтому использую резервный формат отчёта.

## Что сделано

Добавлен обработчик `adjust_stock(sku, qty)` в `api_handler.py`, который создаёт `InventoryRepository` и напрямую сохраняет элемент через `repository.save({...})`.

## Как сделано

Импорт `InventoryRepository` из `inventory_repository.py`, прямая инстанциация репозитория внутри функции-обработчика, запись необработанного словаря.

## Корректность

Не найдено. Функционально код выполняет запись (делегирование в репозиторий) без видимых ошибок выполнения.

## Архитектура и конвенции

- 🔴 `api_handler.py:7` — обработчик API создаёт `InventoryRepository` и напрямую пишет в хранилище (`api_handler.py:8`), минуя сервисный слой — violates: ADR-004 (`docs/decisions/ADR-004.md:3-4`): «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited». Подтверждено чтением кода: `InventoryReservationService` уже существует (`inventory_service.py:4`) и объявлен как единственный путь записи; docstring репозитория (`inventory_repository.py:5`) также прямо запрещает его использование из обработчиков. Исправление: проводить запись через `InventoryReservationService(InventoryRepository()).save(...)`.
- 🔵 `api_handler.py:8` — между модулями передаётся нетипизированный словарь `{"sku": ..., "qty": ...}` — violates: правило Python-стека «Keep structured data explicit across module boundaries; do not pass loose dictionaries when the shape is stable and meaningful». Замечание: та же сигнатура `item: dict` уже используется в `inventory_service.py:10` и `inventory_repository.py:7`, так что исправление затронет все три слоя — только как follow-up, не в рамках этого diff.

## Переиспользование

Не найдено. (Обход существующего `InventoryReservationService` учтён в блокирующем замечании выше, здесь не дублируется.)

## Эффективность

Не найдено.

## Качество

Не найдено.

## Проверки

Проверка выполнялась чтением кода, а не только diff: прочитаны `api_handler.py`, `inventory_service.py`, `inventory_repository.py`, `docs/decisions/ADR-004.md`; подтверждено существование и контракт `InventoryReservationService`. Автоматические проверки не запускались — тестовой инфраструктуры в проекте нет (`conftest.py` пуст, тесты отсутствуют). Код не изменялся: правка затрагивает выбор связывания (где создавать сервис/репозиторий) и оставлена на решение автора.