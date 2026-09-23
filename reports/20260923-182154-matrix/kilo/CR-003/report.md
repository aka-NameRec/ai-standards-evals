Проект не запускал `ai-sync sync-templates` (`.ai-standards/` отсутствует) — использую резервную форму отчёта. Проверяю предполагаемый дефект тестами:
`vitest: not found` — это не сбой rtk, а отсутствие установленных зависимостей. Устанавливаю и повторяю:
Node 18 без strip-types — проверяю логику через JS-репликацию:
# Отчёт code review — ai-standards v2.6.0

Файлы `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` отсутствуют — проект не запускал `ai-sync sync-templates`, отчёт по резервной форме.

**Task**: bare-запрос «code review» — ревью текущего diff (staged-изменения, файл `src/reader.ts`).

**Что сделано (в diff)**: добавлен JSDoc к `parseHeader` и новая функция `tryParseHeader` (возвращает `null` вместо исключения).

**Как выполнялось**: чтение кода (не только diff), попытка прогона тестов, репликация логики на чистом JS для подтверждения корневой причины.

## Correctness

- 🔴 (pre-existing) `src/reader.ts:8` — цикл `readHeaders` использует условие `i <= lines.length`, поэтому на последней итерации `parseHeader(lines[i])` получает `undefined` и функция падает с `TypeError` на любом непустом входе; должно быть `i < lines.length` — нарушает: корректность (функция неработоспособна; тест `test/reader.test.ts:6`, ожидающий успешный парсинг, не может пройти). Проверено: `readHeaders(['a: 1', 'b: 2'])` → `TypeError: Cannot read properties of undefined (reading 'indexOf')`. Дефект существовал до diff: staged-изменения не трогают цикл. Связь с diff: `tryParseHeader` («не бросает исключений») добавлен рядом, тогда как основной потребитель `parseHeader` сломан этой ошибкой на единицу.
- 🟡 `src/reader.ts:24` — новый экспорт `tryParseHeader` не покрыт тестами, хотя vitest-набор в проекте есть (`test/reader.test.ts`): не проверены ни успешный путь, ни путь «невалидная строка → `null`» — нарушает: «Add or update focused tests for … error paths when the project has testing in place».
- 🟡 (pre-existing) `package.json:6` — скрипт `test` вызывает `vitest`, но vitest не объявлен в `dependencies`/`devDependencies`; `npm test` завершается «vitest: not found» — нарушает: воспроизводимость тестов из манифеста. Это помешало верификации данного diff тестами.

## Architecture & Conventions

Не найдено. Новая функция следует существующему стилю, типизация корректна.

## Reuse

Не найдено. `tryParseHeader` переиспользует `parseHeader`, дублирования нет.

## Efficiency

Не найдено.

## Quality

Не найдено.

## Verification

- `npm test` — падает: `vitest: not found` (зависимость отсутствует в манифесте).
- Корневая причина дефекта `readHeaders` подтверждена репликацией точной логики в node: вход `['a: 1', 'b: 2']` бросает `TypeError`.
- Правки в код не вносились: замена `<=` → `<` требует прогона тестов для подтверждения, а набор сейчас не запускается — по политике сообщается, а не применяется.

## Dependencies

Для закрытия: (1) `src/reader.ts:8`: `<=` → `<`; (2) добавить vitest в devDependencies; (3) тесты на `tryParseHeader`. Могу применить всё одним патчем по запросу.