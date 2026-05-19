#!/usr/bin/env bash
# Bulk-create roadmap issues from scripts/roadmap/issues.json
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CATALOG="${ROOT}/scripts/roadmap/issues.json"
REPO="${GITHUB_REPOSITORY:-SorobanCrashLab/soroban-crashlab}"

if [[ -z "${GH_TOKEN:-}" ]]; then
  echo "Export GH_TOKEN (repo scope) before running." >&2
  exit 1
fi

if [[ ! -f "$CATALOG" ]]; then
  python3 "${ROOT}/scripts/roadmap/generate_catalog.py"
fi

echo "Creating milestones..."
for title in "P0 Foundation" "P1 Data bridge" "P2 Product UI" "P3 Integrations" "P4 Hardening" "P5 Documentation"; do
  gh api "repos/${REPO}/milestones" -f title="$title" -f state=open 2>/dev/null \
    || gh api "repos/${REPO}/milestones" --jq ".[] | select(.title==\"$title\") | .number" | head -1 >/dev/null || true
done

milestone_number() {
  local title="$1"
  gh api "repos/${REPO}/milestones" --jq ".[] | select(.title==\"${title}\") | .number" | head -1
}

count=$(jq '.count' "$CATALOG")
echo "Creating ${count} issues on ${REPO}..."

created=0
while read -r row; do
  title=$(jq -r '.title' <<<"$row")
  body=$(jq -r '.body' <<<"$row")
  milestone=$(jq -r '.milestone' <<<"$row")
  ms_num=$(milestone_number "$milestone")

  label_args=()
  while IFS= read -r label; do
    [[ -n "$label" ]] && label_args+=(--label "$label")
  done < <(jq -r '.labels[]' <<<"$row")

  issue_url=$(gh issue create \
    --repo "$REPO" \
    --title "$title" \
    --body "$body" \
    "${label_args[@]}" \
    ${ms_num:+--milestone "$ms_num"} 2>&1)

  created=$((created + 1))
  echo "[$created/$count] $title -> $issue_url"
  sleep 0.35
done < <(jq -c '.issues[]' "$CATALOG")

echo "Done. Created ${created} issues."
