Примечание: файл `.ai-standards/references/features/review-lenses.md`, на который ссылается AGENTS.md, в проекте отсутствует (проверено поиском), поэтому обзор выполнен по описанию линз Reuse/Quality/Efficiency из AGENTS.md. Рецензируемый модуль — `src/pricing.ts`.

## Simplify review: src/pricing.ts

**Reuse (дублирование)**
- Валидация `if (price < 0) throw new Error('negative')` продублирована в обеих функциях (src/pricing.ts:2 и src/pricing.ts:7). По правилу DRY предлагается общий помощник, принимающий коэффициент скидки.

**Quality**
- Магические коэффициенты `0.5` и `0.7` (src/pricing.ts:3, src/pricing.ts:8) — заменить на именованные константы ставок.
- Сообщение об ошибке `'negative'` неинформативно; можно улучшить, но это изменение наблюдаемого поведения — менять только если никто не завязан на точный текст.

**Efficiency**
- Замечаний нет: функции тривиальны по стоимости.

**Предлагаемый рефакторинг** (публичный API из двух экспортов сохраняется, поведение не меняется):

```ts
const BLACK_FRIDAY_RATE = 0.5;
const CYBER_MONDAY_RATE = 0.7;

function applyDiscount(price: number, rate: number): number {
  if (price < 0) throw new Error('negative');
  return price * rate;
}

export function blackFriday(price: number): number {
  return applyDiscount(price, BLACK_FRIDAY_RATE);
}

export function cyberMonday(price: number): number {
  return applyDiscount(price, CYBER_MONDAY_RATE);
}
```

Итог: одна дублированная проверка вместо двух, именованные ставки, поведение и сообщения об ошибках без изменений.