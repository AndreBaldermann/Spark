"""PySpark ETL pipeline for web-log analytics."""

from __future__ import annotations

import argparse
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


def create_spark() -> SparkSession:
    return (
        SparkSession.builder.appName("portfolio-web-log-analytics")
        .master("local[*]")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


def clean_events(events: DataFrame) -> DataFrame:
    """Keep valid events and add analysis columns."""
    return (
        events.withColumn("event_ts", F.to_timestamp("event_time"))
        .filter(F.col("event_ts").isNotNull())
        .filter(F.col("user_id").isNotNull())
        .filter(F.col("page").isNotNull())
        .filter(F.col("status_code").between(100, 599))
        .filter(F.col("latency_ms") >= 0)
        .withColumn("event_hour", F.date_trunc("hour", F.col("event_ts")))
        .withColumn("status_family", (F.col("status_code") / 100).cast("int") * 100)
    )


def users_per_hour(events: DataFrame) -> DataFrame:
    return events.groupBy("event_hour").agg(F.countDistinct("user_id").alias("unique_users"))


def top_pages(events: DataFrame) -> DataFrame:
    return events.groupBy("page").agg(F.count("*").alias("events")).orderBy(F.desc("events"))


def error_rates(events: DataFrame) -> DataFrame:
    total_events = F.count("*")
    error_events = F.sum(F.when(F.col("status_code") >= 500, 1).otherwise(0))
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
