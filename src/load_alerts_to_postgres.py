"""Load Spark JSON alert output into the PostgreSQL alerts table."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

ALERT_COLUMNS = [
    "event_ts",
    "host",
    "severity",
    "root_cause",
    "cpu_usage",
    "ram_usage",
    "disk_usage",
    "temperature_c",
    "packet_loss_pct",
    "db_latency_ms",
    "api_error_rate",
]


def iter_alert_files(alerts_path: Path) -> Iterator[Path]:
    """Yield Spark JSON part files or a single JSONL file in deterministic order."""
    if alerts_path.is_file():
        yield alerts_path
        return
    if not alerts_path.exists():
        return
    yield from sorted(path for path in alerts_path.glob("part-*") if path.is_file())


def iter_alert_records(alerts_path: Path) -> Iterator[dict[str, Any]]:
    """Read JSONL alert records from Spark output files."""
    for file_path in iter_alert_files(alerts_path):
        with file_path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                if record.get("severity") and record.get("host") and record.get("event_ts"):
                    yield {column: record.get(column) for column in ALERT_COLUMNS}


def insert_alerts(dsn: str, records: Iterable[dict[str, Any]]) -> int:
    """Insert alert records into PostgreSQL and return the number of new rows."""
    import psycopg

    rows = [tuple(record.get(column) for column in ALERT_COLUMNS) for record in records]
    if not rows:
        return 0

    placeholders = ", ".join(["%s"] * len(ALERT_COLUMNS))
    columns = ", ".join(ALERT_COLUMNS)
    updates = ", ".join(f"{column} = EXCLUDED.{column}" for column in ALERT_COLUMNS[4:])
    query = f"""
        INSERT INTO alerts ({columns})
        VALUES ({placeholders})
        ON CONFLICT (event_ts, host, severity, root_cause)
        DO UPDATE SET {updates}
    """

    with psycopg.connect(dsn) as connection:
        with connection.cursor() as cursor:
            cursor.executemany(query, rows)
        connection.commit()
    return len(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load Spark JSON alerts into PostgreSQL.")
    parser.add_argument("--alerts-path", type=Path, default=Path("data/homelab/curated/alerts"))
    parser.add_argument(
        "--dsn",
        default=os.environ.get("POSTGRES_DSN", "postgresql://homelab:homelab@localhost:5432/homelab"),
        help="PostgreSQL connection string. Defaults to POSTGRES_DSN or local Docker Compose credentials.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    count = insert_alerts(args.dsn, iter_alert_records(args.alerts_path))
    print(f"Loaded {count} alert records into PostgreSQL")


if __name__ == "__main__":
    main()
