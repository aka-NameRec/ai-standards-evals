`ai-standards v2.6.0`

Примечание: файлов `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте нет — проект не запускал `ai-sync sync-templates`, поэтому отчёт собран по резервной форме (fallback).

## Что сделано
Добавлен новый файл `api_handler.py` (staged, 8 строк): функция `adjust_stock(sku: str, qty: int) -> None`, создающая `InventoryRepository` и вызывающая `repository.save(...)` напрямую.

## Как сделано
Импорт `InventoryRepository` из `inventory_repository.py`, создание экземпляра внутри функции, запись словаря `{"sku": ..., "qty": ...}`.

## Корректность
Не найдено. Синтаксис проверен (`py_compile` — OK); сам вызов делегируется в `InventoryRepository.save` (inventory_repository.py:7).

## Архитектура и конвенции
- 🔴 api_handler.py:8 — API-обработчик пишет в инвентарь напрямую через `InventoryRepository`, минуя сервис (`import` в api_handler.py:3, запись в api_handler.py:8) — violates: ADR-004 (docs/decisions/ADR-004.md:3–4): «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited.» Это подтверждает и докстринг самого репозитория: «Direct storage access; not for API handlers» (inventory_repository.py:5). Исправление: провести запись через `InventoryReservationService` (inventory_service.py:4), который принимает репозиторий в конструкторе и является единственным путём записи. Не исправляю в рамках ревью — это архитектурное решение по ADR, сообщаю автору.
- 🔵 api_handler.py:7 — зависимость (`InventoryRepository()`) создаётся внутри функции, что мешает подмене в тестах — violates: правило Python-стека «Keep application wiring separate from business logic» (в проекте есть пустой `conftest.py`, тесты предполагаются). Опционально: строить цепочку `InventoryReservationService(InventoryRepository())` на уровне композиции или принимать зависимость параметром.

## Переиспользование
Не найдено. Код не дублирует существующую логику; вопрос в выборе неправильного существующего компонента (см. Архитектура).

## Эффективность
Не найдено.

## Качество
Не найдено. Докстринг, типы, англоязычные строки — соответствуют конвенциям.

## Проверки
`python3 -m py_compile api_handler.py` — OK. Тестов в проекте нет (`conftest.py` пуст). Находка 🔴 сверена с кодом, а не только с диффом: прочитаны ADR-004, `inventory_service.py`, `inventory_repository.py`.

## Зависимости
Исправление 🔴 определяется решением по ADR-004; после него находка 🔵 остаётся актуальной для места сборки зависимостей.