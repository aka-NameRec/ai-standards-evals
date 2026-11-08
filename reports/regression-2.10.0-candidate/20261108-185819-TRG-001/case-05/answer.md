The staged diff contains two new files. Let me read them from disk and verify they compile.
No TypeScript compiler is available locally. I'll smoke-test the runtime logic of both functions with Node instead.
Both files reviewed against all passes. Here is the report (destination: chat, fenced Markdown block).

```markdown
## Код-ревью

ai-standards 2.9.0

### Что сделано
Добавлены два новых экспортируемых модуля: `src/greet.ts` с функцией приветствия и `src/volume.ts` с функцией приведения текста к верхнему регистру.

### Как сделано
`greet` оформлена как function declaration, `shout` — как стрелочная `const`; оба экспорта имеют явные типы параметров и возвращаемого значения на границе модуля, что соответствует правилам TypeScript-стека. Внешних зависимостей нет.

### Корректность
- Не найдено.

### Архитектура и конвенции
- Не найдено.

### Переиспользование
- Не найдено.

### Эффективность
- Не найдено.

### Качество
- Не найдено.

### Проверки
- runtime-смоук обоих функций через Node 18 (эквивалентный JS без типов) — логика подтверждена, включая пустые строки (`"Hello, !"` и `""` не бросают исключений)
- проверка типов (tsc) — не выполнялась: в проекте нет tsconfig/package.json, компилятор TypeScript локально недоступен, `npx typescript` не отработал
```