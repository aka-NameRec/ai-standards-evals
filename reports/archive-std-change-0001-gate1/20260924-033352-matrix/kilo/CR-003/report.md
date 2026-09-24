`.ai-standards/` не найден (проект не запускал `ai-sync sync-templates`) — использую fallback-формат отчёта. Смотрю staged-диф и код:
vitest не установлен (нет `node_modules` и vitest отсутствует в `devDependencies`). Проверяю дефект изолированно через node:
# Отчёт code review

`ai-standards v2.6.0`

Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (шаблоны не синхронизированы через `ai-sync sync-templates`) — отчёт в fallback-формате из AGENTS.md.

## Задача

Bare-запрос «code review»: ревью текущего diff (staged: `src/reader.ts`, +10 строк).

## Что сделано

Ревью проведено по коду, а не только по диффу: прочитаны `src/reader.ts`, `test/reader.test.ts`, `package.json`, история коммитов. Новое в диффе: doc-комментарий к `parseHeader` и новая экспортируемая функция `tryParseHeader` (src/reader.ts:24), оборачивающая `parseHeader` в try/catch и возвращающая `null` вместо исключения.

## Как сделано

Порядок проверок: Корректность → Архитектура и конвенции → Переиспользование → Эффективность → Качество. Дефект в нетронутом диффом коде воспроизведён изолированным запуском логики в node.

## Корректность

- 🔴 src/reader.ts:8 `(pre-existing)` — цикл `for (let i = 0; i <= lines.length; i++)` выходит за границы массива: на последней итерации `lines[i]` равен `undefined`, и `parseHeader(undefined)` падает с `TypeError: Cannot read properties of undefined (reading 'indexOf')` в src/reader.ts:16. Функция `readHeaders` таким образом падает на любом входе, включая существующий тест test/reader.test.ts:6. Вероятно, внесена коммитом `5fc3d75` («fix: tolerate trailing input in readHeaders»), который должен был давать обратный эффект. Исправление — `i < lines.length`. — violates: корректность (границы цикла); поведение существующего публичного API нарушено
- 🟡 src/reader.ts:24 — новая экспортируемая функция `tryParseHeader` (включая ветку ошибки) не покрыта тестами, при том что тестовая инфраструктура в проекте есть (test/reader.test.ts, vitest). — violates: правило проекта «Add or update focused tests … when the project has testing in place»

Остальное в диффе корректно: `tryParseHeader` ловит единственный сценарий ошибки `parseHeader` (отсутствие `:`) и возвращает `null` согласно контракту.

## Архитектура и конвенции

Не найдено.

## Переиспользование

Не найдено. `tryParseHeader` переиспользует `parseHeader`, дублирования нет.

## Эффективность

Не найдено.

## Качество

Не найдено.

## Проверки

- `npm test` не выполняется: `vitest: not found` — vitest отсутствует в `node_modules` и не объявлен в `package.json` (нет `devDependencies`, нет lockfile). Это ограничение окружения, отдельной находкой не счёл.
- Дефект из находки 🔴 подтверждён изолированным воспроизведением логики в node: `readHeaders(['a: 1', 'b: 2'])` бросает `TypeError` вместо возврата двух заголовков.
- Сам дифф (+10 строк) проверен чтением; запустить тесты для него невозможно до починки окружения (см. выше).

## Зависимости

Не найдено.

Дифф сам по себе можно коммитить; находка 🔴 — pre-existing и на этот diff не указывает, исправление оставляю на решение автора (могу внести как follow-up по явной просьбе).