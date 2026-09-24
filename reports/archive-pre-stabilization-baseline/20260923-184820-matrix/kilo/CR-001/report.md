Dependencies (typescript, vitest) are not installed in this fixture; I'll verify behavior by direct comparison in a scratch script instead.
Report shape file `.ai-standards/code-review-report.md` is absent, so I used the fallback order from the code-review rules. Report destination: chat.

```markdown
# Код-ревью

ai-standards v2.6.0

## Что сделано

Добавлен новый модуль `src/pricing.ts` с функцией `formatPrice(amount, currency)`:
форматирование суммы в центах в строку вида `$123.45` со знаком валюты, обработкой
отрицательных значений и группировкой тысяч.

## Как сделано

Изменение самодостаточно и размещено в новом файле с явными типами на публичной
границе. Переиспользования существующего кода нет — алгоритм переimplementован
локально (см. находку ниже).

## Корректность

Не найдено.

## Архитектура и конвенции

Не найдено.

## Переиспользование

🟡 src/pricing.ts:1 — `formatPrice` дублирует существующую `formatMoney`
из src/money.ts:1: тот же маппинг валют (`EUR→€`, `GBP→£`, остальное `$`),
знак минус, разделение на целую/дробную часть и группировка тысяч. Вывод
функций идентичен на 8 проверенных случаях (включая тестовые: `12345 USD`,
`-501 EUR`), а также `1000000 GBP`, `7 CHF`, `0 USD` — нарушает: DRY
(«Do not duplicate code»).
Путь рефакторинга: удалить `src/pricing.ts` (или сделать его ре-экспортом
`formatMoney`), а в местах вызова импортировать `formatMoney` из `../money`;
покрытие тестами у `formatMoney` уже есть (test/money.test.ts).

## Эффективность

Не найдено.

## Качество

Не найдено.

## Проверки

- Поведенческое сравнение `formatPrice` и `formatMoney` (node, 8 входных
  случаев, включая оба тестовых кейса): вывод идентичен.
- `npm test` не выполнены: vitest не установлен (`vitest: not found`);
  тесты для `pricing.ts` отсутствуют.
- `tsc --noEmit` не выполнен: typescript не установлен в проекте
  (запустился только npx-стаб «not the tsc command»).
```

Не найдено проверок, которые остались бы непокрытыми, кроме указанных: типизация и тесты не запускались из-за отсутствия установленных зависимостей (`npm install` + повторный запуск `npx tsc --noEmit` и `npm test` закроют этот пробел).