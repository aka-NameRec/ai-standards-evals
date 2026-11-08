Проверки выполнены: прочитаны workflow-файлы (`.ai-standards/references/features/code-review.md`, `.ai-standards/code-review-report.md`, `.ai-standards/references/code-review-reporting.md`), ревьюируется текущий staged-дифф (`helper.py`), краевые случаи проверены запуском Python.

```markdown
## Код-ревью

ai-standards 2.9.0

### Что сделано
`percentile` в `helper.py` теперь при пустом `values` возбуждает `ValueError("empty values")` вместо «голого» `IndexError`.

### Как сделано
Добавлен guard `if not values` перед индексацией `sorted(values)[index]` (helper.py:7-8). Дублирования не внесено: `stats.py` не затронут, ничего общего с `mean` нет. Сообщение исключения конкретное и действует как подсказка вызывающему.

### Корректность
- 🔵 (существовало ранее) helper.py:4 — параметр `p` не валидируется: `percentile([1, 2, 3], -100)` молча возвращает `1` (проверено запуском), `percentile([1, 2, 3], 200)` даёт «голый» `IndexError`; новый guard закрывает только пустой список, а этот класс входных данных остаётся непроверенным — нарушает: Python Stack «Raise exceptions with actionable context instead of returning sentinel values that hide failure»

### Архитектура и конвенции
- Не найдено.

### Переиспользование
- Не найдено.

### Эффективность
- Не найдено.

### Качество
- 🔵 helper.py:6-8 — проверка на пустоту стоит после вычисления `index` (при пустом `values` он всё равно вычисляется в 0, на поведение не влияет); guard-условие читается естественнее первой строкой функции — именованного правила нет, замечание чисто о читаемости

### Проверки
- запуск `python3` против текущего кода — `percentile([], 50)` → `ValueError("empty values")`; `percentile([1, 2, 3], -100)` → `1`; `percentile([1, 2, 3], 200)` → `IndexError`
- автотесты не запускались — тестовой инфраструктуры в проекте нет
```

Место публикации: чат (fenced code block). Исправления не применялись — по умолчанию ревью только сообщает о находках.