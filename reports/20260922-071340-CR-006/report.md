Ревью провёл по staged-диффу (`api_handler.py`). Файл `.ai-standards/code-review-report.md` в проекте отсутствует — значит, `ai-sync sync-templates` не запускался, поэтому отчёт свёрстан по резервному формату из правил. Правки в код не вносились (нарушение — уровень архитектуры, решение за автором). Отчёт размещаю в чате:

```markdown
## Код-ревью

ai-standards v2.5.0

**Что сделано**
Добавлен новый файл `api_handler.py` с функцией `adjust_stock(sku, qty)`: она создаёт `InventoryRepository` и сохраняет запись `{"sku", "qty"}` напрямую в репозиторий.

**Как сделано**
Функция типизирована (`str`/`int`/`None`), есть докстринги; формат записи (словарь) совпадает с существующими сигнатурами `InventoryRepository.save` и `InventoryReservationService.save`.

**Архитектура и конвенции**
- 🔴 api_handler.py:8 — API-обработчик пишет в inventory напрямую через `InventoryRepository`, минуя сервис записи — нарушает: ADR-004 (docs/decisions/ADR-004.md:3-4): «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited». Готовый путь уже есть: `InventoryReservationService` (inventory_service.py:4) принимает репозиторий в конструкторе и делегирует ему `save`.
- 🔵 api_handler.py:1 (no contract) — у изменённого модуля нет module-contract: записей с `type: module-contract` в `docs/architecture/**` и корневого `MODULE_CONTRACT.md` в проекте нет; это пробел, который стоит закрыть, а не дефект.

**Корректность**
Не найдено.

**Переиспользование**
Не найдено.

**Эффективность**
Не найдено.

**Качество**
Не найдено.

**Проверки**
Прочитаны: `git diff --staged` (новый `api_handler.py`, 8 строк), `docs/decisions/ADR-004.md`, `inventory_repository.py`, `inventory_service.py`, `git log`. Тестов в проекте нет (`conftest.py` пуст, файлов тестов нет) — поведение кода не запускалось.
```