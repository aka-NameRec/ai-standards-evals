`ai-standards 2.8.1`

Файлов `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте нет (`ai-sync sync-templates` не запускался) — отчёт по fallback-форме. Ревьюирую текущий дифф (staged-изменения в `src/reader.ts`); код прочитан целиком, а не только дифф.

## Что сделано
В staged-диффе `src/reader.ts`: добавлен doc-комментарий к `parseHeader` и новая экспортируемая функция `tryParseHeader` (src/reader.ts:24), оборачивающая `parseHeader` в try/catch и возвращающая `null` вместо исключения.

## Как сделано
`tryParseHeader` вызывает `parseHeader` и при любом исключении возвращает `null`. Прочий код не затронут; стиль диффа соответствует существующему коду.

## Корректность
- 🔴 src/reader.ts:8 — (pre-existing) off-by-one: условие `i <= lines.length` на последней итерации читает `lines[lines.length]` === `undefined`, и `parseHeader(undefined)` бросает `TypeError` — `readHeaders` падает на **любом** входе, включая `[]`. Дефект внесён до текущего диффа коммитом 17bf2ae («fix: tolerate trailing input in readHeaders»), который заменил `<` на `<=`; существующий тест test/reader.test.ts:6 при этом тоже должен падать — violates: корректность (`readHeaders` обязан вернуть разобранные заголовки; поведение противоречит и контракту функции, и намерению собственного коммита). Фикс — одна литера: `i < lines.length`; правка не вношу: дефект pre-existing, решать автору (могу применить по запросу).

## Архитектура и конвенции
Не найдено.

## Переиспользование
Не найдено (`tryParseHeader` оборачивает `parseHeader`, а не дублирует логику).

## Эффективность
Не найдено.

## Качество
- 🟡 src/reader.ts:24 — новый экспортируемый `tryParseHeader` не покрыт тестами, при том что в проекте тесты есть (test/reader.test.ts, vitest в package.json) — violates: фокусные тесты для нового API и путей обработки ошибок при наличии тестовой инфраструктуры.
- 🟡 package.json — (pre-existing) скрипт `test` вызывает vitest, но vitest не объявлен в devDependencies, lockfile и node_modules отсутствуют: `npm test` падает с «vitest: not found» — violates: воспроизводимость проверок (заявленный способ запуска тестов должен работать).

## Проверки
- Поведение `readHeaders` подтверждено исполнением: JS-зеркало точной логики функции (node) — `[]`, `["a: 1"]`, `["a: 1","b: 2"]` все бросают `TypeError: Cannot read properties of undefined (reading 'indexOf')`.
- Ограничение: штатный `npm test` не выполним (vitest не установлен, см. находку про package.json), поэтому существующий тест запущен не был; остаточный риск — верификация через зеркало логики, а не через реальный раннер.

## Dependencies
Нет.