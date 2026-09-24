Справочник `.ai-standards/references/basic-memory-operations.md` отсутствует — проект не запускал `ai-sync sync-templates`, действую по правилам из AGENTS.md. Проверю базу знаний на дубликаты перед созданием канонической заметки:
Дубликатов нет. Создаю заметку по форме существующей канонической заметки (датированный файл, frontmatter с русским `title`, заголовок `# `, секции `## Observations` и `## Relations`):
Заметка создана: `docs/decisions/2026-09-24-internal-services-grpc.md`.

- Форма по стандарту проекта: frontmatter с русским `title` (`type: decision`), заголовок `# `, повторяющий title, секции `## Observations` (категория `[fact]`, как в существующей заметке) и `## Relations` со ссылкой на `[[Модульный контракт auth]]`.
- Как solution-space заметка, содержит отклонённый вариант (сохранить REST/JSON) и принятые последствия (protobuf-контракты, кодогенерация, grpcurl вместо curl; публичные API вне области решения).
- Дубликатов в Basic Memory не найдено; справочный файл `.ai-standards/references/basic-memory-operations.md` в проекте отсутствует, поэтому действовал по правилам AGENTS.md. Файл не закоммичен — коммит по запросу.