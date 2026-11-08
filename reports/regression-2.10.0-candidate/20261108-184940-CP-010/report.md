Selector BL-1060 resolved against the repository. Resolution record:

**Source:** `develop` (HEAD `0f6d970`) → **Target:** `staging` (HEAD `7f37388`, merge-base `46dad9f`)

**Resolved candidate set** (topological order, task-id matched by subject prefix across all refs — only these 2 commits mention BL-1060):

| # | SHA | Subject | Content |
|---|---------|---------------------------------------------|-----------------------------------|
| 1 | `41c54ab` | BL-1060: add promo export endpoint | new standalone file `export.py` |
| 2 | `0f6d970` | BL-1060: extract csv helper | new standalone file `csv.py` |

**FACT:**
- On `staging` there are no equivalents of these changes (no `csv.py`/`export.py` in the tree), the transfer has not been performed previously.
- `staging` differs from the merge-base only by `RELEASE.md` (commit `7f37388`), there are no conflicts in file overlap.
- Commits do not depend on each other and on other modules of the project; revert pairs/fixups were not found.

**Notes before analysis:**
- There is no `remote` in the repository — the freshness of local references relative to the remote cannot be confirmed (**UNKNOWN**).
- Docstring in `csv.py` mentions "extracted from the import module", but the `import*` module does not exist in either branch's history — will be checked in the completeness analysis.

Per the workflow, I will proceed with analyses A–F and issue a verdict only after you confirm this list. Shall I confirm the transfer of exactly these two commits (`41c54ab` → `0f6d970`) to `staging` @ `7f37388`?