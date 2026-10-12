`rtk pytest` reports collection failure in both runs (the log is genuine — `ModuleNotFoundError: No module named 'config'`); running the raw command to double-check the path setup:
Отчёт размещён в чате (файл `.ai-standards/code-review-report.md` в проекте отсутствует, использован резервный формат из инструкций).

```markdown
ai-standards v2.6.0

## Код-ревью

### Что сделано
В `src/config.py` добавлена функция `parse_timeout` — разбор таймаута в секундах
с `ValueError` для неположительных значений; в `tests/test_config.py` — тест
happy-path для неё.

### Как сделано
Функция повторяет сложившийся в модуле шаблон `parse_setting`, тест написан
в существующем стиле pytest; диф минимальный. Отступления — в находках ниже.

### Корректность
- 🟡 tests/test_config.py:18 — `test_timeout` покрывает только happy-path; ветка
  ошибки `value <= 0` в `parse_timeout` (src/config.py:15-16) не протестирована —
  нарушает: General Engineering Principles — «Add or update focused tests for
  bug fixes, edge cases, and error paths when the project has testing in place».
  Тестирование в проекте есть, соседний `test_setting_rejects_zero`
  (tests/test_config.py:10) задаёт шаблон: достаточно добавить
  `test_timeout_rejects_zero` с `pytest.raises(ValueError)`
  (нулевое и отрицательное значение).

### Архитектура и конвенции
- 🟡 tests/test_config.py:15 — импорт `from config import parse_timeout`
  размещён в середине файла, после тестов — нарушает: PEP 8 (импорты в начале
  файла) и стиль самого файла, где импорты уже собраны наверху
  (tests/test_config.py:3). Исправление: объединить в
  `from config import parse_setting, parse_timeout`.
- 🔵 conftest.py — файл пустой и не добавляет `src/` в `sys.path`, поэтому
  запуск `pytest` из корня падает на коллекции с `ModuleNotFoundError:
  No module named 'config'` (существовало ранее) — нарушает: конкретное правило
  в своде отсутствует, это проблема конфигурации тестового окружения, а не
  диффа. Путь исправления: дописать в `conftest.py` добавление `src/` в
  `sys.path` или задать `pythonpath` в конфиге pytest.

### Переиспользование
- 🔵 src/config.py:12 — `parse_timeout` дословно повторяет тело `parse_setting`
  (src/config.py:4-9), отличается только текст ошибки — нарушает: DRY
  («Do not duplicate code»). Путь рефакторинга: делегировать
  (`return parse_setting(text)`) или сделать алиас, если различие текстов
  ошибок несущественно; если «setting» и «timeout» — разные доменные понятия,
  допустимо оставить как есть по решению автора.

### Эффективность
Не найдено.

### Качество
Не найдено.

### Проверки
- `PYTHONPATH=src python -m pytest -q` — 3 passed, включая новый `test_timeout`;
  запуск без `PYTHONPATH=src` падает на коллекции (см. находку про
  conftest.py, существовало ранее).
- Lint/тайпчек: конфигурация в репозитории отсутствует, не проверялось.
- Примечание: `rtk pytest` дважды показал ошибку коллекции даже с заданным
  `PYTHONPATH=src`, поэтому финальный прогон выполнен напрямую
  через `python -m pytest`.
```

Согласно политике «Fixing While Reviewing» правки не вносились: основной находке нужен прогон тестов после добавления, а файлы уже находятся в индексе.