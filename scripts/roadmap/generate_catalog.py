#!/usr/bin/env python3
"""Generate scripts/roadmap/issues.json with 140 non-overlapping roadmap issues."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from issue_body import format_issue_body

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "issues.json"

MILESTONES = [
    "P0 Foundation",
    "P1 Data bridge",
    "P2 Product UI",
    "P3 Integrations",
    "P4 Hardening",
    "P5 Documentation",
]


@dataclass
class Spec:
    slug: str
    title: str
    milestone: str
    area: str
    stack: list[str]
    issue_type: str
    priority: str
    touch: str
    description: str
    requirements: list[str]
    files: list[tuple[str, str, str]]
    checklist: list[str]
    blocked_by: list[int] = field(default_factory=list)
    extra_notes: str | None = None


def labels_for(spec: Spec) -> list[str]:
    return [
        f"area:{spec.area}",
        spec.issue_type,
        spec.priority,
        spec.touch,
        *spec.stack,
        "roadmap",
    ]


def expand(
    start_id: int,
    milestone: str,
    area: str,
    stack: list[str],
    issue_type: str,
    priority: str,
    touch: str,
    items: list[tuple],
) -> list[Spec]:
    specs: list[Spec] = []
    for i, item in enumerate(items):
        slug, title, desc, reqs, files, checklist, *rest = item
        blocked = rest[0] if rest else []
        specs.append(
            Spec(
                slug=slug,
                title=f"[{area}] {title}",
                milestone=milestone,
                area=area,
                stack=stack,
                issue_type=issue_type,
                priority=priority,
                touch=touch,
                description=desc,
                requirements=list(reqs),
                files=list(files),
                checklist=list(checklist),
                blocked_by=list(blocked) if blocked else [],
            )
        )
    return specs


def p0_contracts() -> list[Spec]:
    m, a, st = "P0 Foundation", "contracts", ["stack:rust"]
    return expand(
        1,
        m,
        a,
        st,
        "type:refactor",
        "priority:p0",
        "touch:single-file",
        [
            (
                "unify-classify-entrypoint",
                "Unify classify() with classify_failure() for bundle signatures",
                "The legacy `classify()` in `lib.rs` produces categories that diverge from `taxonomy::classify_failure()`, causing replay mismatches when bundles are created via `to_bundle()`. Unify so signatures and taxonomy align.",
                [
                    "Delegate `classify()` category selection to `classify_failure()` mapping",
                    "Preserve `signature_hash` stability rules documented in lib.rs",
                    "Add regression test covering previously mismatched payload",
                ],
                [
                    ("contracts/crashlab-core/src/lib.rs", "edit", "Unify classify implementation"),
                    ("contracts/crashlab-core/src/taxonomy.rs", "edit", "Export mapping helper if needed"),
                    ("contracts/crashlab-core/src/lib.rs", "edit", "Add/extend unit tests in mod tests"),
                ],
                [
                    "Implementation complete",
                    "Unit tests pass",
                    "No change to public JSON schema without version bump note in PR",
                ],
            ),
            (
                "signature-from-failure-class",
                "Add signature builder from FailureClass",
                "Introduce a single function that builds `CrashSignature` from seed bytes using taxonomy only.",
                [
                    "New helper used by `to_bundle` paths",
                    "Document stability guarantees in rustdoc",
                ],
                [
                    ("contracts/crashlab-core/src/signature_hash.rs", "edit", "Use helper for hash"),
                    ("contracts/crashlab-core/src/lib.rs", "edit", "Wire helper"),
                ],
                ["Helper covered by tests", "No duplicate hash logic elsewhere"],
            ),
            (
                "to-bundle-tests-taxonomy",
                "Expand to_bundle tests for taxonomy alignment",
                "Add fixtures proving bundle signatures match replay expectations.",
                ["Add regression tests", "Use existing fixtures where possible"],
                [
                    ("contracts/crashlab-core/fixtures/", "edit", "Add fixture if needed"),
                    ("contracts/crashlab-core/src/lib.rs", "edit", "Tests only"),
                ],
                ["cargo test green"],
            ),
            (
                "threat-model-tests-skeleton",
                "Re-enable threat_model_tests module (compile-only pass)",
                "Module is disabled due to API drift. Restore compile, skip obsolete cases with TODO referencing ROADMAP follow-ups.",
                ["Re-export module", "Fix imports to current FailureClass"],
                [
                    ("contracts/crashlab-core/src/lib.rs", "edit", "Re-export mod"),
                    ("contracts/crashlab-core/src/threat_model_tests.rs", "edit", "Fix imports"),
                ],
                ["Module compiles", "Tests run or are ignored with ticket refs"],
            ),
            (
                "runner-trait-contract",
                "Define ContractRunner trait for Soroban integrators",
                "Formalize the integration hook for executing seeds against a contract host.",
                ["Define trait and error types", "Document integration contract"],
                [
                    ("contracts/crashlab-core/src/runner.rs", "create", "Trait + error types"),
                    ("contracts/crashlab-core/src/lib.rs", "edit", "pub mod runner"),
                ],
                ["Trait documented", "Example mock runner in tests"],
            ),
            (
                "simulation-runner-bridge",
                "Bridge simulation module to ContractRunner",
                "Allow `run_simulation_with_timeout` to accept runner injection.",
                ["Inject runner into simulation", "Tests with mock runner"],
                [
                    ("contracts/crashlab-core/src/simulation.rs", "edit", "Inject runner"),
                    ("contracts/crashlab-core/src/runner.rs", "edit", "Use trait"),
                ],
                ["Tests with mock runner"],
            ),
        ],
    )


# Due to size, remaining phases are generated programmatically with unique slugs/files
def phase_issues(
    phase_specs: list[tuple[str, str, str, str, str, list]],
) -> list[Spec]:
    out: list[Spec] = []
    for slug, title, milestone, area, touch, payload in phase_specs:
        desc, reqs, files, checklist, *rest = payload
        blocked = rest[0] if rest else []
        stack = (
            ["stack:rust"]
            if area == "contracts"
            else ["stack:typescript", "stack:nextjs"]
            if area == "frontend"
            else ["stack:rust"]
            if area == "soroban"
            else ["stack:typescript"]
            if area in ("scripts", "ci")
            else ["stack:markdown"]
        )
        out.append(
            Spec(
                slug=slug,
                title=f"[{area}] {title}",
                milestone=milestone,
                area=area,
                stack=stack,
                issue_type="type:feature",
                priority="priority:p1",
                touch=touch,
                description=desc,
                requirements=reqs,
                files=files,
                checklist=checklist,
                blocked_by=blocked,
            )
        )
    return out


def build_p1() -> list[Spec]:
    m = "P1 Data bridge"
    items = []
    seeds = [
        ("run-index-json-export", "Export run index JSON from crash_index", "contracts", "touch:single-file", "contracts/crashlab-core/src/bin/crash-index.rs"),
        ("runs-index-cli-list", "Add crashlab runs list CLI subcommand", "contracts", "touch:single-file", "contracts/crashlab-core/src/bin/crashlab.rs"),
        ("api-types-runs", "Add TypeScript API types for runs", "frontend", "touch:single-file", "apps/web/src/lib/api/runs.ts"),
        ("api-get-runs", "Implement GET /api/runs from index file", "frontend", "touch:single-file", "apps/web/src/app/api/runs/route.ts"),
        ("api-get-run-by-id", "Implement GET /api/runs/[id]", "frontend", "touch:single-file", "apps/web/src/app/api/runs/[id]/route.ts"),
        ("runs-client-fetch", "Add runs-client fetch helper", "frontend", "touch:single-file", "apps/web/src/lib/runs-client.ts"),
        ("home-fetch-api-runs", "Replace home MOCK_RUNS with API", "frontend", "touch:single-file", "apps/web/src/app/page.tsx"),
        ("triage-fetch-api-runs", "Wire triage page to runs API", "frontend", "touch:single-file", "apps/web/src/app/triage/page.tsx"),
        ("trends-fetch-api-runs", "Wire trends page to runs API", "frontend", "touch:single-file", "apps/web/src/app/trends/page.tsx"),
        ("run-detail-api", "Wire run detail to GET /api/runs/[id]", "frontend", "touch:single-file", "apps/web/src/app/runs/[id]/page.tsx"),
        ("artifact-fs-adapter", "Filesystem artifact adapter for API", "frontend", "touch:single-file", "apps/web/src/lib/artifact-fs-adapter.ts"),
        ("api-artifacts-fs-get", "List artifacts from CRASHLAB_ARTIFACT_DIR", "frontend", "touch:single-file", "apps/web/src/app/api/artifacts/route.ts"),
        ("api-artifacts-fs-download", "Download artifact from filesystem", "frontend", "touch:single-file", "apps/web/src/app/api/artifacts/[id]/route.ts"),
        ("env-example-crashlab", "Add .env.example for CRASHLAB paths", "frontend", "touch:single-file", "apps/web/.env.example"),
        ("mock-runs-align-index", "Align buildMockRuns with index schema", "frontend", "touch:single-file", "apps/web/src/app/mockRuns.ts"),
        ("integrate-artifacts-route", "Add /integrations/artifacts page route", "frontend", "touch:single-file", "apps/web/src/app/integrations/artifacts/page.tsx"),
        ("mount-storage-integration", "Mount storage integration component on route", "frontend", "touch:single-file", "apps/web/src/app/integrations/artifacts/page.tsx"),
        ("artifact-explorer-api", "Wire ArtifactExplorer to /api/artifacts", "frontend", "touch:single-file", "apps/web/src/app/add-artifact-explorer.tsx"),
        ("local-artifact-store-config", "Read LocalArtifactStore path in Rust via env", "contracts", "touch:single-file", "contracts/crashlab-core/src/artifact_storage.rs"),
        ("bundle-manifest-sidecar", "Write artifact manifest sidecar JSON", "contracts", "touch:single-file", "contracts/crashlab-core/src/artifact_storage.rs"),
        ("ci-api-runs-smoke", "CI smoke curl /api/runs with fixture", "ci", "touch:single-file", ".github/workflows/ci.yml"),
        ("api-runs-error-shape", "Standardize API error JSON shape", "frontend", "touch:single-file", "apps/web/src/lib/api/errors.ts"),
        ("api-runs-loading-states", "Shared loading skeleton for runs lists", "frontend", "touch:single-file", "apps/web/src/components/runs/RunsListSkeleton.tsx"),
        ("runs-cache-revalidate", "Add revalidate config for runs API", "frontend", "touch:single-file", "apps/web/src/app/api/runs/route.ts"),
        ("index-watcher-dev", "Dev-only index file watcher script", "scripts", "touch:single-file", "scripts/dev/watch-run-index.ts"),
    ]
    for slug, title, area, touch, primary in seeds:
        action = "create" if "create" in primary or "/api/" in primary or "components/" in primary else "edit"
        items.append(
            (
                slug,
                title,
                m,
                area,
                touch,
                (
                    f"Implement **{title}** as part of the Rust ↔ Next.js data bridge. This issue owns only `{primary}` to minimize merge conflicts.",
                    [f"Deliver working code in `{primary}`", "Add or update focused tests", "Document env vars in PR if applicable"],
                    [(primary, action, "Primary ownership for this issue")],
                    ["Implementation merged", "Tests pass", "No lockfile changes"],
                ),
            )
        )
    return phase_issues(items)


def build_p2() -> list[Spec]:
    m = "P2 Product UI"
    items = []
    ui_pieces = [
        ("dashboard-shell-layout", "Extract dashboard shell layout component", "apps/web/src/app/dashboard/DashboardShell.tsx"),
        ("dashboard-home-runs-only", "Reduce home page to runs overview only", "apps/web/src/app/page.tsx"),
        ("route-runs-list", "Create /runs list route", "apps/web/src/app/runs/page.tsx"),
        ("route-analytics", "Create /analytics route for charts", "apps/web/src/app/analytics/page.tsx"),
        ("route-integrations-hub", "Create /integrations hub route", "apps/web/src/app/integrations/page.tsx"),
        ("route-settings-hub", "Create /settings hub route", "apps/web/src/app/settings/page.tsx"),
        ("remove-virtualized-duplicate-table", "Remove duplicate VirtualizedRunTable from home", "apps/web/src/app/page.tsx"),
        ("single-timeline-component", "Consolidate to one timeline on run views", "apps/web/src/app/runs/[id]/RunTimeline.tsx"),
        ("remove-scrubber-from-home", "Move TimelineScrubber to /runs only", "apps/web/src/app/TimelineScrubber.tsx"),
        ("logs-page-shared-fetch", "Unify logs with shared log provider", "apps/web/src/app/logs/page.tsx"),
        ("log-viewer-extract", "Extract LogViewer data hook", "apps/web/src/app/hooks/useLogEntries.ts"),
        ("wire-dashboard-filters", "Apply AdvancedDashboardFilters to query", "apps/web/src/app/page.tsx"),
        ("filters-url-sync", "Sync dashboard filters to URL params", "apps/web/src/app/hooks/useDashboardFilters.ts"),
        ("remove-simulated-fetch-error", "Remove random 10% home fetch failure", "apps/web/src/app/page.tsx"),
        ("maintainer-mode-layout", "Isolate maintainer widgets route", "apps/web/src/app/maintainer/page.tsx"),
        ("nav-primary-routes", "Update header nav to product routes", "apps/web/src/app/layout.tsx"),
        ("footer-roadmap-link", "Link footer to GitHub roadmap milestone", "apps/web/src/app/layout.tsx"),
        ("onboarding-route", "Move onboarding modal to /onboarding", "apps/web/src/app/onboarding/page.tsx"),
        ("campaign-launch-api", "POST /api/campaigns stub", "apps/web/src/app/api/campaigns/route.ts"),
        ("campaign-form-api-wire", "Wire CampaignConfigForm to API", "apps/web/src/app/CampaignConfigForm.tsx"),
        ("cluster-view-route", "Move cluster viz to /analytics/clusters", "apps/web/src/app/analytics/clusters/page.tsx"),
        ("heatmap-single-route", "Single heatmap page with metric toggle", "apps/web/src/app/analytics/heatmap/page.tsx"),
        ("state-diff-run-detail", "Show ledger diff on run detail from API", "apps/web/src/app/runs/[id]/page.tsx"),
        ("reporting-templates-route", "One reporting templates route", "apps/web/src/app/settings/reporting/page.tsx"),
        ("remove-duplicate-templates", "Remove duplicate template manager from home", "apps/web/src/app/page.tsx"),
        ("workflow-board-route", "Move workflow board to /triage/board", "apps/web/src/app/triage/board/page.tsx"),
        ("fuzzy-query-route", "Move fuzzy builder to /runs/query", "apps/web/src/app/runs/query/page.tsx"),
        ("bulk-actions-runs-page", "Bulk actions on /runs only", "apps/web/src/app/runs/page.tsx"),
        ("export-json-runs-page", "Export JSON from /runs toolbar", "apps/web/src/app/add-export-run-json.tsx"),
        ("export-csv-runs-page", "Export CSV from /runs toolbar", "apps/web/src/app/add-export-run-csv.tsx"),
        ("run-annotations-api", "Persist annotations via API", "apps/web/src/app/api/runs/[id]/annotations/route.ts"),
        ("tagging-labels-api", "Persist tags via API", "apps/web/src/app/api/runs/[id]/tags/route.ts"),
        ("notification-center-api", "Optional notifications feed API", "apps/web/src/app/api/notifications/route.ts"),
        ("dark-mode-no-flash", "Fix dark mode hydration flash", "apps/web/src/app/add-dark-mode-support.tsx"),
        ("accessibility-skip-link", "Enhance skip link targeting #main-content", "apps/web/src/app/add-accessible-keyboard-nav-blueprint.tsx"),
        ("responsive-container-tokens", "Use layout tokens in responsive container", "apps/web/src/app/add-responsive-layout-improvements.tsx"),
    ]
    for slug, title, primary in ui_pieces:
        items.append(
            (
                slug,
                title,
                m,
                "frontend",
                "touch:single-file",
                (
                    f"Product UI revamp task: {title}. Owns exclusively `{primary}`.",
                    ["Implement UX per description", "No new mock data paths", "Match existing Tailwind patterns"],
                    [(primary, "create" if "create" in primary else "edit", "Single-file ownership")],
                    ["Visually verified in dev", "lint/build pass"],
                ),
            )
        )
    return phase_issues(items)


def build_soroban() -> list[Spec]:
    m = "P1 Data bridge"
    items = []
    contract_steps = [
        ("soroban-workspace-scaffold", "Scaffold contracts/soroban-example workspace", "contracts/soroban-example/Cargo.toml"),
        ("soroban-token-contract", "Add example token contract lib.rs", "contracts/soroban-example/src/lib.rs"),
        ("soroban-contract-tests", "Add contract unit tests", "contracts/soroban-example/src/test.rs"),
        ("soroban-build-wasm-script", "Script build wasm32 for example contract", "scripts/contracts/build-soroban-example.sh"),
        ("soroban-deploy-docs-target", "Document deploy targets in contract README", "contracts/soroban-example/README.md"),
        ("host-runner-impl", "Implement HostContractRunner using soroban-sdk testutils", "contracts/crashlab-core/src/host_runner.rs"),
        ("host-runner-wire-matrix", "Use host runner in auth_matrix tests", "contracts/crashlab-core/src/auth_matrix.rs"),
        ("rpc-runner-trait-impl", "Add RpcContractRunner stub for RPC URL", "contracts/crashlab-core/src/rpc_runner.rs"),
        ("runner-select-config", "Select runner via env CRASHLAB_RUNNER", "contracts/crashlab-core/src/runner.rs"),
        ("export-wasm-artifact-cli", "CLI export wasm hash artifact", "contracts/crashlab-core/src/bin/export-wasm-hash.rs"),
        ("ci-soroban-build-job", "CI job build soroban example wasm", ".github/workflows/ci.yml"),
        ("integrate-runner-readme", "Integrator guide for runner wiring", "contracts/crashlab-core/README.md"),
    ]
    for slug, title, primary in contract_steps:
        area = "soroban" if "soroban-example" in primary else "contracts"
        items.append(
            (
                slug,
                title,
                m,
                area,
                "touch:single-file",
                (
                    f"Soroban credibility track: {title}.",
                    ["Working Rust/Soroban build", "Tests in CI where applicable"],
                    [(primary, "create" if "create" in primary else "edit", "Owned file")],
                    ["cargo build/test pass"],
                ),
            )
        )
    return phase_issues(items)


def build_p3() -> list[Spec]:
    m = "P3 Integrations"
    integrations = [
        ("prometheus-deps-impl", "Implement MetricsExportDependencies adapter", "apps/web/src/lib/integrations/prometheus-adapter.ts", "frontend"),
        ("prometheus-ui-wire", "Wire Prometheus UI to adapter", "apps/web/src/app/integrate-metrics-export-to-prometheus.tsx", "frontend"),
        ("issue-link-github-adapter", "GitHub issue link adapter", "apps/web/src/lib/integrations/github-issues.ts", "frontend"),
        ("issue-link-jira-adapter", "Jira issue link adapter stub", "apps/web/src/lib/integrations/jira-issues.ts", "frontend"),
        ("issue-link-linear-adapter", "Linear issue link adapter stub", "apps/web/src/lib/integrations/linear-issues.ts", "frontend"),
        ("issue-link-ui-wire", "Wire issue link integration UI", "apps/web/src/app/integrate-run-issue-link-integration-tests.tsx", "frontend"),
        ("issue-link-api-persist", "API route persist run issue links", "apps/web/src/app/api/runs/[id]/issues/route.ts", "frontend"),
        ("alerting-api-get-put", "GET/PUT /api/settings/alerting", "apps/web/src/app/api/settings/alerting/route.ts", "frontend"),
        ("alerting-ui-api-wire", "Wire create alerting page to API", "apps/web/src/app/create-alerting-settings-page-page.tsx", "frontend"),
        ("remove-mock-alerting-54", "Remove mock fetch from alerting page 54", "apps/web/src/app/implement-alerting-settings-page-54.tsx", "frontend"),
        ("sentry-sdk-install", "Add @sentry/nextjs integration", "apps/web/src/lib/integrations/sentry-client.ts", "frontend"),
        ("sentry-ui-wire", "Wire Sentry settings UI", "apps/web/src/app/integrate-sentry-integration-for-crash-reporting.tsx", "frontend"),
        ("webhook-api-persist", "Persist webhooks via API", "apps/web/src/app/api/webhooks/route.ts", "frontend"),
        ("webhook-ui-persist", "Wire webhook manager to API", "apps/web/src/app/integrate-webhook-manager-for-run-events.tsx", "frontend"),
        ("replay-api-invoke", "POST /api/runs/[id]/replay invoking CLI", "apps/web/src/app/api/runs/[id]/replay/route.ts", "frontend"),
        ("replay-ui-real", "Replace simulateSeedReplay with API", "apps/web/src/app/replay.ts", "frontend"),
        ("ci-replay-integration-page", "Mount CI replay integration page", "apps/web/src/app/integrations/ci-replay/page.tsx", "frontend"),
        ("db-migration-integration-page", "Mount DB migration integration page", "apps/web/src/app/integrations/db-migrations/page.tsx", "frontend"),
        ("external-auth-integration-page", "Mount external auth integration page", "apps/web/src/app/integrations/auth/page.tsx", "frontend"),
        ("regression-deploy-page", "Mount regression deploy integration page", "apps/web/src/app/integrations/regression-deploy/page.tsx", "frontend"),
        ("ui-harness-page", "Mount UI flow harness page", "apps/web/src/app/integrations/ui-harness/page.tsx", "frontend"),
        ("replay-e2e-page", "Mount replay E2E integration page", "apps/web/src/app/integrations/replay-e2e/page.tsx", "frontend"),
        ("sanity-check-page", "Mount sanity check pipeline page", "apps/web/src/app/integrations/sanity-check/page.tsx", "frontend"),
        ("api-error-report-page-route", "Mount API error report page", "apps/web/src/app/integrations/api-errors/page.tsx", "frontend"),
        ("run-issue-link-page-route", "Mount run issue link creator page", "apps/web/src/app/integrations/issue-links/page.tsx", "frontend"),
        ("prometheus-api-health", "API route exporter health check", "apps/web/src/app/api/integrations/prometheus/health/route.ts", "frontend"),
        ("health-metrics-rust-export", "Export HealthSummary JSON from Rust", "contracts/crashlab-core/src/health.rs", "contracts"),
        ("health-metrics-api", "Expose /api/health/metrics", "apps/web/src/app/api/health/metrics/route.ts", "frontend"),
        ("webhook-delivery-worker", "Background webhook delivery util", "apps/web/src/lib/webhook-delivery-worker.ts", "frontend"),
        ("integrate-sentry-server", "Sentry server instrumentation", "apps/web/src/instrumentation.ts", "frontend"),
        ("oauth-github-callback", "GitHub OAuth callback route stub", "apps/web/src/app/api/auth/github/callback/route.ts", "frontend"),
        ("oauth-secrets-env", "Document OAuth secrets in .env.example", "apps/web/.env.example", "frontend"),
        ("integration-test-deps-ci", "Run integration utils tests in CI", ".github/workflows/ci.yml", "ci"),
        ("issue-link-detail-wire", "Show associated issues on run detail", "apps/web/src/app/runs/[id]/page.tsx", "frontend"),
        ("triage-board-api", "Wire triage board to issues API", "apps/web/src/app/triage/page.tsx", "frontend"),
    ]
    items = []
    for row in integrations:
        slug, title, primary, area = row
        items.append(
            (
                slug,
                title,
                m,
                area,
                "touch:single-file",
                (
                    f"Integration deliverable: {title}.",
                    ["Implement real adapter or API", "Remove mock timers where applicable", "Utils tests updated"],
                    [(primary, "create" if "/api/" in primary or "/integrations/" in primary or "lib/integrations" in primary else "edit", "Exclusive file")],
                    ["Manual test steps in PR", "build/test pass"],
                ),
            )
        )
    return phase_issues(items)


def build_p4() -> list[Spec]:
    m = "P4 Hardening"
    items = []
    hardening = [
        ("e2e-playwright-scaffold", "Add Playwright e2e scaffold", "apps/web/e2e/home.spec.ts"),
        ("e2e-runs-list", "E2E runs list loads", "apps/web/e2e/runs.spec.ts"),
        ("e2e-artifact-upload", "E2E artifact upload/download", "apps/web/e2e/artifacts.spec.ts"),
        ("threat-model-tests-full", "Complete threat_model_tests refactor", "contracts/crashlab-core/src/threat_model_tests.rs"),
        ("flaky-detector-dashboard", "Surface flaky rate in UI", "apps/web/src/app/analytics/flaky/page.tsx"),
        ("regression-suite-badge", "Show regression suite status badge", "apps/web/src/components/RegressionStatusBadge.tsx"),
        ("bundle-schema-validation-api", "Validate CaseBundle uploads", "apps/web/src/app/api/artifacts/validate/route.ts"),
        ("rate-limit-api-middleware", "Rate limit public API routes", "apps/web/src/middleware.ts"),
        ("security-headers-middleware", "Add security headers", "apps/web/next.config.ts"),
        ("a11y-axe-ci", "axe a11y check in CI", ".github/workflows/ci.yml"),
        ("perf-virtualize-runs-only", "Ensure virtualization on large lists only", "apps/web/src/app/runs/page.tsx"),
        ("structured-logging-api", "Structured logs for API handlers", "apps/web/src/lib/logger.ts"),
        ("rust-log-env-filter", "RUST_LOG filter in CLI bins", "contracts/crashlab-core/src/bin/crashlab.rs"),
        ("retention-policy-job", "Retention sweep CLI command", "contracts/crashlab-core/src/bin/crashlab.rs"),
        ("crash-index-dedup-ui", "Crash index dedup stats component", "apps/web/src/components/CrashIndexStats.tsx"),
        ("replay-cli-api-bridge-test", "Integration test CLI replay bridge", "contracts/crashlab-core/tests/api_replay_bridge.rs"),
        ("pnpm-ci-migration", "Migrate CI from npm to pnpm", ".github/workflows/ci.yml"),
        ("contributor-pr-template", "Add pull request template", ".github/pull_request_template.md"),
        ("codeowners-file", "Add CODEOWNERS for areas", ".github/CODEOWNERS"),
        ("stale-bot-config", "Configure stale issue workflow", ".github/workflows/stale.yml"),
        ("release-drafter", "Release drafter workflow", ".github/workflows/release-drafter.yml"),
        ("benchmark-mutation-budget", "Criterion bench mutation budget", "contracts/crashlab-core/benches/mutation_budget.rs"),
        ("fuzz-smoke-ci", "Short fuzz smoke in CI", ".github/workflows/ci.yml"),
        ("api-openapi-spec", "OpenAPI spec for public routes", "apps/web/openapi.yaml"),
        ("api-openapi-ui", "Swagger UI dev route", "apps/web/src/app/api-docs/page.tsx"),
    ]
    return phase_issues(
        [
            (
                slug,
                title,
                m,
                "frontend" if primary.startswith("apps") else "contracts" if "contracts" in primary else "ci",
                "touch:single-file",
                (
                    f"Hardening: {title}.",
                    ["Production-quality implementation", "Tests or CI verification"],
                    [(primary, "create" if "create" in primary or "e2e/" in primary or ".github/" in primary else "edit", "Owned path")],
                    ["CI green", "Documented in PR"],
                ),
            )
            for slug, title, primary in hardening
        ]
    )


def build_p0_frontend_scripts() -> list[Spec]:
    m = "P0 Foundation"
    fe = [
        (
            "shared-artifact-store-module",
            "Shared artifact store for API routes",
            "Completed in foundation prep; verify tests document singleton behavior.",
            ["apps/web/src/lib/artifact-store.ts"],
        ),
        (
            "settings-routes-stub",
            "Settings routes for accessibility and alerting",
            "Stub routes prevent 404 from header nav.",
            ["apps/web/src/app/settings/accessibility/page.tsx", "apps/web/src/app/settings/alerting/page.tsx"],
        ),
        (
            "roadmap-issue-generator",
            "Roadmap issue catalog generator script",
            "Generate issues.json for bulk GitHub creation.",
            ["scripts/roadmap/generate_catalog.py"],
        ),
        (
            "roadmap-create-issues-script",
            "Bulk create GitHub issues script",
            "Uses gh api with labels and milestones.",
            ["scripts/roadmap/create_github_issues.sh"],
        ),
        (
            "roadmap-labels-script",
            "Create GitHub labels script",
            "Idempotent label creation.",
            ["scripts/roadmap/create_labels.sh"],
        ),
        (
            "ops-backlog-archive",
            "Archive ops TSV backlog with GitHub issue pointer",
            "Mark ops TSV as archived; link to milestones.",
            ["ops/README.md"],
        ),
        (
            "consolidate-mock-runs-home",
            "Use buildMockRuns on dashboard home",
            "Single generator for run shape.",
            ["apps/web/src/app/page.tsx"],
        ),
        (
            "wire-dashboard-filters-logic",
            "Apply dashboardFilters in filteredRuns",
            "Advanced filters must affect list.",
            ["apps/web/src/app/page.tsx"],
        ),
        (
            "remove-random-fetch-failure",
            "Remove simulated network failure on home",
            "Keep loading state demo optional via query flag.",
            ["apps/web/src/app/page.tsx"],
        ),
    ]
    specs = []
    for slug, title, desc, files in fe:
        specs.append(
            Spec(
                slug=slug,
                title=f"[frontend] {title}" if "apps" in files[0] else f"[scripts] {title}",
                milestone=m,
                area="frontend" if files[0].startswith("apps") else "scripts" if "scripts" in files[0] else "ops",
                stack=["stack:typescript", "stack:nextjs"] if files[0].startswith("apps") else ["stack:typescript"],
                issue_type="type:chore" if "script" in slug or "ops" in slug else "type:bug",
                priority="priority:p0",
                touch="touch:single-file",
                description=desc,
                requirements=["Implement as described", "No lockfile commits"],
                files=[(f, "edit" if "artifact-store" not in slug else "edit", "Primary file") for f in files],
                checklist=["Done", "build/test pass"],
            )
        )
    return specs


def build_docs() -> list[Spec]:
    m = "P5 Documentation"
    docs = [
        ("vision-md", "Add docs/VISION.md product vision", "docs/VISION.md", "Define 90% done criteria aligned with roadmap."),
        ("contributing-md", "Add CONTRIBUTING.md with PR policy", "CONTRIBUTING.md", "Branch naming, lockfile policy, one-issue-per-PR."),
        ("api-contract-md", "Add docs/API.md for Next routes", "docs/API.md", "Document /api/runs, artifacts, settings."),
        ("env-configuration-md", "Add docs/ENV.md", "docs/ENV.md", "CRASHLAB_ARTIFACT_DIR, runners, OAuth."),
        ("roadmap-index-md", "Add docs/ROADMAP.md index", "docs/ROADMAP.md", "Milestone table linking to GitHub milestones."),
    ]
    return [
        Spec(
            slug=slug,
            title=f"[docs] {title}",
            milestone=m,
            area="docs",
            stack=["stack:markdown"],
            issue_type="type:docs",
            priority="priority:p2",
            touch="touch:single-file",
            description=desc,
            requirements=["Complete markdown", "Cross-link from README", "Reviewed for accuracy"],
            files=[(path, "create", "New documentation file")],
            checklist=["Doc merged", "Links valid"],
        )
        for slug, title, path, desc in docs
    ]


def main() -> None:
    # Exact allocation: 135 code + 5 docs (issues 136–140)
    limits = {
        "p0_contracts": 6,
        "p0_fe_scripts": 9,
        "soroban": 12,
        "p1": 18,
        "p2": 35,
        "p3": 35,
        "p4": 20,
    }
    all_specs: list[Spec] = []
    all_specs.extend(p0_contracts()[: limits["p0_contracts"]])
    all_specs.extend(build_p0_frontend_scripts()[: limits["p0_fe_scripts"]])
    all_specs.extend(build_soroban()[: limits["soroban"]])
    all_specs.extend(build_p1()[: limits["p1"]])
    all_specs.extend(build_p2()[: limits["p2"]])
    all_specs.extend(build_p3()[: limits["p3"]])
    all_specs.extend(build_p4()[: limits["p4"]])

    code_count = len(all_specs)
    assert code_count == 135, f"Expected 135 code issues, got {code_count}"

    all_specs.extend(build_docs())  # always 5, roadmap 136–140
    assert len(all_specs) == 140, f"Expected 140 total, got {len(all_specs)}"

    issues = []
    for idx, spec in enumerate(all_specs, start=1):
        body = format_issue_body(
            roadmap_id=idx,
            slug=spec.slug,
            description=spec.description,
            requirements=spec.requirements,
            files=spec.files,
            checklist=spec.checklist,
            blocked_by=spec.blocked_by,
            extra_notes=spec.extra_notes,
        )
        issues.append(
            {
                "roadmap_id": idx,
                "title": spec.title,
                "slug": spec.slug,
                "milestone": spec.milestone,
                "labels": labels_for(spec),
                "body": body,
            }
        )

    OUT.write_text(json.dumps({"issues": issues, "count": len(issues)}, indent=2), encoding="utf-8")
    print(f"Wrote {len(issues)} issues to {OUT}")


if __name__ == "__main__":
    main()
