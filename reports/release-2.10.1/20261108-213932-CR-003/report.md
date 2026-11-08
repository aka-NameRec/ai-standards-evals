vitest is unavailable in this environment (no node_modules; npx fallback fails on this Node version). I will verify the behavior with plain Node.js using the exact file logic.
Проверка окружения: `.ai-standards/code-review-report.md` и `.ai-standards/references/*` в проекте отсутствуют (шаблоны не развёрнуты через `ai-sync sync-templates`), поэтому использую резервную форму отчёта из правил. Ревью — текущий индексированный diff (`src/reader.ts`, +10 строк).

```markdown
ai-standards 2.10.1

## Задача
Code review индексированного изменения: `src/reader.ts` — добавлен `tryParseHeader` и doc-комментарий к `parseHeader`.

## Что сделано
- Добавлен `tryParseHeader(line): Header | null` — обёртка над `parseHeader`, возвращающая `null` вместо исключения.
- Добавлен doc-комментарий к `parseHeader`.

## Как сделано
- Обёртка реализована через `try/catch` вокруг существующего `parseHeader` без дублирования логики парсинга.

## Корректность
- 🔴 src/reader.ts:8 (pre-existing) — условие цикла `i <= lines.length` даёт итерацию за пределами массива: `parseHeader(lines[i])` получает `undefined`, и `readHeaders` бросает `TypeError: Cannot read properties of undefined (reading 'indexOf')` на любых входных данных (проверено в Node). Из-за этого тест test/reader.test.ts:6 не может пройти, а коммит bd1b930 («fix: tolerate trailing input in readHeaders») дефект не устранил — violates: Correctness / Completion Discipline (результат не проверен перед закрытием задачи).
- 🔵 src/reader.ts:27 — `tryParseHeader` глотает все исключения, а не только задокументированную ошибку «invalid header line» из `parseHeader`: `TypeError` от нестрокового входа тоже молча превращается в `null`, маскируя ошибки вызова — violates: General Engineering Principles (явная обработка ошибок; валидация входа на границе).
- Сам diff корректен: поведение `tryParseHeader` проверено для валидной строки, строки без `:` и `undefined` — соответствует doc-комментарию.

## Архитектура и конвенции
Не найдено.

## Переиспользование
Не найдено. `tryParseHeader` переиспользует `parseHeader` — дублирования нет.

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
- `npm test` (vitest) не выполним в этом окружении: `node_modules` отсутствует, `npx vitest` несовместим с установленной версией Node (Startup Error). Это среда, не код.
- Логика проверена напрямую в Node (точная копия функций файла): подтверждено, что `readHeaders` бросает `TypeError` на любом входе (корневая причина 🔴), и что `tryParseHeader` возвращает `null` для «bad»/`undefined` и корректный `Header` для «a: 1».
- Оставшийся риск: полный прогон тестового набора (vitest) не выполнен; после исправления 🔴 требуется `npm install && npm test`.
```

По политике `Fixing While Reviewing`: находка 🔴 — pre-existing, правка цикла выходит за пределы diff и ждёт явного запроса; находка 🔵 — опциональная. Дефектная строка — src/reader.ts:8, достаточно заменить `i <= lines.length` на `i < lines.length`.