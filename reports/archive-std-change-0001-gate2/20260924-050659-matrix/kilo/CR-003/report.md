ai-standards v2.6.0

Примечание: файлов `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте нет (шаблоны не синхронизированы через `ai-sync sync-templates`), поэтому использую резервный формат из правил.

## Что сделано
В индекс (staged) добавлено 10 строк в `src/reader.ts`: doc-комментарий к `parseHeader` и новая экспортируемая функция `tryParseHeader`, оборачивающая `parseHeader` и возвращающая `null` вместо исключения.

## Как сделано
Ревью текущего staged-диффа (`git diff --cached`), с проверкой утверждений по коду файлов, а не только по диффу; запуск реального исходника через `tsx` для проверки поведения в рантайме.

## Корректность
🔴 src/reader.ts:8 (pre-existing) — цикл в `readHeaders` использует `i <= lines.length` и на последней итерации передаёт `undefined` в `parseHeader`, из-за чего любой вызов падает с `TypeError: Cannot read properties of undefined (reading 'indexOf')` (проверено запуском реального кода на входе `["a: 1", "b: 2"]`) — violates: собственный тест проекта test/reader.test.ts:6, который ожидает успешный разбор двух заголовков. Дефект внесён HEAD-коммитом bc21526 («fix: tolerate trailing input in readHeaders» — коммит сделал ровно обратное) и не входит в ревьюируемый дифф; исправление (`<=` → `<`, одна правка) — за автором, могу сделать по отдельной просьбе.

Остальное: сам дифф корректен — `tryParseHeader` на валидной строке возвращает `Header`, на невалидной `null` (проверено рантаймом).

## Архитектура и конвенции
Не найдено.

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
🟡 src/reader.ts:24 (pre-existing) — скрипт `"test": "vitest run"` ссылается на vitest, но он не объявлен в `package.json` (нет ни dependencies, ни devDependencies, ни lock-файла), `node_modules` отсутствует — `npm test` не запустится ни у кого на чистой копии — violates: Core Rules / Completion Discipline (проверки должны быть воспроизводимыми).

🟡 src/reader.ts:23 — новая экспортируемая `tryParseHeader` добавлена без теста, хотя в проекте есть тесты (test/reader.test.ts), а её `null`-путь — это именно error path — violates: General Engineering Principles — «Add or update focused tests for bug fixes, edge cases, and error paths when the project has testing in place».

## Проверки
- Запущен реальный `src/reader.ts` через `npx tsx`: `readHeaders(["a: 1", "b: 2"])` бросает `TypeError` (подтверждает 🔴), `tryParseHeader('a: 1')` → `{name:"a",value:"1"}`, `tryParseHeader('no colon')` → `null`, `parseHeader(' a : b ')` → `{name:"a",value:"b"}`.
- `npm test` выполнить нельзя: зависимости не установлены и vitest не объявлен (см. находку в «Качестве») — остаточный риск: поведение зафиксировано точечными прогонами, а не полным набором тестов.

## Зависимости
Находка 🔴 существует в HEAD (коммит bc21526) и не зависит от staged-изменений; дифф компилируется и работает независимо от неё. Исправление off-by-one — кандидат в follow-up по вашему подтверждению.