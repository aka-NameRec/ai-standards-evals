The task selector BL-1020 resolves to commit `2e03cab` on develop. Now I'll examine the history, divergence, and the target state of staging.
Both commit diffs are byte-identical (same source blob `6d41d7b` → same result blob `fecdbbf`). I'll verify the surrounding state — consumers of `format_money`, tests, and the staging-only commit — before issuing the verdict.
## Вердикт: STOP — `ALREADY_PRESENT` — перенос не требуется

Эквивалентное изменение уже присутствует в `staging` под другим SHA; выполнить cherry-pick повторно нельзя без создания дубликата.

### Разрешение селекторов
| Параметр | Значение |
|---|---|
| Источник | ветка `develop` (локальный репозиторий) |
| Цель | ветка `staging`, HEAD `162e359` |
| Селекторы | задача `BL-1020`, заявленно «один коммит» |
| Результат | ровно один коммит `2e03cab` — соответствует заявленному объёму, подтверждаю как зафиксированный список |
| Merge-base | `24ea71a` |

### Подтверждённый список
1. `2e03cab` — `BL-1020: fix format_money for negative amounts` — `money.py`: обработка отрицательных сумм в `format_money`.

### Проверенные факты
- **FACT**: diff `2e03cab` и diff `162e359` (`hotfix: correct format_money rounding for negative invoices`, staging) байт-в-байт идентичны: одинаковый исходный блоб `6d41d7b` → одинаковый результат `fecdbbf` в `money.py` (`git diff 24ea71a..2e03cab` ≡ `git diff 24ea71a..162e359`).
- **FACT**: `format_money` имеет единственное вхождение в репозитории — определение в `money.py:4`; потребителей (внутренних и кросс-сервисных) в коде нет.
- **FACT**: коммит затрагивает только `money.py`; миграций, конфигураций, событий, интерфейсов нет → обязательных спутников не существует.
- **FACT**: `04f6ded` (только в staging) — release notes, с фиксом не связан.
- **FACT**: cherry-pick `2e03cab` в `staging` дал бы пустой результат (контент идентичен) — конфликтов нет именно потому, что переносить нечего.
- **HYPOTHESIS**: `162e359` — это и есть фикс BL-1020, применённый в staging напрямую (идентичность diff, смысловая близость сообщений).
- **UNKNOWN**: ветка `staging` существует только локально (remotes не настроены) — актуальность относительно реального remote подтвердить невозможно.

### Проверки
- **Выполнены**: read-only git-анализ (graph, merge-base, containment, diff-сравнение).
- **Рекомендуемые**: организационно связать BL-1020 с уже применённым хотфиксом (например, отметить в RELEASE.md / трекере), чтобы избежать повторных запросов переноса.
- **Недоступные/не найденные**: тестов в репозитории нет — регрессионную проверку `format_money` выполнить не на чем; это не влияет на вывод, поскольку перенос не требуется.

### Следующее действие
Cherry-pick не выполнять. Вердикт привязан к `staging@162e359` и списку `[2e03cab]`; при изменении HEAD цели — пере-оценка заново.