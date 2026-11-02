"""CLI: run the RD-120 stack-trigger matrix over the registry stack entries.

The matrix materializes one fixture per stack entry in
``[reference_disclosure.stacks]`` of the pinned revision, runs the stack's
edit prompt through the adapter, and scores the reference-read-before-edit
oracle plus the encoded stack rule.
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from agents.kilo import KiloAdapter
from scorers.reference_disclosure import check_rd120_param
from scripts.config import EvalConfig, load_config
from scripts.fixtures import build_rd120_param
from scripts.pipeline import ScenarioVerdict
from scripts.render import render_agents_md
from scripts.standards import resolve_standards_checkout

# Encoded rule per stack entry: a distinctive verbatim substring of the stack
# reference (the fragment body). The scorer asserts the substring still exists
# in the deployed reference, so parameter drift fails loudly instead of
# passing silently.
ENCODED_RULES: dict[str, str] = {
    "layered-architecture": "explicit dependency boundaries",
    "backend-layered-architecture": "transport boundaries",
    "frontend-layered-architecture": "UI composition",
    "typescript": "Avoid `any`",
    "python": "pathlib",
    "fastapi": "dependency injection",
    "react": "during rendering",
    "nextjs": "App Router",
    "tanstack-query": "query keys",
    "postgres": "backward compatibility",
    "vue": "<script setup>",
    "nuxt": "useFetch",
    "vue-query": "query keys",
    "vite": "import.meta.env",
    "fsd": "slice",
    "java": "`Optional`",
    "spring": "constructor injection",
    "spring-data-jpa": "DTOs or projections",
    "java-spring": "constructor injection",
    "django": "nearest surrounding context",
    "django-service-layer": "service-and-selector",
    "django-drf": "least abstract",
    "django-save-orchestration": "save wrapper",
    "sqlalchemy": "context managers",
}

# Probe file and edit request per stack entry; the request is small and sits
# inside the encoded rule's area, so a compliant agent applies the rule.
STACK_PARAMS: dict[str, tuple[str, str]] = {
    "layered-architecture": (
        "src/services/billing.py",
        "добавь функцию charge_invoice в этот слой",
    ),
    "backend-layered-architecture": (
        "src/services/payments.py",
        "добавь функцию refund_payment в этот слой",
    ),
    "frontend-layered-architecture": (
        "src/features/catalog/api.ts",
        "добавь функцию fetchCatalog в этот слой",
    ),
    "typescript": ("src/index.ts", "добавь функцию formatId(id: number): string"),
    "python": ("src/util.py", "добавь функцию чтения конфига load_config"),
    "fastapi": ("src/api/routes.py", "добавь роут GET /health"),
    "react": ("src/components/Cart.tsx", "добавь компонент CartBadge"),
    "nextjs": ("src/app/page.tsx", "добавь секцию Header на страницу"),
    "tanstack-query": ("src/queries/useCatalog.ts", "добавь query-фабрику useCatalogQuery"),
    "vue-query": ("src/queries/useCatalog.ts", "добавь query-фабрику useCatalogQuery"),
    "postgres": ("migrations/0001_init.sql", "добавь таблицу order_items"),
    "vue": ("src/components/ProductCard.vue", "добавь пропс compact"),
    "nuxt": ("src/pages/index.vue", "добавь секцию Hero на страницу"),
    "vite": ("vite.config.ts", "добавь алиас @ -> src"),
    "fsd": ("src/features/cart/ui/Cart.tsx", "добавь компонент CartTotal"),
    "java": ("src/main/java/app/Order.java", "добавь record OrderLine"),
    "spring": ("src/main/java/app/OrderController.java", "добавь endpoint GET /orders"),
    "spring-data-jpa": (
        "src/main/java/app/repo/OrderRepo.java",
        "добавь метод поиска findAllByStatus",
    ),
    "java-spring": ("src/main/java/app/OrderService.java", "добавь метод placeOrder"),
    "django": ("src/orders/models.py", "добавь поле created_at в модель Order"),
    "django-service-layer": ("src/services/orders.py", "добавь сервис-функцию cancel_order"),
    "django-drf": ("src/orders/api.py", "добавь endpoint GET /orders/<id>"),
    "django-save-orchestration": ("src/services/save_order.py", "добавь обёртку save_order"),
    "sqlalchemy": ("src/db/session.py", "добавь контекстный менеджер сессии"),
}


def _reference_stacks(worktree: Path) -> list[str]:
    """Stack entries declared reference-capable by the pinned revision."""
    data = tomllib.loads((worktree / "registry.toml").read_text(encoding="utf-8"))
    disclosure = cast("dict[str, object]", data.get("reference_disclosure", {}))
    stacks = cast("list[str]", disclosure.get("stacks", []))
    return sorted(stacks)


def _run_parameter(
    config: EvalConfig,
    worktree: Path,
    adapter: KiloAdapter,
    stack: str,
    base_dir: Path,
) -> ScenarioVerdict:
    probe_path, request = STACK_PARAMS[stack]
    param_dir = base_dir / stack
    param_dir.mkdir(parents=True, exist_ok=True)
    probe_content = f"# {stack} probe file\n\nEdit target for the RD-120 matrix.\n"
    fixture = build_rd120_param(
        worktree,
        param_dir / "fixture",
        config.standards_revision,
        render_agents_md,
        stack=stack,
        probe_relative_path=probe_path,
        probe_content=probe_content,
    )
    prompt = (
        f"{request}. Файл: {probe_path}. Перед правкой сверись со стековыми "
        "правилами проекта."
    )
    result = adapter.run(prompt, fixture, f"RD-120-{stack}")
    (param_dir / "agent-stdout.jsonl").write_text(result.stdout, encoding="utf-8")
    (param_dir / "report.md").write_text(result.answer, encoding="utf-8")
    check = check_rd120_param(
        result.stdout,
        result.answer,
        fixture,
        stack=stack,
        encoded_rule=ENCODED_RULES[stack],
    )
    verdict = ScenarioVerdict(
        scenario_id=f"RD-120[{stack}]",
        ok=check.ok,
        failures=check.failures,
        report_path=param_dir / "report.md",
        fixture_path=fixture,
    )
    (param_dir / "verdict.json").write_text(
        json.dumps(
            {
                "scenario_id": verdict.scenario_id,
                "ok": verdict.ok,
                "failures": list(verdict.failures),
                "adapter": result.adapter,
                "model": config.model,
                "standards_revision": config.standards_revision,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return verdict


def main(argv: list[str] | None = None) -> int:
    """Run the stack matrix; exit non-zero when any parameter fails."""
    parser = argparse.ArgumentParser(description="Run the RD-120 stack trigger matrix.")
    parser.add_argument("--config", type=Path, default=Path("config.toml"))
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    parser.add_argument(
        "--revision",
        default=None,
        help="Override the pinned standards revision (tag, branch, or commit)",
    )
    parser.add_argument("--stacks", default=None, help="Comma-separated stack subset")
    args = parser.parse_args(argv)

    config = load_config(args.config, args.revision)
    adapter = KiloAdapter(model=config.model, timeout_seconds=config.timeout_seconds)
    with resolve_standards_checkout(config) as worktree:
        stacks = _reference_stacks(worktree)
        if args.stacks:
            wanted = {name.strip() for name in args.stacks.split(",")}
            stacks = [stack for stack in stacks if stack in wanted]
        unknown = [stack for stack in stacks if stack not in ENCODED_RULES]
        if unknown:
            parser.error(f"no matrix parameter for stacks: {', '.join(unknown)}")
        stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        base_dir = args.reports_dir / f"{stamp}-RD-120"
        results = [
            _run_parameter(config, worktree, adapter, stack, base_dir) for stack in stacks
        ]

    failed = [verdict for verdict in results if not verdict.ok]
    for verdict in failed:
        print(f"{verdict.scenario_id}: FAIL")
        for failure in verdict.failures:
            print(f"  - {failure}")
    passed = len(results) - len(failed)
    print(f"matrix: {passed}/{len(results)} PASS")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
