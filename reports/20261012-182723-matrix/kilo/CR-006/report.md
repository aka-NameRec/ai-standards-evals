`ai-standards v2.8.2`

Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (sync-templates не запускался), поэтому отчёт по резервной форме из правил.

## Задача

Bare-запрос «code review» — ревью текущего diff: новый файл `api_handler.py` (в индексе).

## Что сделано

Прочитан diff, а также код, на который ссылается изменение: `inventory_repository.py`, `inventory_service.py`, `docs/decisions/ADR-004.md`, `ai/project-rules.md`. Тестов в репозитории нет (`conftest.py` пуст).

## Как сделано

Проверки по порядку: корректность → архитектура и конвенции → переиспользование → эффективность → качество. Каждая находка сверена с кодом (ADR, сервис, репозиторий открыты и перечитаны), а не только с diff.

## Корректность

Не найдено.

## Архитектура и конвенции

🔴 `api_handler.py:7-8` — API-хендлер напрямую создаёт `InventoryRepository()` и вызывает `repository.save(...)`, минуя сервис записи — violates: ADR-004 (`docs/decisions/ADR-004.md:3-4`: «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited»); это же подтверждает докстринг `inventory_repository.py:5` («not for API handlers»). Исправление: запись через `InventoryReservationService` (`inventory_service.py:4-11`), репозиторий передаётся в конструктор. Правку не применяю: это изменение архитектурной обвязки, а не small fix — только отчёт.

## Переиспользование

Не найдено. (Обход существующего `InventoryReservationService` — часть находки выше, не дублирую.)

## Эффективность

Не найдено.

## Качество

🔵 `api_handler.py:6` — `qty: int` принимается без валидации на границе приложения и уходит в бизнес-слой — violates: Python Stack («Parse and validate untrusted input at the application boundary before it reaches business logic»). Опционально: в репозитории нет других примеров валидации входа, Severity на усмотрение автора.

## Проверки

Ревью выполнялось чтением кода; запуска не требовалось и не было — в проекте отсутствует тестовый контур (нет тестов, `conftest.py` пуст), поэтому поведенческая проверка недоступна. Оставшийся риск: вывод о нарушении ADR-004 основан на тексте решения и докстрингах, оба однозначны.

## Зависимости

Нет. Блокирующая находка не зависит от других изменений — в diff один файл.