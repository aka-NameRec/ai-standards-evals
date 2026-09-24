ai-standards v2.6.0

Файлов `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте нет — `ai-sync sync-templates`, судя по всему, не запускался, поэтому отчёт собран по резервной форме из правил.

## Что сделано
Проанализирован staged-дифф (`git diff --cached`): новый файл `api_handler.py` (8 строк). Незастейдженных изменений нет (`git diff` пуст).

## Как сделано
Ревью выполнено чтением кода, а не только диффа: прочитаны `api_handler.py`, `inventory_service.py`, `inventory_repository.py`, `docs/decisions/ADR-004.md`, `ai/project-rules.md`, `conftest.py`.

## Корректность
Не найдено.

## Архитектура и конвенции
- 🔴 api_handler.py:7 — API-обработчик пишет напрямую в `InventoryRepository`, минуя `InventoryReservationService` (импорт на api_handler.py:2) — violates: docs/decisions/ADR-004.md:3-4 («All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited.»); это подтверждает и docstring `inventory_repository.py:5` («Direct storage access; not for API handlers»). Исправление: направить запись через `InventoryReservationService` — по inventory_service.py:10-11 это чистая делегация в репозиторий, поведение не изменится. Правку не вносил: файл уже в индексе, и смену пути записи стоит применять отдельным патчем по явному запросу.

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
- 🔵 api_handler.py:7 — на границе модулей передаётся неявный словарь `{"sku": ..., "qty": ...}` при стабильной и осмысленной форме данных — violates: правило стека Python из AGENTS.md («Keep structured data explicit across module boundaries; do not pass loose dictionaries when the shape is stable and meaningful»). Отмечаю как опциональное: сигнатуры `InventoryReservationService.save` и `InventoryRepository.save` тоже принимают `dict` (pre-existing стиль), поэтому полноценное исправление — типизированная модель (`@dataclass`) на всей цепочке записи, а не только в обработчике.

## Проверки
- Дифф снят через `git diff --cached`; выводы сверены с исходниками `inventory_service.py`, `inventory_repository.py` и ADR-004, а не только с текстом диффа.
- Тесты не запускались: тестовой базы в репозитории нет (`conftest.py` пуст, файлов тестов нет). Правки в рамках ревью не вносились, поэтому прогон не требовался; предложенное 🔴-исправление перед применением стоит проверить запуском, если тесты появятся.

## Зависимости
Новых зависимостей изменение не добавляет; существенные зависимости не затронуты.