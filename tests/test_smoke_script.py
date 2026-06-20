from pathlib import Path


def test_smoke_script_covers_end_to_end_pipeline() -> None:
    script = Path("scripts/smoke_test.sh").read_text(encoding="utf-8")

    assert "docker compose build spark-demo" in script
    assert "docker compose up -d postgres grafana redpanda" in script
    assert "docker compose run --rm spark-demo" in script
    assert "SELECT COUNT(*) FROM alerts" in script
    assert "http://localhost:3000/api/health" in script
