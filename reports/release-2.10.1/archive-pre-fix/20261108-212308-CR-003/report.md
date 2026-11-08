Дифф поэтапный — `src/reader.ts`: doc-комментарий к `parseHeader` и новая функция `tryParseHeader`. Замечаю подозрительную границу цикла в `readHeaders` (строка 8, `i <= lines.length`) — это код до диффа. Проверяю тестами.
vitest не установлен (в `package.json` нет зависимостей) — ставить зависимости и менять lock-файлы в рамках ревью не буду. Проверю логику напрямую через Node:
Ревью завершено. Отчёт:

```markdown
ai-standards v2.10.1

# Code Review

## Задача
Ревью текущего staged-диффа (`src/reader.ts`): doc-комментарий к `parseHeader`
и новая функция `tryParseHeader`.

## Что сделано
- Прочитан дифф (`git diff --cached`), файл `src/reader.ts` целиком, тесты
  `test/reader.test.ts`, `package.json`.
- Попытка запуска тестов (`npm test`) — не прошла: vitest не установлен.
- Поведение проверено выполнением JS-копии модуля через node (см. Проверки).

## Как сделано
Проверки выполнялись чтением кода и прямым исполнением функций; изменения кода
не вносились.

## Корректность
- 🔴 src/reader.ts:8 (pre-existing) — в `readHeaders` цикл идёт до
  `i <= lines.length`: на последней итерации `lines[i] === undefined`, и
  `parseHeader(undefined)` бросает `TypeError: Cannot read properties of
  undefined (reading 'indexOf')`. Функция падает на любом входе, включая
  `[]` и валидный `["a: 1", "b: 2"]` — существующий тест test/reader.test.ts:6
  не может проходить. Дефект внесён коммитом 5c2ce7a до данного диффа, поэтому
  помечен (pre-existing); граница цикла должна быть `i < lines.length`.
  Исправление — за автором, могу применить отдельным патчем по запросу.

## Архитектура и конвенции
- 🔵 src/reader.ts:27 — `catch` в `tryParseHeader` без фильтра перехватывает
  любые исключения, а не только ошибку «invalid header line». Сегодня
  `parseHeader` больше ничего не бросает, разницы в поведении нет, но при
  расширении `parseHeader` маскировка чужих ошибок станет реальной. Точнее —
  проверять сообщение/тип ошибки или выделить нероняющее ядро парсинга, общее
  для обеих функций.

## Переиспользование
Не найдено. `tryParseHeader` корректно переиспользует `parseHeader`, дублей нет.

## Эффективность
Не найдено.

## Качество
- 🟡 src/reader.ts:24 — новый экспортируемый `tryParseHeader` (обработка
  ошибочной ветки) не покрыт тестами; в проекте vitest уже используется
  (test/reader.test.ts) — violates: правило «Add or update focused tests for
  bug fixes, edge cases, and error paths when the project has testing in
  place».

## Проверки
- `npm test` — не выполняется: vitest не найден (см. Зависимости).
- Прямое исполнение JS-копии `src/reader.ts` (node 18): `readHeaders(["a: 1",
  "b: 2"])` и `readHeaders([])` — воспроизведён `TypeError`; `tryParseHeader`
  корректна (объект на валидной строке, `null` на `"no-colon"`).
- `tsc` не запускался: tsconfig и typescript в проекте отсутствуют.
- TypeScript не ловит дефект из Корректности: без `noUncheckedIndexedAccess`
  `lines[i]` типизируется как `string`, и передача `undefined` выглядит
  валидной.

## Зависимости
- 🟡 (pre-existing) package.json:5 — скрипт `test` ссылается на vitest, но
  зависимости (`vitest`, `typescript`) в package.json не объявлены; тестовая
  база не воспроизводится чистой установкой.
```

Главный итог: сам дифф корректен и мал, но в файле есть блокирующий дефект до диффа — `readHeaders` падает на любом входе из-за off-by-one в src/reader.ts:8. Исправить его (и добавить тесты для `tryParseHeader`) могу по вашей команде.