Файл формы отчёта `.ai-standards/code-review-report.md` в проекте отсутствует — похоже, `ai-sync sync-templates` не запускался, поэтому отчёт собран по резервному порядку разделов из инструкций. Отчёт ниже.

```markdown
ai-standards v2.5.0

## Код-ревью — eval-fixture

### Что сделано
Добавлен новый модуль `api_handler.py` с функцией `adjust_stock(sku, qty)`,
сохраняющей корректировку остатка на складе.

### Как сделано
Функция типизирована, модуль повторяет плоскую структуру проекта и стиль
соседних файлов; запись, однако, направлена в обход сервисного слоя (см. находку).

### Корректность
Не найдено.

### Архитектура и конвенции
🔴 api_handler.py:7-8 — API-обработчик создаёт `InventoryRepository` и пишет
в хранилище напрямую, минуя `InventoryReservationService` — нарушает:
docs/decisions/ADR-004.md («All inventory writes must go through
`InventoryReservationService`. Direct repository writes from API handlers
are prohibited»). Это подтверждает и докстринг самого репозитория
(inventory_repository.py:5 — «not for API handlers»). Исправление: направить
запись через сервис, например
`InventoryReservationService(InventoryRepository()).save({"sku": sku, "qty": qty})`.

### Переиспользование
Не найдено (неиспользование готового `InventoryReservationService` — та же
находка, что и выше).

### Эффективность
Не найдено.

### Качество
Не найдено.

### Проверки
Просмотрен staged-дифф (`git diff --cached`: один новый файл, +8 строк);
нарушение свергено с `docs/decisions/ADR-004.md` и смежными модулями
(`inventory_service.py`, `inventory_repository.py`). Тесты не запускались —
в проекте тестовой обвязки нет (`conftest.py` пуст, тестовых файлов не найдено).
```

Направление отчёта: чат (в code block выше). Найти помечена 🔴 как блокирующая, так как ADR-004 прямо запрещает такие записи.