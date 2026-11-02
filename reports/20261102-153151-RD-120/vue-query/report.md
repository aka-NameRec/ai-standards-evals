Стековые правила прочитал (`.ai-standards/references/stacks/vue-query.md` + сводка из AGENTS.md: серверное состояние — только через кэш TanStack Query, стабильные доменные ключи, Composition API, явные типы). Целевой файл — заглушка-«пробник», перезаписываю его.
Файл `src/queries/useCatalog.ts` готов. Что внутри:

- **`useCatalogQuery(filters?)`** — фабрика запроса: принимает `MaybeRefOrGetter<CatalogFilters>`, возвращает результат `useQuery` (Composition API, реективные фильтры поддержаны).
- **`catalogQueryOptions(filters?)`** — фабрика `queryOptions` с ключом `['catalog', normalizedFilters]`: ключ доменно-осмысленный и стабильный (нормализация отсекает `undefined`/пустые значения, `computed` отслеживает изменения фильтров), пригоден для инвалидации по `['catalog']`.
- Синхронизация серверного состояния только через кэш TanStack Query — локальных дублирующих `ref`-ов состояния нет; типы контрактов (`CatalogItem`, `CatalogFilters`) объявлены явно.

Проверка ограничена: в проекте нет `package.json`, `tsconfig` и установленных зависимостей, поэтому запустить typecheck/lint и компиляцию нельзя. Отмечаю остаточный риск: типы `@tanstack/vue-query` и `vue` не верифицированы компилятором — при появлении зависимостей стоит прогнать typecheck.