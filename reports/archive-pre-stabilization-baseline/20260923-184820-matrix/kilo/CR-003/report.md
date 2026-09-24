rtk сработал; vitest отсутствует (нет node_modules и зависимости в package.json) — проверю логику напрямую через node:
## Код-ревью

`ai-standards v2.6.0`

Файл `.ai-standards/code-review-report.md` в проекте отсутствует — шаблон отчёта не развёрнут (`ai-sync sync-templates` не запускался), поэтому использую резервный порядок разделов.

### Что сделано
В `src/reader.ts` добавлен JSDoc-комментарий к `parseHeader` и новая экспортируемая функция `tryParseHeader`, которая возвращает `null` вместо исключения при невалидной строке заголовка.

### Как сделано
`tryParseHeader` делегирует парсинг существующему `parseHeader`, не дублируя логику; стиль и JSDoc соответствуют остальному файлу, комментарии на английском.

### Корректность
- 🔴 src/reader.ts:8 — цикл в `readHeaders` идёт до `i <= lines.length` и на последней итерации передаёт `undefined` в `parseHeader` (`lines[i]` вне границ массива): любой вызов с непустым массивом падает с `TypeError: Cannot read properties of undefined (reading 'indexOf')`, в том числе зашитый в тест кейс `readHeaders(["a: 1", "b: 2"])` (test/reader.test.ts:6). Воспроизведено запуском этой логики в node: `THROWS: TypeError`. Должно быть `i < lines.length` — нарушает: TypeScript Stack «Treat optional properties and indexed access precisely; model absence explicitly instead of relying on loose object semantics» (существовало ранее — внесено коммитом e87e01b «fix: tolerate trailing input in readHeaders», который как раз и сломал границу цикла).
- 🟡 package.json:6 — объявлен скрипт `test: vitest run`, но vitest отсутствует и в зависимостях (нет `devDependencies`, нет lockfile, `npm test` падает с `vitest: not found`) — нарушает: собственный контракт проекта на запуск тестов; явного правила в проекте на это нет, отмечаю как несоответствие заявленного скрипта фактическому состоянию (существовало ранее).

### Архитектура и конвенции
Не найдено.

### Переиспользование
Не найдено.

### Эффективность
Не найдено.

### Качество
Не найдено.

### Проверки
- `git diff` / `git diff --cached` — изменение только в `src/reader.ts` (staged).
- Логика `readHeaders` воспроизведена в `node` один-в-один — подтверждён `TypeError` на валидном входе.
- `rtk npm test` — не выполним: `vitest: not found` (зависимости не объявлены). Полный набор тестов и typecheck не прогонялись (vitest и tsconfig в проекте отсутствуют); вывод о дефекте сделан по чтению кода и прямому воспроизведению.

### Зависимости
Изменение самодостаточно, внешних репозиториев не затрагивает.

---
Отчёт размещён в чате (внутрь fenced-блока), файлом не сохранялся. Оба замечания существовали до диффа; исправлять их не стал — по правилам ревью это остаётся на усмотрение автора, могу внести фикс (`i < lines.length` и добавление vitest в devDependencies) отдельным патчем по явному запросу.