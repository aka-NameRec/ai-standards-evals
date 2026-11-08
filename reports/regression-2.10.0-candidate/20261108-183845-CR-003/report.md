`ai-standards v2.9.0`

Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/*.md` в проекте не найдены (шаблоны не развернуты через `ai-sync sync-templates`) — отчёт в fallback-формате.

**Задача:** bare-запрос «code review» — ревью текущего diff (staged: `src/reader.ts`).

**Что сделано**
- В `src/reader.ts` добавлена doc-комментарий к `parseHeader` и новая экспортируемая функция `tryParseHeader` (возвращает `null` вместо броска).

**Как сделано**
- `tryParseHeader` оборачивает `parseHeader` в `try/catch`; логика `parseHeader` не менялась.

**Корректность**
- 🔴 (pre-existing) src/reader.ts:8 — цикл `i <= lines.length` выходит за границы массива: на последней итерации `lines[i]` равен `undefined`, и `parseHeader` падает с `TypeError: Cannot read properties of undefined (reading 'indexOf')`. Функция `readHeaders` падает на любом входе, включая кейс из test/reader.test.ts:6 — то есть существующий тест красный. Дефект присутствует уже в HEAD (коммит `b5d2dbc`), в текущий diff не входит — поэтому не исправляю, решение за автором (фикс — заменить `<=` на `<`). — violates: контракт самой функции `readHeaders` (должна вернуть распарсенные заголовки); конкретное правило из свода не назначено.
- 🔵 src/reader.ts:27 — `catch {}` в `tryParseHeader` глотает любые исключения (включая случайные `TypeError`), маскируя ошибки под `null`; отличить «невалидную строку» от бага невозможно, т.к. `parseHeader` бросает generic `Error`. — violates: назначенного правила нет; отмечено как риск.

**Архитектура и конвенции**
- Не найдено.

**Переиспользование**
- 🔵 src/reader.ts:24 — `tryParseHeader` экспортирована, но не имеет ни вызовов, ни тестов в репозитории. — violates: назначенного правила нет; отмечено как неживая добавленная поверхность API.

**Эффективность**
- Не найдено.

**Качество**
- Не найдено.

**Проверки**
- Поведение проверено запуском JS-копии логики (node 18, типы сняты вручную): `readHeaders(["a: 1", "b: 2"])` бросает `TypeError`, `readHeaders([])` — тоже; `tryParseHeader("a: 1")` → `{name:"a",value:"1"}`, `tryParseHeader("garbage")` → `null`. Вывод о дефекте в строке 8 подтвержден.
- `npm test` не выполнен: vitest не установлен (`node_modules` отсутствует, в package.json нет devDependencies) — тесты запустить в текущем окружении нельзя; это заявленный остаточный риск.
- `tsc`/линтер в проекте не настроены — прогон невозможен.

**Зависимости**
- Не менялись.