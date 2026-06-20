"""PySpark ETL pipeline for web-log analytics."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession

SUPPORTED_PYTHON_MAJOR = 3
MAX_SUPPORTED_PYTHON_MINOR = 11


def validate_runtime_environment() -> None:
    """Fail early with actionable setup hints before Spark starts its Java gateway."""
    if sys.version_info[:2] > (SUPPORTED_PYTHON_MAJOR, MAX_SUPPORTED_PYTHON_MINOR):
        raise SystemExit(
            "PySpark 3.5.x is intended for Python 3.8-3.11 in this demo. "
            "Please create the virtual environment with Python 3.11, for example: "
            "python3.11 -m venv .venv"
        )

    if shutil.which("java") is None:
        raise SystemExit(
            "Java was not found, but PySpark needs a JVM. Install OpenJDK 17 and set JAVA_HOME. "
            "On Ubuntu/Debian: sudo apt install openjdk-17-jre-headless && "
            "export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64"
        )

    if not os.environ.get("JAVA_HOME"):
        print(
            "Warning: JAVA_HOME is not set. If Spark cannot start, set it to your JDK/JRE path, "
            "for example: export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64",
            file=sys.stderr,
        )


def load_pyspark() -> tuple[Any, Any, Any]:
    """Import PySpark lazily so missing setup produces a helpful CLI error."""
    try:
        from pyspark.sql import DataFrame, SparkSession, functions as F
    except ModuleNotFoundError as exc:
        if exc.name == "pyspark":
            raise SystemExit("PySpark is not installed. Run: pip install -r requirements.txt") from exc
        raise
    return DataFrame, SparkSession, F


def create_spark() -> "SparkSession":
    validate_runtime_environment()
    _, spark_session, _ = load_pyspark()
    return (
        spark_session.builder.appName("portfolio-web-log-analytics")
        .master("local[*]")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


def clean_events(events: "DataFrame") -> "DataFrame":
    """Keep valid events and add analysis columns."""
    _, _, functions = load_pyspark()
    return (
        events.withColumn("event_ts", functions.to_timestamp("event_time"))
        .filter(functions.col("event_ts").isNotNull())
        .filter(functions.col("user_id").isNotNull())
        .filter(functions.col("page").isNotNull())
        .filter(functions.col("status_code").between(100, 599))
        .filter(functions.col("latency_ms") >= 0)
        .withColumn("event_hour", functions.date_trunc("hour", functions.col("event_ts")))
        .withColumn("status_family", (functions.col("status_code") / 100).cast("int") * 100)
    )


def users_per_hour(events: "DataFrame") -> "DataFrame":
    _, _, functions = load_pyspark()
    return events.groupBy("event_hour").agg(functions.countDistinct("user_id").alias("unique_users"))


def top_pages(events: "DataFrame") -> "DataFrame":
    _, _, functions = load_pyspark()
    return events.groupBy("page").agg(functions.count("*").alias("events")).orderBy(functions.desc("events"))


def error_rates(events: "DataFrame") -> "DataFrame":
    _, _, functions = load_pyspark()
    total_events = functions.count("*")
    error_events = functions.sum(functions.when(functions.col("status_code") >= 500, 1).otherwise(0))
    return events.groupBy("status_family").agg(
        total_events.alias("events"),
        error_events.alias("server_errors"),
        (error_events / total_events).alias("server_error_rate"),
    )


def run_pipeline(input_path: Path, output_path: Path) -> None:
    spark = create_spark()
    try:
        raw_events = spark.read.json(str(input_path))
        clean = clean_events(raw_events).cache()

        output_path.mkdir(parents=True, exist_ok=True)
        users_per_hour(clean).write.mode("overwrite").parquet(str(output_path / "users_per_hour"))
        top_pages(clean).write.mode("overwrite").parquet(str(output_path / "top_pages"))
        error_rates(clean).write.mode("overwrite").parquet(str(output_path / "error_rates"))
    finally:
        spark.stop()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Spark web-log analytics pipeline.")
    parser.add_argument("--input", type=Path, default=Path("data/raw/events.jsonl"), help="Input JSONL file.")
    parser.add_argument("--output", type=Path, default=Path("data/curated"), help="Output directory for Parquet datasets.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_pipeline(args.input, args.output)
    print(f"Wrote curated Parquet datasets to {args.output}")


if __name__ == "__main__":
    main()
