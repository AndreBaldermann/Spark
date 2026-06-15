"""Generate deterministic fake web-log events for the Spark demo pipeline."""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

PAGES = ["/", "/pricing", "/docs", "/blog", "/login", "/checkout"]
STATUS_CODES = [200, 200, 200, 200, 201, 204, 301, 404, 500, 503]
USER_AGENTS = ["Chrome", "Firefox", "Safari", "Edge", "Bot"]


def build_event(index: int, rng: random.Random, start: datetime) -> dict[str, Any]:
    """Build one synthetic event with occasional invalid fields for cleaning demos."""
    event_time = start + timedelta(seconds=index * rng.randint(1, 7))
    status_code = rng.choice(STATUS_CODES)

    event: dict[str, Any] = {
        "event_id": f"evt-{index:08d}",
        "event_time": event_time.isoformat(),
        "user_id": f"user-{rng.randint(1, 2500):05d}",
        "page": rng.choice(PAGES),
        "status_code": status_code,
        "latency_ms": rng.randint(20, 2500),
        "user_agent": rng.choice(USER_AGENTS),
    }

    if index % 97 == 0:
        event["user_id"] = None
    if index % 131 == 0:
        event["status_code"] = 0
    if index % 173 == 0:
        event["latency_ms"] = -1

    return event


def write_events(rows: int, output: Path, seed: int = 42) -> None:
    """Write JSON Lines events to ``output``."""
    output.parent.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)

    with output.open("w", encoding="utf-8") as handle:
        for index in range(rows):
            handle.write(json.dumps(build_event(index, rng, start), sort_keys=True))
            handle.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate fake web-log events.")
    parser.add_argument("--rows", type=int, default=100_000, help="Number of events to generate.")
    parser.add_argument("--output", type=Path, default=Path("data/raw/events.jsonl"), help="Output JSONL file.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.rows < 1:
        raise ValueError("--rows must be greater than zero")
    write_events(args.rows, args.output, args.seed)
    print(f"Wrote {args.rows} events to {args.output}")


if __name__ == "__main__":
    main()
