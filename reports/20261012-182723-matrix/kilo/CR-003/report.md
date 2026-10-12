`ai-standards v2.8.2`

Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (`ai-sync sync-templates` не запускался) — использую резервный формат из инструкций.

## Что сделано
В индексе один файл: `src/reader.ts` — добавлен doc-комментарий к `parseHeader` и новая экспортируемая функция `tryParseHeader`, оборачивающая `parseHeader` в try/catch и возвращающая `null` вместо исключения.

## Как сделано
`tryParseHeader` (src/reader.ts:24-30) повторно использует `parseHeader`, перехватывает любое исключение и возвращает `null`. Новых зависимостей нет.

## Корректность
- 🔴 src/reader.ts:8 — (pre-existing) условие цикла `i <= lines.length` даёт лишнюю итерацию, где `lines[i] === undefined`, и `parseHeader(undefined)` падает с `TypeError: Cannot read properties of undefined (reading 'indexOf')` — `readHeaders` бросает исключение на любом входе, включая кейс из test/reader.test.ts:6 — нарушает: контракт функции, который фиксирует тест (ожидается массив из двух заголовков). Дефект внесён коммитом d42b2f7 «fix: tolerate trailing input in readHeaders» (замена `<` на `<=`). Вне диффа, поэтому не исправляю — могу сделать follow-up патч (`i < lines.length`) по вашей команде.
- 🔵 src/reader.ts:27 — `catch {}` без типа глотает в том числе `TypeError` для нестрокового аргумента, маскируя ошибку вызова как «невалидную строку» — нарушает: явная модель ошибок; правило не закреплено явно, помечаю как опциональное замечание.

## Архитектура и конвенции
- 🟡 src/reader.ts:24 — `tryParseHeader` экспортирована, но в репозитории нет ни одного вызова и ни одного теста на неё — нарушает: AGENTS.md «Add or update focused tests … when the project has testing in place» (vitest в проекте есть).

## Переиспользование
Не найдено.

## Эффективность
Не найдено.

## Качество
Не найдено.

## Проверки
- Дефект `readHeaders` подтверждён прогоном точной копии кода в node: `readHeaders(["a: 1", "b: 2"])` бросает `TypeError`.
- `npx vitest run` не выполнился в этом окружении: vitest 5 требует Node ≥ 20 (`styleText` отсутствует в node:util на Node 18.12.1), поэтому тестовый набор не запускался — верификация частичная, остаточный риск: поведение тестов не подтверждено прогоном.
- `tsc` недоступен, скрипт typecheck в package.json отсутствует — типы не проверялись.

## Зависимости
Не найдено.