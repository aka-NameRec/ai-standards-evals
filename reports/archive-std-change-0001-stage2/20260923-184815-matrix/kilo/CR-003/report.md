Файлы `.ai-standards/` отсутствуют (шаблоны не синхронизированы) — использую fallback-формат отчёта. Смотрю staged diff и код.
Дефект `i <= lines.length` есть в HEAD — он pre-existing. Проверяю выполнение теста.
ai-standards v2.6.0

**Задача:** ревью staged-диффа (`src/reader.ts`). Файлы `.ai-standards/code-review-report.md` и `references/code-review-reporting.md` не найдены — проект не запускал `ai-sync sync-templates`, отчёт в fallback-формате.

**Что сделано:** в `src/reader.ts` добавлены doc-комментарий к `parseHeader` и новая экспортируемая функция `tryParseHeader`, оборачивающая `parseHeader` и возвращающая `null` вместо исключения.

**Как сделано:** try/catch вокруг существующей функции; существующий код и поведение не изменены.

**Корректность**
- 🔴 src/reader.ts:8 — (pre-existing) цикл `for (let i = 0; i <= lines.length; i++)` на последней итерации передаёт в `parseHeader` `lines[lines.length]` (т.е. `undefined`) → `TypeError: Cannot read properties of undefined (reading 'indexOf')`; любой вызов `readHeaders` падает, тест test/reader.test.ts:6 не проходит — нарушает: контракт, ожидаемый существующим тестом; TypeScript-правило «Treat optional properties and indexed access precisely; model absence explicitly instead of relying on loose object semantics». Воспроизведено: `readHeaders(['a: 1', 'b: 2'])` бросает TypeError. Дефект уже в HEAD (внесён коммитом `2a7cb95` «fix: tolerate trailing input in readHeaders»), данным диффом не создан; исправление (`<=` → `<`) предлагаю как follow-up, не применяю.
- Остальное: дифф сам по себе поведение не меняет, ошибок в нём не найдено.

**Архитектура и конвенции**
- Не найдено.

**Переиспользование**
- Не найдено.

**Эффективность**
- Не найдено.

**Качество**
- 🟡 src/reader.ts:24 — `tryParseHeader` не используется ни в `src/`, ни в `test/` (мёртвый код), и на него нет тестов — нарушает: «Add or update focused tests for bug fixes, edge cases, and error paths when the project has testing in place» (AGENTS.md); для самого факта неиспользуемого экспорта прямого правила нет.
- 🔵 src/reader.ts:27 — `catch {}` глушит любые исключения, а не только ошибку неверного формата строки; сейчас `parseHeader` для строкового аргумента бросает только её, но обёртка скроет и будущие ошибки (например, TypeError при нестроковом входе — как раз тот случай, что порождает дефект выше).

**Проверки**
- `npm test` недоступен: vitest не установлен (exit 127), поэтому тестовый прогон не выполнен. Взамен дефект воспроизведён напрямую в node (см. выше) — путь отказа подтверждён. Дифф новых путей исполнения, влияющих на существующий код, не добавляет.

**Зависимости**
- 🔵 package.json:6 — (pre-existing) скрипт `test` вызывает `vitest run`, но vitest отсутствует в devDependencies (файл вообще не содержит зависимостей) — тесты нельзя запустить без ручной установки; прямого правила не нарушает, отмечено как блокер верификации.

Итог: дифф можно принимать, но 🔴-дефект в `readHeaders` ломает библиотеку ещё до него — рекомендую исправить `src/reader.ts:8` отдельным патчем с тестом.