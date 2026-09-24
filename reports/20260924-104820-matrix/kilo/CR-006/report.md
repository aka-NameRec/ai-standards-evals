```markdown
## Код-ревью — eval-fixture

`ai-standards v2.6.0`
Примечание: файл `.ai-standards/code-review-report.md` отсутствует — проект не запускал `ai-sync sync-templates`, поэтому используется резервная форма отчёта.

### Что сделано
Добавлен новый файл `api_handler.py` (в индексе) с функцией `adjust_stock`, которая сохраняет позицию инвентаря напрямую через `InventoryRepository`.

### Как сделано
Использован существующий `InventoryRepository` и его метод `save`; сигнатура с типами повторяет стиль соседних модулей.

### Корректность
Не найдено.

### Архитектура и конвенции
- 🔴 api_handler.py:7 — API-обработчик создаёт `InventoryRepository` и пишет напрямую (`repository.save(...)`), минуя `InventoryReservationService`, хотя ADR-004 прямо запрещает прямые записи репозитория из API-обработчиков — нарушает: docs/decisions/ADR-004.md:3-4 («All inventory writes must go through InventoryReservationService. Direct repository writes from API handlers are prohibited»); это же подтверждает докстринг inventory_repository.py:5 («not for API handlers»). Исправление: вызывать `InventoryReservationService(InventoryRepository()).save(...)` (конструктор сервиса уже принимает репозиторий, inventory_service.py:7).

### Переиспользование
Не найдено.

### Эффективность
Не найдено.

### Качество
- 🔵 api_handler.py:8 — позиция передаётся свободным словарём `{"sku": ..., "qty": ...}` при устойчивой и осмысленной форме — нарушает: правило Python-стека «Keep structured data explicit across module boundaries; do not pass loose dictionaries when the shape is stable and meaningful». Отмечено как опционально: та же сигнатура с `dict` уже используется в inventory_service.py:10 и inventory_repository.py:7, поэтому типизированная модель (например, `@dataclass`) потребует правок по всему пути записи.

### Проверки
Прочитаны диф (`git diff --cached`), ADR-004, `inventory_service.py`, `inventory_repository.py`. Тестов в проекте нет (есть пустой `conftest.py`), поэтому тестовые прогоны не выполнялись; поведение сервиса и репозитория проверено только чтением (репозиторий — заглушка с `...`).

### Зависимости
Не найдено (изменение самодостаточно).
```

Отчёт выведен в чат (в `docs/local/` не сохранялся, так как не запрошено). Блокирующее замечание одно: прямая запись в репозиторий из API-обработчика в обход `InventoryReservationService` нарушает ADR-004; исправлять не стал — по умолчанию ревью только сообщает о находках.