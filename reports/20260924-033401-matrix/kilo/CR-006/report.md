```markdown
## Код-ревью

ai-standards 2.6.0

Примечание: файл `.ai-standards/code-review-report.md` в проекте отсутствует — вероятно, `ai-sync sync-templates` не запускался, поэтому отчёт собран по резервной структуре из правил.

**Задача** — не найдена (трекер не указан).

### Что сделано
Добавлен новый файл `api_handler.py` с функцией `adjust_stock(sku, qty)`, которая создаёт `InventoryRepository` и сохраняет элемент напрямую.

### Как сделано
Сигнатура функции типизирована, docstring на месте — стиль совпадает с остальными файлами репозитория.

### Корректность
Не найдено.

### Архитектура и конвенции
🔴 api_handler.py:8 — API-обработчик пишет в хранилище напрямую через `InventoryRepository` (создание на строке 7), минуя сервис — нарушает: ADR-004 (docs/decisions/ADR-004.md): «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited». Это подтверждает и docstring самого репозитория («not for API handlers»); правильный путь записи — `InventoryReservationService` из inventory_service.py:4, который уже принимает репозиторий в конструкторе.

### Переиспользование
Не найдено.

### Эффективность
Не найдено.

### Качество
Не найдено.

### Проверки
Просмотрен staged-дифф (`git diff --cached`, 1 файл, +8 строк); прочитаны `inventory_repository.py`, `inventory_service.py`, `docs/decisions/ADR-004.md`, `ai/project-rules.md`. Тесты не запускались — в репозитории тестов нет (`conftest.py` пуст), поведение `InventoryRepository.save` — заглушка.
```