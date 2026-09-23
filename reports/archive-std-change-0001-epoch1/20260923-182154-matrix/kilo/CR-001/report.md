**ai-standards v2.6.0**

Примечание: `.ai-standards/code-review-report.md` и `.ai-standards/references/code-review-reporting.md` в проекте отсутствуют (похоже, `ai-sync sync-templates` не запускался), поэтому отчёт собран по резервному порядку разделов из AGENTS.md.

## Что сделано
В индекс подготовлен новый файл `src/pricing.ts` (14 строк) — функция `formatPrice(amount, currency)` для форматирования денежной суммы (в центах) с символом валюты и группировкой разрядов.

## Как сделано
Ручная таблица символов валют, `Math.abs`/`Math.floor` для целой и дробной части, посимвольный цикл для группировки запятыми, шаблонная строка с суффиксом `.frac`.

## Correctness
None found. (Проверил `formatPrice` и существующий `formatMoney` на совпадающих входах: `(-501, "EUR")` → `-€5.01`, неизвестная валюта → `$` — поведение идентичное.)

## Architecture & Conventions
None found.

## Reuse
- 🟡 `src/pricing.ts:1` — `formatPrice` полностью дублирует уже существующий и покрытый тестами `formatMoney` из `src/money.ts:1` (та же конвертация центов, символы валют, отрицательные суммы, группировка; отличается только ручной цикл вместо regex и имя параметра `amount` вместо честного `cents`) — violates: DRY («Do not duplicate code» / «If duplication is detected... propose a refactoring path»). Путь рефакторинга: удалить `src/pricing.ts`, при необходимости добавить нужное имя/поведение внутри `src/money.ts`, тесты уже есть в `test/money.test.ts`. Дифф проверен по коду обоих файлов, не по догадке.

## Efficiency
None found.

## Quality
- 🔵 `src/pricing.ts:2` (pre-existing по сути: паттерн из `src/money.ts:2`) — цепочка тернарников для символа валюты нечитаема и плохо расширяется; при удалении дубля уходит вместе с ним — violates: General Engineering Principles («Use meaningful names», «Replace magic values with named constants»).

## Verification
Прочитал `src/pricing.ts`, `src/money.ts`, `test/money.test.ts`, `package.json`; сверил вывод двух функций вручную на 3 кейсах; убедился, что `src/pricing.ts` пока никем не импортируется. Тесты и typecheck не запускались (в `package.json` нет отдельных скриптов, и новый файл в прогон не входит) — риск: вывод функций сверялся только вручную.

## Dependencies
- 🔵 `package.json:6` (pre-existing) — скрипт `test: "vitest run"` ссылается на vitest, но он не объявлен в `devDependencies`, и `node_modules` в проекте нет — тесты не запустятся без ручной установки — violates: General Engineering Principles («Verify information», воспроизводимость тестового прогона).