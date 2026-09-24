В проекте нет файлов `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` — проект не запускал `ai-sync sync-templates`, поэтому использую fallback-структуру отчёта. Изменения staged — смотрю `git diff --cached` и читаю код целиком.
**ai-standards v2.6.0**

## Что сделано

Просмотрен staged-диф (новый файл `api_handler.py`, 8 строк). Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют — проект не запускал `ai-sync sync-templates`, поэтому отчёт написан по fallback-структуре.

## Как сделано

Диф проверен по коду, а не по диффу: открыты `docs/decisions/ADR-004.md`, `inventory_service.py`, `inventory_repository.py`, `conftest.py`. Нарушение контракта подтверждено чтением обеих сторон (ADR и кода сервиса/репозитория).

## Корректность

Не найдено.

## Архитектура и конвенции

🔴 api_handler.py:7 — API-обработчик `adjust_stock` создаёт `InventoryRepository()` и пишет напрямую, минуя `InventoryReservationService`, при том что сервис уже существует как единственный путь записи (inventory_service.py:4) — violates: docs/decisions/ADR-004.md:3 («All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited.»)

  Исправление: в обработчике использовать `service = InventoryReservationService(InventoryRepository())` и вызывать `service.save(...)`. Не применено — правка пути записи не входит в перечень безопасных исправлений во время ревью, внесение правок оставлено за автором.

## Переиспользование

Не найдено.

## Эффективность

Не найдено.

## Качество

Не найдено.

## Проверки

Проверка выполнена чтением кода и ADR; тестов в проекте нет (`conftest.py` пуст, тестовых файлов нет), запуск проверок невозможен. Отчёт сделан только по staged-дифу, окружающий код не расширялся.