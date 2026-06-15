import json
from pathlib import Path

from src.generate_logs import write_events


def test_write_events_creates_deterministic_jsonl(tmp_path: Path) -> None:
    output = tmp_path / "events.jsonl"

    write_events(rows=3, output=output, seed=7)

    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3
    first = json.loads(lines[0])
    assert first["event_id"] == "evt-00000000"
    assert first["event_time"].startswith("2026-01-01T00:00:00")


def test_write_events_creates_parent_directories(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "events.jsonl"

    write_events(rows=1, output=output)

    assert output.exists()
