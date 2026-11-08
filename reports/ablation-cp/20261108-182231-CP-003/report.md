Перенос не требуется: эквивалентная правка уже есть в `staging`.

- В `develop` задача BL-1020 — коммит `056fbf2` «fix format_money for negative amounts» (правка `money.py`).
- В `staging` уже есть коммит `7ebdec3` «hotfix: correct format_money rounding for negative invoices» с идентичным содержимым: тот же исходный блоб `6d41d7b` и тот же результат `fecdbbf`, дельта побайтово совпадает.
- `git diff develop staging -- money.py` пустой — файлы полностью идентичны; в `staging` нет других расхождений по этой функции.

Рекомендация: коммит `056fbf2` не переносить. Обычный `git cherry-pick` на `staging` дал бы пустой коммит (изменения уже применены). Если нужна формальная трассировка BL-1020 в истории `staging`, можно сделать `git cherry-pick -x --allow-empty 056fbf2`, но это создаст дублирующий пустой коммит — по умолчанию лучше ограничиться отметкой задачи как выполненной в `staging`.