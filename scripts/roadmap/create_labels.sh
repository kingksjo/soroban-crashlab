#!/usr/bin/env bash
# Idempotent label creation for Soroban CrashLab roadmap.
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-SorobanCrashLab/soroban-crashlab}"

if [[ -z "${GH_TOKEN:-}" ]]; then
  echo "Set GH_TOKEN with repo scope." >&2
  exit 1
fi

create_label() {
  local name="$1"
  local color="$2"
  local description="$3"
  gh label create "$name" --repo "$REPO" --color "$color" --description "$description" --force 2>/dev/null \
    || gh api -X PATCH "repos/${REPO}/labels/$(printf '%s' "$name" | sed 's/:/%3A/g')" -f color="$color" -f description="$description" >/dev/null \
    || true
}

# Areas
for area in contracts soroban frontend docs scripts ci ops; do
  create_label "area:${area}" "0E8A16" "Repository area: ${area}"
done

# Stack
create_label "stack:rust" "DEA584" "Rust / crashlab-core"
create_label "stack:typescript" "3178C6" "TypeScript"
create_label "stack:nextjs" "000000" "Next.js app"
create_label "stack:markdown" "C5DEF5" "Documentation"
create_label "stack:github-actions" "2088FF" "GitHub Actions"

# Types
for t in feature bug refactor test chore docs; do
  create_label "type:${t}" "FBCA04" "Change type: ${t}"
done

# Priority
create_label "priority:p0" "B60205" "Critical path"
create_label "priority:p1" "D93F0B" "High"
create_label "priority:p2" "FBCA04" "Medium"
create_label "priority:p3" "0E8A16" "Low"

# Touch scope
create_label "touch:single-file" "EDEDED" "Single primary file — low conflict"
create_label "touch:module" "C2E0C6" "Small module scope"
create_label "touch:api-route" "BFD4F2" "API route handler"

create_label "roadmap" "6F42C1" "Roadmap batch issue"

echo "Labels ensured on ${REPO}"
