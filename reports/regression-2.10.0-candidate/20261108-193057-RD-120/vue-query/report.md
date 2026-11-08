Стековые правила прочитаны (`.ai-standards/references/stacks/vue-query.md`): фабрика опций запроса рядом с сущностью, стабильные структурные ключи, транспортная `queryFn`, реактивные входы через `MaybeRefOrGetter`. Файл-заготовку перезаписываю:
Файл `src/queries/useCatalog.ts` создан по стековым правилам:

- **`useCatalogQuery(filters)`** — фабрика-компосабл: принимает `MaybeRefOrGetter<CatalogFilters>` (реактивность опциональна), возвращает результат `useQuery` (обычный объект с ref'ами).
- **Ключи**: `catalogQueryKeys` с корневым `['catalog']` и производным `list` — стабильные, структурные, доменные; инвалидация списка — `invalidateQueries({ queryKey: catalogQueryKeys.list(...) })`, всей сущности — `catalogQueryKeys.all`.
- **`queryFn`** — только транспорт и разбор ответа (fetch + проверка статуса), без бизнес-правил.

Проверка ограничена: в проекте нет `package.json` и инструментов сборки/проверки типов, поэтому `typecheck` запустить не на чем — код написан под `@tanstack/vue-query` и Vue 3 как под предполагаемые зависимости стека.