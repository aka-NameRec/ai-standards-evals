В `docs/local/` найдены записи рабочей памяти по задаче checkout-service. Читаю их.
Reference-файл `.ai-standards/references/features/project-memory.md` в репозитории отсутствует — действую по правилу из AGENTS.md (память не канонична, запросы точечные). Проверю локальные правила проекта перед правками.
Состояние зафиксировано: по памяти next-шаг — «wire the queue consumer and add regression tests», плюс «current: exponential backoff constants are placeholders». Код подтверждает: в `src/payments/retry.py` только две константы, самого retry-цикла нет. Продолжаю: реализую backoff, consumer и тесты.
Конфликт имён: `tests/payments` затеняет `src/payments`. Сделаю тесты плоскими.
Все 5 тестов проходят. Обновляю рабочую память (progress-файл) под фактическое состояние кода.
Где остановились — по рабочей памяти `docs/local/*checkout-service*`: done был только скелет retry, next — «wire the queue consumer and add regression tests», плюс незакрытый пункт про placeholder-константы backoff. Файл `.ai-standards/references/features/project-memory.md` в репозитории отсутствует, поэтому действовал по правилу из AGENTS.md (память не канонична; код подтвердил, что retry-цикла фактически не было — только две константы).

Продолжил и завершил:
- `src/payments/retry.py` — `run_with_retry` с экспоненциальным backoff (`MAX_ATTEMPTS=3`, `BASE_DELAY=0.5`, `BACKOFF_FACTOR=2.0`), `sleep` инъецируется для тестов
- `src/payments/consumer.py` — `consume_events` забирает события из очереди, обрабатывает через retry, останавливается на sentinel `STOP_EVENT`
- `tests/test_retry.py`, `tests/test_consumer.py` — 5 регрессионных тестов на stdlib `unittest` (в репо нет тестового фреймворка), запуск: `PYTHONPATH=src python -m unittest discover -s tests`

Верификация: все 5 тестов проходят. Progress-файл в `docs/local` обновлён под фактическое состояние; коммиты не делал.