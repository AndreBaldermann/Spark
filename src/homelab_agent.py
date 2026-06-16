"""Generate Raspberry-Pi-like telemetry for local homelab operations demos."""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

HOSTS = ["pi-1", "pi-2", "pi-3", "homeserver", "nas-1"]
LOG_MESSAGES = [
    ("INFO", "health check ok"),
    ("INFO", "container heartbeat"),
    ("WARN", "high memory watermark"),
    ("ERROR", "connection timeout to database"),
    ("WARN", "thermal throttling detected"),
]


def metric_event(host: str, timestamp: datetime, rng: random.Random, spike: bool) -> dict[str, object]:
    cpu = rng.uniform(10, 45)
    ram = rng.uniform(20, 70)
    temp = rng.uniform(42, 64)
    incoming = rng.uniform(5, 80)
    outgoing = rng.uniform(3, 60)
    packet_loss = rng.uniform(0, 0.8)
    db_latency = rng.uniform(20, 180)
    api_errors = rng.uniform(0, 0.03)

    if spike and host == "pi-3":
        cpu = rng.uniform(92, 99)
        temp = rng.uniform(82, 88)
        outgoing = rng.uniform(120, 210)
    if spike and host == "homeserver":
        db_latency = rng.uniform(750, 1300)
        api_errors = rng.uniform(0.15, 0.35)

    return {
        "event_type": "metrics",
        "event_time": timestamp.isoformat(),
        "host": host,
        "cpu_usage": round(cpu, 2),
        "ram_usage": round(ram, 2),
        "disk_usage": round(rng.uniform(35, 96), 2),
        "temperature_c": round(temp, 2),
        "incoming_mbps": round(incoming, 2),
        "outgoing_mbps": round(outgoing, 2),
        "packet_loss_pct": round(packet_loss, 2),
        "db_latency_ms": round(db_latency, 2),
        "api_error_rate": round(api_errors, 4),
    }


def log_event(host: str, timestamp: datetime, rng: random.Random, spike: bool) -> dict[str, object]:
    level, message = rng.choice(LOG_MESSAGES)
    if spike and host == "pi-3":
        level, message = "WARN", "thermal throttling detected"
    if spike and host == "homeserver":
        level, message = "ERROR", "connection timeout to database"
    return {
        "event_type": "logs",
        "event_time": timestamp.isoformat(),
        "host": host,
        "level": level,
        "message": message,
        "service": rng.choice(["api", "postgres", "ollama", "nginx", "backup"]),
    }


def write_demo_events(output: Path, minutes: int = 60, seed: int = 7) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    start = datetime(2026, 6, 16, 10, 0, tzinfo=timezone.utc)
    with output.open("w", encoding="utf-8") as handle:
        for minute in range(minutes):
            timestamp = start + timedelta(minutes=minute)
            spike = 25 <= minute <= 34
            for host in HOSTS:
                handle.write(json.dumps(metric_event(host, timestamp, rng, spike), sort_keys=True) + "\n")
                if rng.random() < 0.45 or spike:
                    handle.write(json.dumps(log_event(host, timestamp, rng, spike), sort_keys=True) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate homelab telemetry events.")
    parser.add_argument("--output", type=Path, default=Path("data/homelab/raw/events.jsonl"))
    parser.add_argument("--minutes", type=int, default=120)
    parser.add_argument("--seed", type=int, default=7)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    write_demo_events(args.output, args.minutes, args.seed)
    print(f"Wrote homelab telemetry to {args.output}")


if __name__ == "__main__":
    main()
