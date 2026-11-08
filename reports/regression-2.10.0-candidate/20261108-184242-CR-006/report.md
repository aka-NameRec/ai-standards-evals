**ai-standards 2.9.0**

Примечание: файлов `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте нет — `ai-sync sync-templates` не запускался, поэтому отчёт по резервной форме.

## Задача
Известна из индекса: staged-коммит добавляет новый файл `api_handler.py` — обработчик API для корректировки стоков.

## Что сделано
Просмотрен staged-диф (`git diff HEAD`): один новый файл `api_handler.py` (8 строк). Проверен код, с которым он взаимодействует: `inventory_repository.py`, `inventory_service.py`, `docs/decisions/ADR-004.md`, `ai/project-rules.md`.

## Как сделано
Проходы: Корректность → Архитектура и конвенции → Переиспользование → Эффективность → Качество. Каждый вывод сверён с открытыми файлами.

## Корректность
Не найдено.

## Архитектура и конвенции
- 🔴 `api_handler.py:7-8` — API-обработчик создаёт `InventoryRepository` напрямую и пишет в хранилище (`repository.save(...)`), минуя единственный путь записи — нарушает: ADR-004 (`docs/decisions/ADR-004.md:3-4`): «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited.» Это подтверждается и докстрингом самого репозитория (`inventory_repository.py:5`: «Direct storage access; not for API handlers»). Конкретное исправление: использовать существующий `InventoryReservationService` из `inventory_service.py` (например, `service = InventoryReservationService(InventoryRepository())`, затем `service.save({"sku": sku, "qty": qty})`) — сигнатура `save` идентична, изменение локальное. Поскольку правка меняет архитектурный путь записи, не применяю её сам — решение за автором.

## Переиспользование
Покрыто находкой выше: готовый путь записи `InventoryReservationService` (`inventory_service.py:4-11`) не переиспользован.

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
Статический review: код синтаксически корректен, типизация присутствует. Выполнять нечего: в проекте нет тестов (`conftest.py` пуст), конфигурации линтера или тайп-чекера. Остаточный риск: поведенческая проверка невозможна, вывод основан только на чтении кода.

## Зависимости
Не найдено.