`ai-standards v2.6.0`

Примечание: `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (sync-templates не запускался) — отчёт по fallback-форме. Ревью — staged diff (`src/reader.ts`, +10).

## Что сделано
Добавлен doc-комментарий к `parseHeader` и новая экспортируемая функция `tryParseHeader` (src/reader.ts:24), возвращающая `null` вместо исключения.

## Как сделано
`tryParseHeader` оборачивает `parseHeader` в `try/catch`; при исключении возвращает `null`. Код прочитан целиком, не только diff.

## Корректность
- 🔴 (pre-existing) src/reader.ts:8 — условие `i <= lines.length` даёт лишнюю итерацию: `lines[i]` равен `undefined`, и `parseHeader` падает с `TypeError: Cannot read properties of undefined (reading 'indexOf')`, поэтому `readHeaders` бросает исключение на любом непустом входе — нарушает: контракт функции (возврат `Header[]`), зафиксированный существующим тестом test/reader.test.ts:6, который из-за этого падает.
- В самом diff нарушений корректности: Не найдено. (`tryParseHeader` проверен чтением — семантика соответствует объявленной.)

## Архитектура и конвенции
Не найдено.

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
- 🔵 src/reader.ts:24 — новый экспорт `tryParseHeader` не покрыт тестом — нарушает: правило проекта «Add or update focused tests … when the project has testing in place» (тесты в проекте есть: test/reader.test.ts).

## Проверки
- Дефект из Корректности воспроизведён: тот же код `readHeaders`/`parseHeader` выполнен через node — `readHeaders(["a: 1","b: 2"])` бросает `TypeError: Cannot read properties of undefined (reading 'indexOf')`.
- `npm test` не выполним: vitest не установлен (exit 127) — полный прогон тестов не проводился; риск: автотестами сценарии не подтверждены.
- Исправления по итогам ревью не вносились; статус git-индекса не менялся.

## Зависимости
- 🟡 (pre-existing) package.json:6 — скрипт `test` требует vitest, но он не объявлен в `dependencies`/`devDependencies`, `node_modules` отсутствует — нарушает: явного правила в AGENTS.md нет; практически это блокирует воспроизводимый запуск `npm test` (см. Проверки).

Исправление 🔴 (замена `<=` на `<` в src/reader.ts:8) — однострочное и подтверждаемое чтением; вносится только по вашей явной просьбе, поскольку дефект существовал до diff.