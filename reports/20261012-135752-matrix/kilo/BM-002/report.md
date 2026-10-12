The reference file is absent (the project has not run `ai-sync sync-templates`), so I will follow the main rules. According to the synchronization hygiene rule: after a pull with mass renames, sync health must be checked and an explicit re-index performed before relying on the notes.
The `bm` CLI is available (`ai-sync` is missing — which is consistent with the absence of a reference file). Following the hygiene rule, I will check sync health and reindex before relying on the notes.
Сначала по гигиене синхронизации: после pull с массовыми переименованиями выполнил `bm doctor` (пройден), `bm orphans` (сирот нет) и явный `bm reindex` (индекс проекта `main` показывает 0 наблюдаемых файлов — проект в этом воркспейсе фактически не проиндексирован, поэтому отвечаю по прямому чтению файлов из `docs/`, а не по поиску индекса).

По заметкам — `docs/decisions/ADR-0007.md` («Подход к записи аудита»):

- Аудит-записи пишутся **только append-only** в `audit_log`;
- обязательные поля: `actor`, `action`, `target` и время в формате ISO;
- ретракция — **отдельной компенсирующей записью**; удаление записей запрещено.

Смежная заметка `docs/notes/audit-retention.md` («Хранение аудита») дополняет: срок хранения аудита — 3 года.