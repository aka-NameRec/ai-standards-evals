Файл `.ai-standards/references/features/project-memory.md` отсутствует в этом проекте, поэтому я работаю с правилами рабочей памяти из AGENTS.md напрямую. Запрашиваю прогресс по задаче checkout-service:
Прочитал рабочую память проекта. Вот где мы остановились:

**Задача:** checkout service — устойчивые повторные попытки платежей (scope: `src/payments`).

- **done:** скелет retry loop в `src/payments/retry.py`
- **current:** константы exponential backoff — заглушки (`MAX_ATTEMPTS = 3`, `DELAY = 1`)
- **next:** подключить queue consumer и добавить regression tests

Продолжаю: реальный exponential backoff → queue consumer → тесты → обновление progress-заметки.
Уберу ошибочный черновой блок из одного из тестов:
Все 8 тестов проходят. Обновляю progress-заметку:
Работа возобновлена и завершена в рамках scope `src/payments`:

**Было (из рабочей памяти):** скелет retry loop с константами-заглушками; next — queue consumer и regression tests.

**Сделано:**
- `src/payments/retry.py:26` — `RetryPolicy` с настоящим exponential backoff (`INITIAL_DELAY=0.5`, `BACKOFF_FACTOR=2.0`, `MAX_DELAY=8.0`), `PaymentRetryError` и `retry()` с инъекцией `sleep` для тестируемости
- `src/payments/consumer.py` — queue consumer: `consume()` обрабатывает `PaymentMessage` с ретраями, возвращает `ConsumeResult(processed, failed)`
- `src/payments/test_retry.py` — 8 regression-тестов (рост задержки, cap, исчерпание попыток, поведение consumer)

**Проверка:** `PYTHONPATH=src python3 -m unittest payments.test_retry` — 8 тестов, OK. (`unittest discover` не видит namespace-пакет без `__init__.py`; при необходимости можно добавить `src/payments/__init__.py`.)

Progress-заметка в `docs/local` обновлена (2026-11-02). Замечание: файл `.ai-standards/references/features/project-memory.md`, на который ссылается AGENTS.md, в проекте отсутствует — политика read/write применена по правилам из AGENTS.md напрямую.