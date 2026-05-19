# Ops backlog

Historical Wave 3 backlog TSV files in this directory are **archived**.

**Source of truth:** GitHub Issues and milestones (`P0 Foundation` … `P5 Documentation`).

Generate or refresh the roadmap catalog locally:

```bash
python3 scripts/roadmap/generate_catalog.py
export GH_TOKEN=...   # repo scope, do not commit
./scripts/roadmap/create_labels.sh
./scripts/roadmap/create_github_issues.sh
```

Do not edit `pnpm-lock.yaml` or `package-lock.json` in contributor PRs.
