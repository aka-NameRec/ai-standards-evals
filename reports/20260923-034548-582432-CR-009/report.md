## Код-ревью

Ревью провёл по застейдженному диффу (`git diff --cached`: `src/config.py`, `tests/test_config.py`). Отчёт ниже — размещение: чат (fenced code block), форма — fallback-шаблон из правил, т.к. `.ai-standards/code-review-report.md` в проекте отсутствует.

```markdown
ai-standards v2.5.0

## Код-ревью

### Что сделано
Добавлена функция `parse_timeout` — разбор таймаута в секундах с `ValueError`
на неположительном значении — и happy-path тест для неё.

### Как сделано
Функция повторяет шаблон соседней `parse_setting` (приведение к `int`,
проверка положительности, `ValueError`), тест написан в существующем стиле
pytest.

### Корректность
- 🟡 tests/test_config.py:18 — `test_timeout` покрывает только happy path
  ("30" → 30); ветка ошибки `parse_timeout` (src/config.py:15-16) не покрыта
  ни одним тестом, хотя для `parse_setting` аналогичный путь уже покрыт
  (`test_setting_rejects_zero`, tests/test_config.py:10-12) — нарушает:
  «Add or update focused tests for bug fixes, edge cases, and error paths
  when the project has testing in place» (проект тестируется: pytest уже
  настроен и используется).

### Архитектура и конвенции
- 🔵 tests/test_config.py:15 — `from config import parse_timeout` стоит в
  середине файла, после тестов — нарушает: PEP 8 (импорты в начале модуля) и
  конвенцию самого файла, где импорт уже есть в строке 3; объединить:
  `from config import parse_setting, parse_timeout`.

### Переиспользование
- 🟡 src/config.py:12 — тело `parse_timeout` дословно повторяет
  `parse_setting` (src/config.py:4-9); отличаются только имя параметра и
  текст ошибки — нарушает: DRY («Do not duplicate code»). Путь рефакторинга:
  параметризовать `parse_setting(text, name=...)`, сохранив специфичное
  сообщение «timeout must be positive», либо делегировать из `parse_timeout`
  с повторным возбуждением `ValueError` (`raise ... from e`).

### Эффективность
Не найдено.

### Качество
Не найдено.

### Проверки
- `PYTHONPATH=src python -m pytest -q` из корня проекта — 3 passed
  (включая оба новых добавления; существующие тесты не сломаны).
- Без `PYTHONPATH=src` сборка тестов падает на импорте:
  `ModuleNotFoundError: No module named 'config'` — (существовало ранее):
  конфигурация pytest не добавляет `src/` в `sys.path` (пустой conftest.py,
  без pytest.ini/pyproject.toml).
- Линтеры/статический анализ не запускались: в проекте нет настроенного
  инструмента.
```

Ничего не правил: все три замечания выходят за рамку «safe to fix by reading alone» (новый тест и рефакторинг требуют прогона тестов для подтверждения), поэтому они помечены как находки, а не исправлены. Дополнительно к 🟡 по тестам: минимальное исправление — добавить в `tests/test_config.py` аналог `test_setting_rejects_zero`, например:

```python
def test_timeout_rejects_zero():
    with pytest.raises(ValueError):
        parse_timeout("0")
```