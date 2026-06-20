import json
from pathlib import Path

from src.homelab_agent import write_demo_events


def test_write_demo_events_contains_metrics_and_logs(tmp_path: Path) -> None:
    output = tmp_path / "homelab" / "events.jsonl"

    write_demo_events(output, minutes=3, seed=1)

    events = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    event_types = {event["event_type"] for event in events}
    assert "metrics" in event_types
    assert "logs" in event_types
    assert {"pi-1", "pi-2", "pi-3"}.issubset({event["host"] for event in events})
