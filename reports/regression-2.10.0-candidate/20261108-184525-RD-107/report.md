Скилл `capture-knowledge` в этой сессии не загружается, поэтому действую по маршруту из справочника `.ai-standards/references/features/knowledge-capture.md`: запись решения, запись задачи, пары `.ru.md` для всего в `docs/`, ссылки в README. Фича `project-memory` в манифесте не включена, поэтому `docs/local/**` не создаю.
Знания зафиксированы по маршруту из `.ai-standards/references/features/knowledge-capture.md`:

- **Решение** (принятый выбор: константы ретраев в `src/payments/retry.py`, backoff ≤ 5 попыток): `docs/decisions/2026-11-08-retry-backoff-cap.md`
- **Запись о задаче** (каркас цикла ретраев, проверка `uv run pytest`): `docs/tasks/2026-11-08-retry-loop-skeleton.md`
- **Пары `.ru.md`** созданы для обеих записей и для существующего `docs/session-notes.md`
- **README.md** дополнен ссылками на поддерживаемые документы

Пропущено по правилам: контракты модулей (в.fixture нет кода/крупных модулей) и `docs/local/**` (фича `project-memory` не включена в `ai.project.toml`). Коммит не делал — не запрашивался.