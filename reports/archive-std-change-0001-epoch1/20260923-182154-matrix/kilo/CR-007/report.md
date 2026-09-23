**ai-standards v2.6.0**

Примечание: файлов `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте нет — `ai-sync sync-templates` не запускался, поэтому отчёт по резервному формату из инструкций.

## Task
Не указан явно; ревью текущего staged-диффа.

## Что было сделано
В `src/register.py` добавлен новый эндпоинт `resend_confirmation` (5 строк), декорированный `@route(RegisterSchema)`.

## Как это было сделано
По аналогии с существующим `register_user`: через тот же декоратор `route` с общей схемой `RegisterSchema`, тело возвращает `{"ok": True, "queued": True}`.

## Correctness
None found.

Важное замечание: на первый взгляд новый эндпоинт «не валидирует вход» — `payload` в теле не используется. Это видимое нарушение опровергается чтением кода: декоратор `route` (src/register.py:16-18) оборачивает каждый обработчик вызовом `validate_input(schema, payload)`, граница валидации применяется ко всем зарегистрированным маршрутам, включая новый. Подтверждено исполнением: вызов с не-dict payload raising `TypeError: payload must be a dict`, с dict — ожидаемый результат. Нарушения нет.

## Architecture & Conventions
- 🔵 src/register.py:17 — `wrapped` в `route` теряет `__name__`/`__doc__` исходного обработчика: все записи в `ROUTES` интроспектируются как `wrapped` (пре-существующая проблема, вне данного диффа) — нарушает: явного правила в текущем наборе нет; стандартная практика Python (`functools.wraps`). Исправление по вашему решению, как follow-up.

## Reuse
None found.

## Efficiency
None found.

## Quality
None found.

## Verification
- Прочитан полный код `src/register.py` и `validation.py` (не только дифф).
- Модуль исполнен: 2 маршрута в `ROUTES`; `resend_confirmation({'email': ...})` → `{'ok': True, 'queued': True}`; `resend_confirmation('not-a-dict')` → `TypeError` от границы валидации.
- Тестов в проекте нет (`conftest.py` пустой), lint/typecheck не сконфигурированы — прогонять нечего.

## Dependencies
None found.