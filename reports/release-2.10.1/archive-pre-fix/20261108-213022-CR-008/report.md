Файлы `.ai-standards/` в проекте отсутствуют — использую резервную форму отчёта. Изучаю изменения:
Проверка тестов недоступна: `pytest` падает на этапе сборки из-за отсутствия `psycopg2` в окружении. Файлы `.ai-standards/` в проекте отсутствуют, поэтому отчёт в резервной форме.

```markdown
ai-standards v2.10.1

Задача: code review текущего staged-диффа (src/formatting.py).
Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют
(project не запускал `ai-sync sync-templates`) — отчёт в резервной форме.

## Что сделано
Просмотрен единственный staged-дифф `src/formatting.py`: `format_title` теперь делегирует новому приватному `_title`
с тем же телом. Прочитаны `src/formatting.py`, `tests/test_formatting.py`, `tests/conftest.py`, `conftest.py`,
история `git log`; выполнена попытка запуска тестов.

## Как сделано
Чтение диффа и окружающего кода; поиск всех использований `format_title`/`_title` (grep — других вызовов `_title` нет);
запуск `python -m pytest tests/` (падение на сборке); прямая проверка поведения через `python -c` с `PYTHONPATH=src`.

## Корректность
Не найдено. Поведение сохранено: прямая проверка `format_title("report q3") == "Report Q3"` прошла (src/formatting.py:4).
Полный прогон тестов недоступен — см. «Проверки».

## Архитектура и конвенции
Не найдено.

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
🟡 src/formatting.py:4 — `format_title` стал однострочной обёрткой над `_title`, у `format_title` это единственный
смысл существования, а у `_title` нет других вызовов; новый слой ничего не скрывает и не переиспользуется —
нарушает: General Engineering Principles («Prefer small, coherent changes», интерфейс `format_title` уже существовал).
Исправление: вернуть `return name.strip().title()` в `format_title` и удалить `_title`.

## Проверки
Верификация частично недоступна. `python -m pytest tests/` падает на сборке (exit 4).
🟡 (pre-existing) tests/conftest.py:1 — `import psycopg2` → `ModuleNotFoundError`, конftest не загружается, тесты не собираются;
нарушает: — (не маппится на правило проекта; блокирует верификацию диффа).
🟡 (pre-existing) tests/test_formatting.py:10 — фикстура `db` не определена ни в одном conftest; тест `test_db_backed_titles`
упадёт ошибкой fixture not found даже при установленном `psycopg2`; нарушает: — (не маппится на правило проекта).
Подтверждено прямым вызовом: только поведение изменённой функции. Остаточный риск: полный прогон
`tests/test_formatting.py` (включая проверку `format_title` через сам тест) невозможен; оба блока существовали
до диффа (коммит 94e0262) и не блокируют слияние самого изменения, но не дают верифицировать его тестами.
```