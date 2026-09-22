The file `.ai-standards/code-review-report.md` is missing — the report shape falls back to the order specified in the rules. `rtk` compressed the diff too much, I'll look at the full one.
The key duplication candidate is confirmed. Checking whether the new feature is used anywhere, and whether there are any tests.
`formatPrice` isn't used anywhere, while `formatMoney` is already tested. I'll check whether the tests can be run for verification.
Проверка завершена: тесты запустить нельзя — vitest не установлен (нет `node_modules/` и lock-файла). Замечание о дублировании подтверждено чтением обоих файлов: `formatPrice` полностью повторяет существующую `formatMoney`.

Файл `.ai-standards/code-review-report.md` отсутствует — проект не запускал `ai-sync sync-templates`, поэтому отчёт собран по резервной форме из правил. Отчёт размещён в чате:

```markdown
ai-standards v2.5.0

## Код-ревью

### Что сделано
Добавлен новый файл `src/pricing.ts` с функцией `formatPrice(amount, currency)`: форматирование суммы в центах в строку вида `-€1,234.56` — символ валюты, знак, разбиение целой части по три цифры.

### Как сделано
Стиль кода согласован с проектом (явные типы на экспортируемой границе, `const`, шаблонные строки). Переиспользование при этом не выполнено: вместо существующей проверенной функции создан её полный дубль (см. находку ниже).

### Корректность
Не найдено.

### Архитектура и конвенции
Не найдено.

### Переиспользование
🟡 src/pricing.ts:1 — `formatPrice` полностью дублирует существующую `formatMoney` из src/money.ts:1: та же карта символов (EUR→€, GBP→£, остальное→$), обработка знака, деление на целую/дробную часть, группировка цифр и шаблон вывода дают идентичный результат; новая функция нигде не используется, при этом `formatMoney` уже покрыта тестами (test/money.test.ts) — нарушает: DRY (AGENTS.md).
Путь исправления: удалить `src/pricing.ts` и использовать `formatMoney` из `src/money.ts`; если нужна новая абстракция — расширять существующую функцию, а не клонировать её.

### Эффективность
Не найдено.

### Качество
Не найдено.

### Проверки
- Дублирование подтверждено чтением обоих файлов (src/pricing.ts, src/money.ts), вывод функций эквивалентен.
- `npm test` (vitest run) — упало: `vitest: not found`; зависимости не установлены (`node_modules/` и lock-файл отсутствуют), существующие тесты из test/money.test.ts не запускались.
- Проверка типов не выполнялась: tsconfig в проекте отсутствует.
```

`Dependencies` опущены — изменение самодостаточно. Отправка отчёта — по умолчанию в чат; в файл сохраню только по явной просьбе.