Обёртка freshness-gate — это `.ai-standards/scripts/code_index.py` (`code-query` сначала обновляет, потом запрашивает). Поскольку индекс устарел (`index-stale.marker`), я запрошу данные через него:
Индекс обновлён через обёртку (fresh). По правилу chroma.md семантика сужает область, но не доказывает полноту — дополняю точным поиском:
Семантический поиск (через freshness-gate обёртку `.ai-standards/scripts/code_index.py code-query`, индекс обновлён перед запросом) и точный поиск сходятся — в коде обрабатывается/определяется таймаут запроса только в одном месте:

- **src/timeouts.py:4** — `read_timeout()` (30 сек)
- **src/timeouts.py:8** — `connect_timeout()` (10 сек)

Совпадение в AGENTS.md (строка 52) и `.ai-standards/state/manifest.json` — это документация и служебный манифест индекса, не код.