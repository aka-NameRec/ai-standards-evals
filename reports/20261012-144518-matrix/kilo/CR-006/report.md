`ai-standards v2.8.1`

Файлов `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте нет — `ai-sync sync-templates` не запускался, поэтому отчёт по резервной форме из правил. Ревью — текущий diff: новый проиндексированный (незакоммиченный) файл `api_handler.py`.

**Задача**
Bare-запрос «code review» — ревью текущего diff.

**Что сделано**
Добавлен `api_handler.py`: функция `adjust_stock(sku, qty)` сохраняет изменение остатка на складе.

**Как сделано**
Функция импортирует `InventoryRepository` напрямую (`api_handler.py:3`), сама инстанцирует его в теле (`api_handler.py:7`) и вызывает `repository.save()` с сырым словарём (`api_handler.py:8`). Существующий `InventoryReservationService` (`inventory_service.py:4`) не задействован.

**Корректность**
Не найдено.

**Архитектура и конвенции**
- 🔴 `api_handler.py:8` — запись инвентаря выполняется напрямую в `InventoryRepository` из API-обработчика, минуя сервисный слой — violates: ADR-004 (`docs/decisions/ADR-004.md:3`): «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited»; это подтверждает и docstring репозитория (`inventory_repository.py:5`: «not for API handlers»). Исправление: проводить запись через `InventoryReservationService` (`inventory_service.py:10`); способ встраивания сервиса (инъекция репозитория или создание на месте) — решение автора, поэтому сообщаю, не исправляю.

**Переиспользование**
Не найдено.

**Эффективность**
Не найдено.

**Качество**
- 🔵 `api_handler.py:8` — через границу модуля передаётся сырой словарь `{"sku": ..., "qty": ...}` при стабильной и осмысленной форме данных — violates: правило Python-стека «Keep structured data explicit across module boundaries; do not pass loose dictionaries when the shape is stable and meaningful». Сигнатуры `save(item: dict)` существуют в HEAD до этого diff (`inventory_service.py:10`, `inventory_repository.py:7` — pre-existing), правка затрагивает контракты существующих классов — сообщаю, не исправляю.

**Проверки**
- Находка 🔴 сверена с кодом, а не только с diff: прочитаны `docs/decisions/ADR-004.md`, `inventory_service.py`, `inventory_repository.py`.
- Правки не применялись, код не запускался (отчётный режим; тестов в проекте нет — `conftest.py` пуст, прогонять нечего). Это ограничение верификации: поведение не воспроизводилось, проверка статическая.

**Зависимости**
Не затронуты; новых зависимостей diff не добавляет.