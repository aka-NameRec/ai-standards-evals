Review is complete: the scope is the staged diff (new `src/greet.ts` and `src/volume.ts`), all passes were run — Correctness, Architecture & Conventions, Reuse, Efficiency, Quality — plus a module-contract and decision-record check (none exist in the repository, and these two files are not major modules, so no `(no contract)` notes). Destination: chat, fenced block (default). No fixes were applied — nothing qualified as safe-by-reading.

```markdown
## Code Review

ai-standards 2.8.2

### What Was Done
Two string utilities are added: `greet` builds a greeting from a name, and `shout` uppercases text.

### How It Was Done
Each utility lives in its own module under `src/`, exports a single named function with explicit
parameter and return types, and has no dependencies.

### Correctness
- None found.

### Architecture & Conventions
- None found.

### Reuse
- None found.

### Efficiency
- None found.

### Quality
- None found.

### Verification
- no lint, typecheck, or test tooling is configured in the repository, so nothing was run;
  the review was done by reading the staged files
```

Nothing is left on your side: `Task` is omitted (no known tracker reference), `Dependencies` is dropped (the change is self-contained).