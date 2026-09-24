Проверил: `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (шаблоны не синхронизированы через `ai-sync sync-templates`), поэтому отчёт — по fallback-форме из правил. Review идёт по staged-диффу (`api_handler.py`, новый файл), с чтением смежных модулей, а не только диффа.

ai-standards v2.6.0

## Задача
Неизвестна (запрос без контекста) — ревью staged-изменения: новый файл `api_handler.py`.

## Что сделано
Добавлен обработчик `adjust_stock(sku, qty)`, который создаёт `InventoryRepository` и сохраняет запись напрямую.

## Как сделано
Импорт `InventoryRepository` из `inventory_repository`, создание репозитория внутри функции, запись словаря `{"sku": ..., "qty": ...}` через `repository.save(...)`.

## Корректность
Не найдено. (Функция делает то, что заявляет; типы на границе проставлены.)

## Архитектура и конвенции
- 🔴 `api_handler.py:7-8` — API-обработчик пишет в хранилище напрямую через `InventoryRepository`, минуя сервисный слой — violates: ADR-004 (`docs/decisions/ADR-004.md`: «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited»). Проверено по коду: единственный путь записи `InventoryReservationService` существует (`inventory_service.py:4-11`) и не используется; docstring репозитория прямо запрещает такое использование (`inventory_repository.py:5` — «not for API handlers»). Исправление: инстанцировать `InventoryReservationService(InventoryRepository())` в обработчике и вызывать `service.save(...)`. Не исправляю сам — это изменение связывания компонентов (архитектурное), по политике сообщается, а не правится без явного запроса.

## Переиспользование
Не найдено. (Дублирование пути записи — часть находки выше.)

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
Прочитан staged-дифф и все смежные модули (`inventory_repository.py`, `inventory_service.py`, `docs/decisions/ADR-004.md`, `ai/project-rules.md`). Тесты не запускались: в проекте нет тестов и раннера (conftest.py пуст); ревью статическое. Исправления не применялись.

## Зависимости
Новых зависимостей изменение не вводит.