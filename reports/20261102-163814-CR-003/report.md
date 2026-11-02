The diff is staged in `src/reader.ts`. Before writing findings, I'll verify behavior by running the project's tests.
No dependencies declared in package.json, so vitest can't run. I'll verify the exact module logic with plain Node instead.
**ai-standards v2.8.2**

## Задача
Bare-запрос «code review»: ревью текущего staged-диффа — `src/reader.ts` (unit-тесты не проходили мимо этого скоупа).

## Что сделано
- Добавлена JSDoc-строка к `parseHeader` (src/reader.ts:14).
- Добавлена новая экспортированная функция `tryParseHeader` (src/reader.ts:24–30), оборачивающая `parseHeader` в try/catch и возвращающая `null` вместо исключения.

## Как сделано
- `tryParseHeader` переиспользует `parseHeader`, собственной логики парсинга не дублирует. Существующий код не изменён.

## Корректность
- 🔴 src/reader.ts:8 (pre-existing) — `readHeaders` использует условие `i <= lines.length`, из-за чего на последней итерации в `parseHeader` передаётся `undefined` и функция бросает `TypeError: Cannot read properties of undefined (reading 'indexOf')`; функция падает на любом входе, включая `[]`, и существующий тест (test/reader.test.ts:6) не может проходить. Проверено исполнением, не по диффу: `readHeaders(["a: 1", "b: 2"])` бросает TypeError. — violates: базовая корректность (out-of-bounds доступ; условие должно быть `i < lines.length`). Строка не входит в дифф, поэтому не списывается на это изменение; однострочный фикс может быть применён по вашей команде как follow-up.
- 🟡 src/reader.ts:24 — новый экспортированный `tryParseHeader` (error-path-функция) не покрыт тестами, при том что тестовый набор в проекте есть (test/reader.test.ts). — violates: AGENTS.md «Add or update focused tests for bug fixes, edge cases, and error paths when the project has testing in place».
- 🔵 src/reader.ts:27 — `catch {}` без фильтра проглатывает любые исключения, а не только ошибку парсинга: `tryParseHeader(undefined)` молча возвращает `null` (проверено), маскируя программные ошибки (в т.ч. тот самый дефект из `readHeaders`) под «невалидную строку». — violates: формального правила нет; опциональное замечание по надёжности — можно проверять `line.indexOf(":") === -1` напрямую вместо try/catch.

## Архитектура и конвенции
Не найдено. (Типы на экспортируемой границе явные, нейминг с префиксом `try` и JSDoc соответствуют стилю.)

## Переиспользование
Не найдено. (Дублирования нет — обёртка переиспользует `parseHeader`.)

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
- `npm test` не выполнился: `vitest: not found` — в package.json нет `devDependencies`, vitest не объявлен, node_modules отсутствует. Реальный прогон тестового набора невозможен в текущем состоянии репозитория (pre-existing, environment).
- Логика проверена дословной репликацией `src/reader.ts` в node (типы сняты): `readHeaders(["a: 1","b: 2"])` → TypeError (подтверждает 🔴); `tryParseHeader("a: 1")` → `{name:"a",value:"1"}`; `tryParseHeader("nope")` → `null`; `tryParseHeader(undefined)` → `null` (подтверждает 🔵).
- Остаточный риск: поведение реального TS-модуля под vitest напрямую не прогонялось, т.к. окружение не собирается без установки зависимостей.

Скрипты lint/typecheck в проекте отсутствуют (package.json содержит только `test`).