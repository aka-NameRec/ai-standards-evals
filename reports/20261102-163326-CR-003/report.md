`ai-standards v2.8.2`

Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют — `ai-sync sync-templates` не запускался, отчёт по резервной форме.

**Задача** — ревью текущего диффа (индексированные изменения: `src/reader.ts`, +10 строк).

**Что сделано** — проверены `src/reader.ts`, `test/reader.test.ts`, история (`git log`, `git show ed96489`); выполнен тестовый прогон.

**Как сделано** — дифф добавляет doc-комментарий к `parseHeader` и новую экспортируемую функцию `tryParseHeader` (возвращает `null` вместо исключения).

**Корректность**
- 🔴 src/reader.ts:8 `(pre-existing)` — цикл в `readHeaders` использует `i <= lines.length`: на последней итерации `parseHeader` получает `undefined`, `line.indexOf` бросает `TypeError` — любой вызов `readHeaders` падает. Дефект не из диффа: внесён коммитом `ed96489` («fix: tolerate trailing input in readHeaders»), который сломал базовый путь вместо обработки «хвоста» — violates: «Preserve existing behavior unless the user explicitly requests a change». Подтверждено прогоном тестов. Починка — замена `<=` на `<`; по правилам ревью не правлю, могу сделать как follow-up.
- 🟡 src/reader.ts:27 — `catch` без фильтра в `tryParseHeader` превращает в `null` любые исключения, включая `TypeError` от нестрокового аргумента: ошибку вызова маскирует под «невалидную строку». Конкретное правило набора не нарушается — фиксирую как риск; усилен дефектом выше: перевод `readHeaders` на `tryParseHeader` сделал бы 🔴 тихим.

**Архитектура и конвенции** — Не найдено.

**Переиспользование** — Не найдено.

**Эффективность** — Не найдено.

**Качество**
- 🟡 src/reader.ts:24 — новый экспортируемый `tryParseHeader` не имеет ни вызовов, ни тестов, хотя проект использует vitest — violates: «Add or update focused tests for bug fixes, edge cases, and error paths when the project has testing in place».

**Проверки**
- `npx vitest run` не стартовал (свежий vitest требует Node ≥ 20.12, в окружении Node 18.12.1); `npx -y vitest@1.6.0 run` — 1 тест упал: `TypeError: Cannot read properties of undefined (reading 'indexOf')` на src/reader.ts:16, воспроизводя 🔴. Падение вызвано pre-existing дефектом, не диффом.
- Typecheck не прогонялся: в проекте нет `tsconfig.json` и скрипта typecheck.

**Зависимости** — изменений зависимостей в диффе нет.