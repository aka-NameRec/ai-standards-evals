Алиас добавлен в `vite.config.ts`:

```ts
import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'

export default defineConfig({
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
```

По стековым правилам Vite (`.ai-standards/references/stacks/vite.md`):
- конфиг ограничен сборкой/алиасами/плагинами — правка в рамках правила;
- алиас задан через `import.meta.url`, без зависимости от окружения;
- правило о согласованности алиасов между Vite и TypeScript: в проекте нет `tsconfig.json`, поэтому соответствующий `paths` добавить некуда — при его появлении нужно продублировать `@/* -> src/*` там же.