Файл формы отчёта `.ai-standards/code-review-report.md` в проекте отсутствует (как и `.ai-standards/references/`), то есть `ai-sync sync-templates` не запускался — использую резервный формат отчёта из AGENTS.md. Ревью выполняю по staged-диффу (новый файл `api_handler.py`), сверяя его с кодом репозитория и ADR-004.

```markdown
ai-standards v2.10.1

Задача
- Bare-запрос «code review»: ревью staged-изменений — новый файл `api_handler.py` (+8 строк).

Что сделано
- (Ревью, ничего не менялось.) Добавлен обработчик `adjust_stock(sku, qty)`, создающий `InventoryRepository` и сохраняющий запись `{"sku": ..., "qty": ...}` напрямую в хранилище.

Как сделано
- Напрямую: импорт `InventoryRepository` (api_handler.py:3), инстанцирование и вызов `save` внутри функции (api_handler.py:7-8); сервисный слой не задействован.

Корректность
- Не найдено. Код тривиален, логических ошибок не содержит. Замечание вне скоупа (pre-existing): `InventoryRepository.save` — заглушка без реализации (inventory_repository.py:7-8).

Архитектура и конвенции
- 🔴 api_handler.py:7-8 — API-обработчик инстанцирует репозиторий и пишет в инвентарь напрямую, минуя сервис; прямые записи репозитория из API-обработчиков запрещены — violates: docs/decisions/ADR-004.md («All inventory writes must go through InventoryReservationService. Direct repository writes from API handlers are prohibited»). Намерение подтверждает и докстринг репозитория (inventory_repository.py:5: «Direct storage access; not for API handlers»). Исправление: вести запись через `InventoryReservationService` (inventory_service.py:4 — «Single write path for inventory mutations»), передавая экземпляр `InventoryRepository` в его конструктор, а не создавая репозиторий внутри обработчика. Сам не исправляю: меняется путь записи и компоновка (wiring), безопасность правки чтением не устанавливается — решение за автором.

Переиспользование
- Не найдено. (Обход готового сервисного слоя — часть находки 🔴 выше; отдельно не дублирую.)

Эффективность
- Не найдено.

Качество
- 🔵 api_handler.py:6 — входные параметры `sku`/`qty` поступают из API-границы без валидации (пустой `sku`, `qty <= 0` уходят прямо в запись) — violates: правило python-стека «Parse and validate untrusted input at the application boundary before it reaches business logic». Опционально: в проекте нет фреймворка/DTO-слоя, конкретная форма валидации — на усмотрение автора.

Проверки
- Сверка чтением с docs/decisions/ADR-004.md, inventory_service.py, inventory_repository.py, ai/project-rules.md. Тестов и линтеров в репозитории нет (conftest.py пуст, pyproject/ruff/flake8 отсутствуют), прогон проверок невозможен. Оставшийся риск: поведение `save` в рантайме не проверялось, так как реализация — заглушка.
```