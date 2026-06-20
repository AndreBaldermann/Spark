#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker is not installed or not available on PATH." >&2
  exit 127
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "ERROR: docker compose is not available." >&2
  exit 127
fi

echo "Clean previous generated homelab data..."
rm -rf data/homelab/raw data/homelab/curated data/homelab/checkpoints
mkdir -p data/homelab/raw data/homelab/curated

echo "Build spark-demo image..."
docker compose build spark-demo

echo "Start platform services..."
docker compose up -d postgres grafana redpanda

echo "Wait for PostgreSQL healthcheck..."
for _ in {1..30}; do
  if docker compose exec -T postgres pg_isready -U homelab -d homelab >/dev/null 2>&1; then
    break
  fi
  sleep 2
done
docker compose exec -T postgres pg_isready -U homelab -d homelab >/dev/null

echo "Run end-to-end Spark demo..."
docker compose run --rm spark-demo

echo "Check alert JSON files exist..."
ALERT_FILE="$(find data/homelab/curated/alerts -name 'part-*.json' -print -quit)"
test -n "$ALERT_FILE"

echo "Check alert JSON is not empty..."
ALERT_LINES="$(cat data/homelab/curated/alerts/part-*.json | wc -l | tr -d ' ')"
test "$ALERT_LINES" -gt 0

echo "Check PostgreSQL alerts table is not empty..."
COUNT="$(docker compose exec -T postgres psql -U homelab -d homelab -t -A -c 'SELECT COUNT(*) FROM alerts;')"
test "$COUNT" -gt 0

echo "Check Grafana datasource target query..."
docker compose exec -T postgres psql -U homelab -d homelab -c "
SELECT host, severity, root_cause, event_ts
FROM alerts
ORDER BY event_ts DESC
LIMIT 5;
"

echo "Check Grafana HTTP endpoint..."
python - <<'PY'
import urllib.request

with urllib.request.urlopen("http://localhost:3000/api/health", timeout=10) as response:
    body = response.read().decode("utf-8")
    if response.status != 200 or "database" not in body.lower():
        raise SystemExit(f"Unexpected Grafana health response: {response.status} {body}")
PY

echo "OK: Homelab AI Ops pipeline works end-to-end"
