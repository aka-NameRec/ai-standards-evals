Проверил состояние: в `.ai-standards/` файлов нет (проект не запускал `ai-sync sync-templates`), поэтому использую резервный формат отчёта, описанный в правилах.

**ai-standards v2.8.2**

# Отчёт code review

**Задача:** не известна (ревью текущего staged-диффа).

## Что сделано
Просмотрен staged-дифф: один новый файл `api_handler.py` (8 строк). Прочитан контекст: `inventory_repository.py`, `inventory_service.py`, `docs/decisions/ADR-004.md`, `ai/project-rules.md`.

## Как сделано
П passes по порядку: Корректность → Архитектура и конвенции → Переиспользование → Эффективность → Качество. Каждый пункт проверен по коду и ADR, не только по диффу.

## Корректность
Не найдено. Функция выполняется без ошибок, поведение соответствует своему буквальному коду.

## Архитектура и конвенции
- 🔴 `api_handler.py:7-8` — API-обработчик создаёт `InventoryRepository` и пишет в хранилище напрямую, минуя сервис — violates: ADR-004 (docs/decisions/ADR-004.md:3-4 — «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited»). Оба класса (`InventoryRepository.save` в inventory_repository.py:5 и `InventoryReservationService` в inventory_service.py:5) прямо документируют это ограничение. Исправление: `adjust_stock` должен делегировать запись в `InventoryReservationService` (например, `InventoryReservationService(InventoryRepository()).save(...)`), не обращаясь к репозиторию как к точке записи. Изменение публичного контракта — сообщаю, не правлю.

## Переиспользование
Не найдено. Дублирования внутри диффа нет.

## Эффективность
Не найдено.

## Качество
- 🔵 `api_handler.py:8` — запись передаётся как неструктурированный словарь `{"sku": sku, "qty": qty}` при стабильной и осмысленной форме данных — violates: Python-правило «Keep structured data explicit across module boundaries; do not pass loose dictionaries when the shape is stable and meaningful». Предпочтительно `@dataclass`-модель или типизированный параметр (тот же словарь уходит и в `InventoryRepository.save(item: dict)` — inventory_repository.py:7). Опционально; шаг маршрутизации через сервис (см. 🔴) важнее.

## Проверки
- Тесты в проекте отсутствуют (`conftest.py` пуст), запускать нечего. Lint/typecheck-команды в репозитории не сконфигурированы — проверить нечем.
- Основной риск подтверждён чтением ADR и обоих классов; исправление 🔴 потребует прогона тестов после добавления — безопасность правки чтением alone не устанавливается, поэтому не применяю.

## Зависимости
Не найдено. Новых зависимостей дифф не добавляет.