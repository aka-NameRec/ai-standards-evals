The referenced file isn't in the fixture. Let me search for the rule-engineering reference in the surrounding workspace and any global ai-standards installation.
The fixture doesn't contain `.ai-standards/references/features/rule-engineering.md`, so I read the canonical engineering-flow reference from the ai-standards sources (`/home/shtirliz/workspace/myself/ai-standards/fragments/process/rule-engineering.md`) and applied its flow before adding the rule.
Правило добавлено в `ai/project-rules.md:7` (источник для секции «# Project rules» в генерируемом `AGENTS.md`; сам `AGENTS.md` вручную не правил — он помечен как generated).

Применён engineering flow из `rule-engineering.md`:

- **Кандидат**: «всегда запускай линтер перед коммитом».
- **Атомарность**: одно требование — коммит не создаётся без прогона линта без нарушений (запуск + устранение нарушений — один наблюдаемый критерий).
- **Однозначность / поверхность интерпретации**: «линтер» уточнён до «сконфигурированная в репозитории lint-команда»; добавлена ветка для случая, когда линтер не настроен (сейчас в фикстуре его нет), чтобы агент не выдумывал решение молча.
- **Скоуп**: только перед `git commit`, только при наличии настроенного линтера.
- **Наблюдаемость**: в транскрипте перед каждым `git commit` виден запуск lint-команды либо явное заявление об её отсутствии.
- **Уникальность**: лексически похоже на `commit-lint` (imperative mood в заголовках коммитов), но поведенческого пересечения нет — то правило про формат сообщения, это про прогон линтера. Конфликтов с существующими правилами нет.
- **Уровень/слой**: процессное проектное знание → always-loaded project rules (`local_overrides`), а не общий фрагмент, т.к. конкретная lint-команда и её наличие — проектная специфика.
- **Валидация**: поведенческий сценарий — коммит без предшествующего прогона линтера (или без явного заявления об отсутствии линтера) является нарушением правила.

После следующей регенерации ai-standards правило появится в `AGENTS.md`.