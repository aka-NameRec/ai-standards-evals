Файл `.ai-standards/code-review-report.md` в проекте отсутствует (шаблоны не синхронизированы через `ai-sync sync-templates`), поэтому отчёт собран по резервной структуре из правил. Ревью выполнено по staged-диффу (новый файл `api_handler.py`).

```markdown
ai-standards v2.6.0

## Код-ревью

### Что сделано
Добавлен `api_handler.py` с функцией `adjust_stock()`, которая сохраняет
корректировку остатка по SKU через репозиторий.

### Как сделано
Функция переиспользует существующий модуль `inventory_repository`, параметры
протипизированы, функция осталась небольшой и одноцелевой.

### Корректность
Не найдено.

### Архитектура и конвенции
- 🔴 api_handler.py:7-8 — обработчик напрямую создаёт `InventoryRepository` и
  пишет в хранилище (`repository.save({...})`), минуя сервисный слой.
  `InventoryReservationService` (inventory_service.py:4) объявлен единственным
  путём записи, а репозиторий прямо помечен «not for API handlers»
  (inventory_repository.py:5) — нарушает: ADR-004
  (docs/decisions/ADR-004.md:3-4): «All inventory writes must go through
  `InventoryReservationService`. Direct repository writes from API handlers
  are prohibited». Исправление: собрать запись через сервис, например
  `InventoryReservationService(InventoryRepository()).save({"sku": sku, "qty": qty})`,
  либо получить сервис через стандартную точку сборки проекта, если она есть.

### Переиспользование
Не найдено.

### Эффективность
Не найдено.

### Качество
Не найдено.

### Проверки
- `rtk git status`, `rtk git diff --cached` — просмотрен staged-дифф
  (1 новый файл, +8 строк).
- `python3 -m py_compile api_handler.py` — OK (синтаксис валиден).
- Не проверялось: поведение в рантайме (`InventoryRepository.save` — заглушка),
  тесты в репозитории отсутствуют (conftest.py пуст), pytest не запускался.
```

Отчёт отправлен в чат (в файл не сохранял — не просили). Находка 🔴 блокирующая: нарушение запрета из ADR-004; исправление выходит за рамки мелких правок при ревью и ждёт отдельной команды.