## Код-ревью

`ai-standards v2.5.0`

**Что сделано**

Добавлен новый модуль `api_handler.py` с функцией `adjust_stock(sku, qty)`, которая сохраняет запись о товаре напрямую через `InventoryRepository`.

**Как сделано**

Модуль снабжён docstring, публичная граница функции аннотирована типами; структура передачи данных (dict в `save`) повторяет сигнатуру существующего слоя хранения.

**Корректность**

Не найдено.

**Архитектура и конвенции**

- 🔴 `api_handler.py:7` — API-обработчик выполняет запись напрямую в `InventoryRepository`, минуя `InventoryReservationService` — нарушает: ADR-004 (docs/decisions/ADR-004.md): «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited». Это подтверждает и docstring самого репозитория («not for API handlers»). Исправление: конструировать `InventoryReservationService(InventoryRepository())` и вызывать `service.save({"sku": sku, "qty": qty})`, оставив единственный путь записи за сервисом.

**Переиспользование**

Не найдено.

**Эффективность**

Не найдено.

**Качество**

Не найдено.

**Проверки**

Просмотрен staged-дифф (`git diff --cached`) и прочитаны сопутствующие модули: `inventory_repository.py`, `inventory_service.py`, `docs/decisions/ADR-004.md`. Тестов в репозитории нет (есть пустой `conftest.py`), поэтому код не запускался — проверка выполнена только чтением.

**Зависимости**

Изменение самодостаточно, затрагиваемых других репозиториев нет.

```
## Код-ревью

`ai-standards v2.5.0`

**Что сделано**

Добавлен новый модуль `api_handler.py` с функцией `adjust_stock(sku, qty)`, которая сохраняет запись о товаре напрямую через `InventoryRepository`.

**Как сделано**

Модуль снабжён docstring, публичная граница функции аннотирована типами; структура передачи данных (dict в `save`) повторяет сигнатуру существующего слоя хранения.

**Корректность**

Не найдено.

**Архитектура и конвенции**

- 🔴 `api_handler.py:7` — API-обработчик выполняет запись напрямую в `InventoryRepository`, минуя `InventoryReservationService` — нарушает: ADR-004 (docs/decisions/ADR-004.md): «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited». Это подтверждает и docstring самого репозитория («not for API handlers»). Исправление: конструировать `InventoryReservationService(InventoryRepository())` и вызывать `service.save({"sku": sku, "qty": qty})`, оставив единственный путь записи за сервисом.

**Переиспользование**

Не найдено.

**Эффективность**

Не найдено.

**Качество**

Не найдено.

**Проверки**

Просмотрен staged-дифф (`git diff --cached`) и прочитаны сопутствующие модули: `inventory_repository.py`, `inventory_service.py`, `docs/decisions/ADR-004.md`. Тестов в репозитории нет (есть пустой `conftest.py`), поэтому код не запускался — проверка выполнена только чтением.

**Зависимости**

Изменение самодостаточно, затрагиваемых других репозиториев нет.
```

Отчёт опубликован в чате (файл `.ai-standards/code-review-report.md` в проекте отсутствует — использован резервный формат отчёта).