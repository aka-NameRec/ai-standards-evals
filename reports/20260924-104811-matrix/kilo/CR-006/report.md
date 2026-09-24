**ai-standards v2.6.0**

Примечание: файлов `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте нет — `ai-sync sync-templates` не запускался, поэтому использую резервный формат отчёта.

## Задача
Ревью текущего диффа: новый файл `api_handler.py` (в индексе, не закоммичен).

## Что сделано
Проверка ограничена диффом (`api_handler.py`). Смежный код прочитан целиком, а не по диффу: `inventory_service.py`, `inventory_repository.py`, `docs/decisions/ADR-004.md`.

## Как сделано
Проходы по порядку: корректность → архитектура и конвенции → переиспользование → эффективность → качество.

## Корректность
Не найдено.

## Архитектура и конвенции
- 🔴 `api_handler.py:7-8` — обработчик создаёт `InventoryRepository()` и пишет напрямую (`repository.save(...)`), минуя `InventoryReservationService` — violates: ADR-004 (`docs/decisions/ADR-004.md:3-4`): «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited»; это же подтверждает docstring репозитория (`inventory_repository.py:5`: «not for API handlers»). Обходной путь ломает единственный путь записи, ради которого введён сервис (`inventory_service.py:5`). Исправление: инстанцировать `InventoryReservationService` и вызывать его `save`; решение о способе получения зависимостей (DI/конструирование на месте) — за автором, поэтому не исправляю сам.

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
Верификация чтением кода и ADR; тестового набора в репозитории нет (`conftest.py` пуст, тестов не обнаружено), прогонять нечего.

## Зависимости
Сторонних зависимостей дифф не добавляет.