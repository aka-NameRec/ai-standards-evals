Ревью по текущему (застейдженному) диффу. Отчёт размещён в чате; файла `.ai-standards/code-review-report.md` в проекте нет (`ai-sync sync-templates` не запускался), поэтому использован резервный формат из правил.

```markdown
ai-standards v2.6.0

## Код-ревью

> `.ai-standards/code-review-report.md` отсутствует — шаблон отчёта не синхронизирован
> (`ai-sync sync-templates` не выполнялся); использован резервный формат из правил.

### Что сделано
Добавлена функция `parse_timeout` в `src/config.py` — разбор таймаута в секундах с `ValueError`
для неположительных значений — и happy-path тест `test_timeout` в `tests/test_config.py`.

### Как сделано
Функция и тест повторяют существующий образец `parse_setting` (int + проверка положительности,
`ValueError`, англоязычные docstring и текст ошибки) и стиль имён соседних тестов.

### Корректность
- 🟡 tests/test_config.py:18 — `test_timeout` покрывает только happy path («30»), хотя docstring
  `parse_timeout` (src/config.py:13) явно обещает `ValueError` для неположительных значений, а у
  соседней `parse_setting` негативная ветка покрыта (`test_setting_rejects_zero`,
  tests/test_config.py:10) — регрессия в ветке ошибки останется незамеченной — нарушает:
  общие инженерные принципы — сфокусированные тесты для edge cases и error paths, когда в проекте есть тесты

### Архитектура и конвенции
- 🔵 tests/test_config.py:15 — импорт `from config import parse_timeout` стоит в середине файла,
  после тестов; его место наверху, рядом с `from config import parse_setting` (можно объединить в
  `from config import parse_setting, parse_timeout`) — нарушает: PEP 8 (импорты верхнего уровня в начале файла, E402)
- 🔵 tests/test_config.py:3 (существовало ранее) — обычный `pytest` в корне репозитория не собирает
  тесты: `ModuleNotFoundError: No module named 'config'` (проверено запуском); сбор проходит только
  с `PYTHONPATH=src`, пустой conftest.py и отсутствие pytest-конфига не добавляют `src` в `sys.path` —
  нарушений конкретного правила из свода нет; сообщаю, так как это напрямую блокирует проверку тестами

### Переиспользование
- 🔵 src/config.py:12 — `parse_timeout` дословно повторяет `parse_setting` (src/config.py:4-9),
  отличаясь только docstring и текстом ошибки; путь рефакторинга: общий помощник вида
  `_parse_positive_int(raw, name)` либо делегирование `parse_timeout` → `parse_setting`
  (текст сообщения изменится; если «timeout must be positive» важен вызывающим — оставить как есть) —
  нарушает: DRY (не дублировать код)

### Эффективность
Не найдено.

### Качество
Не найдено.

### Проверки
- `PYTHONPATH=src pytest -q` — 3 passed (0.02s). Замечание: обёртка `rtk pytest` не пробросила
  `PYTHONPATH` (оба запуска через rtk упали с `ModuleNotFoundError`), финальный запуск выполнен
  обычным `pytest` без rtk.
- Не проверялось: линтеры и проверка типов — в репозитории не настроены
  (нет pyproject.toml / ruff / flake8 / mypy); миграций и UI нет.
```

Находка 🟡 — главная: закрывается добавлением в `test_timeout` проверки `pytest.raises(ValueError)` для `"0"` (по образцу `test_setting_rejects_zero`). Правки не вносил — ревью в режиме отчёта.