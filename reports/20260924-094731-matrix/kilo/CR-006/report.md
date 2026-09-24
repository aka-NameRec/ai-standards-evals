Файлов `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте нет — шаблоны не синхронизированы (`ai-sync sync-templates` не запускался), поэтому отчёт собран по резервному формату из правил.

# Отчёт code review

ai-standards v2.6.0
Легенда: 🔴 — блокирующее, 🟡 — желательно исправить, 🔵 — опционально, ✅ — исправлено.

## Задача
Ревью текущего диффа: один новый файл `api_handler.py` (в индексе, 8 строк).

## Что сделано
Добавлен обработчик `adjust_stock(sku, qty)`, который создаёт `InventoryRepository` и сохраняет запись `{"sku": ..., "qty": ...}` напрямую.

## Как сделано
Прямое создание репозитория внутри функции-обработчика и вызов `repository.save(...)` без участия сервиса.

## Корректность
- 🔵 api_handler.py:6 — параметр `qty` принимается без какой-либо валидации (в т.ч. отрицательные значения) и уходит в слой хранения — нарушает: правило Python-фрагмента «Parse and validate untrusted input at the application boundary before it reaches business logic» (обработчик API — граничная точка входа).

## Архитектура и конвенции
- 🔴 api_handler.py:7-8 — API-обработчик пишет в `InventoryRepository` напрямую, минуя `InventoryReservationService` — нарушает: ADR-004 (docs/decisions/ADR-004.md:3-4: «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited.»). Проверено по коду: `inventory_service.py:4-11` содержит `InventoryReservationService.save` как единственный путь записи, а `inventory_repository.py:5` прямо помечает репозиторий как «not for API handlers». Исправление: собрать `InventoryReservationService(InventoryRepository())` в точке сборки приложения и в обработчике вызывать только сервис. Сам не исправляю: это изменение сборки/контрактов, а не мелкий фикс.

## Переиспользование
Не найдено. (Обход существующего пути записи учтён в находке 🔴 выше — отдельной проблемы дублирования нет.)

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
Прочитаны не только дифф, но и `ADR-004.md`, `inventory_service.py`, `inventory_repository.py` — вывод о нарушении подтверждён кодом, а не только текстом диффа. Тесты в репозитории отсутствуют (`conftest.py` пуст, файлов `test_*` нет), `repository.save` — заглушка (`...`), поэтому запускать нечего; поведение диффа подтверждено только чтением.

## Зависимости
Новых зависимостей нет; используется только локальный модуль `inventory_repository`.