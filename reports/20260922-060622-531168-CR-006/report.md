Ревью выполнено. Замечание: файла `.ai-standards/code-review-report.md` в проекте нет — шаблон отчёта не синхронизирован (нужно запустить `ai-sync sync-templates`), поэтому использую резервную структуру отчёта.

```markdown
ai-standards v2.5.0

## Код-ревью

**Задача:** не указана.

**Что сделано:** добавлен новый файл `api_handler.py` с функцией `adjust_stock`, которая записывает изменение остатка на складе напрямую через `InventoryRepository`.

**Как сделано:** обработчик создаёт репозиторий локально и передаёт ему сырой словарь — в остальном стиль (типизация, докстринги, именование) повторяет соседние модули.

**Архитектура и конвенции**
- 🔴 api_handler.py:6-7 — обработчик API выполняет запись в инвентарь напрямую через `InventoryRepository`, минуя `InventoryReservationService` — нарушает: ADR-004 (`docs/decisions/ADR-004.md`: «All inventory writes must go through `InventoryReservationService`. Direct repository writes from API handlers are prohibited»), а также контракт самого репозитория (inventory_repository.py:5 «not for API handlers») и сервиса (inventory_service.py:5 «Single write path for inventory mutations»). Запись должна идти через `InventoryReservationService`.

**Корректность**
Не найдено.

**Переиспользование**
Не найдено.

**Эффективность**
Не найдено.

**Качество**
Не найдено.

**Проверки:** полный диф просмотрен (`git diff --cached`, 1 файл, +8 строк); сверка с ADR-004, `inventory_repository.py` и `inventory_service.py` выполнена по исходникам, а не по дифу. Тесты не запускались — в репозитории тестов нет (conftest.py пуст), проверять нечего.

**Зависимости:** изменение самодостаточное, затрагивает только этот репозиторий.
```

Отчёт выведен в чат (в код-блоке выше), файл не создавался. Ещё раз: `.ai-standards/code-review-report.md` отсутствует — стоит выполнить `ai-sync sync-templates`, чтобы форма отчётов была зафиксирована шаблоном.