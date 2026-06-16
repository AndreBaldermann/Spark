"""Spark Structured Streaming job for the Homelab AI Operations Platform."""

from __future__ import annotations

import argparse
from pathlib import Path

from spark_pipeline import create_spark


def run_file_stream(input_dir: Path, output_dir: Path, checkpoint_dir: Path, once: bool) -> None:
    spark = create_spark()
    try:
        schema = """
            event_type STRING, event_time STRING, host STRING, cpu_usage DOUBLE, ram_usage DOUBLE,
            disk_usage DOUBLE, temperature_c DOUBLE, incoming_mbps DOUBLE, outgoing_mbps DOUBLE,
            packet_loss_pct DOUBLE, db_latency_ms DOUBLE, api_error_rate DOUBLE, level STRING,
            message STRING, service STRING
        """
        events = spark.readStream.schema(schema).json(str(input_dir))
        metrics = events.filter("event_type = 'metrics'").withColumn("event_ts", __import__("pyspark.sql.functions", fromlist=["to_timestamp"]).to_timestamp("event_time"))

        alerts = metrics.selectExpr(
            "event_ts",
            "host",
            "cpu_usage",
            "ram_usage",
            "disk_usage",
            "temperature_c",
            "packet_loss_pct",
            "db_latency_ms",
            "api_error_rate",
            "CASE WHEN cpu_usage >= 95 OR temperature_c >= 82 OR db_latency_ms >= 750 OR api_error_rate >= 0.15 THEN 'critical' "
            "WHEN cpu_usage >= 85 OR ram_usage >= 80 OR disk_usage >= 90 OR packet_loss_pct >= 2 THEN 'warning' ELSE 'info' END AS severity",
            "CASE WHEN cpu_usage >= 85 AND temperature_c >= 80 AND ram_usage < 75 THEN 'thermal_throttling_suspected' "
            "WHEN db_latency_ms >= 600 AND api_error_rate >= 0.10 THEN 'database_latency_causing_api_errors' "
            "WHEN packet_loss_pct >= 2 AND (incoming_mbps >= 150 OR outgoing_mbps >= 150) THEN 'network_saturation_or_packet_loss' "
            "WHEN cpu_usage >= 85 AND ram_usage >= 80 AND outgoing_mbps >= 120 THEN 'backup_or_batch_job_suspected' "
            "WHEN disk_usage >= 92 THEN 'disk_capacity_risk' WHEN cpu_usage >= 85 THEN 'cpu_pressure' ELSE 'no_clear_root_cause' END AS root_cause",
        ).filter("severity != 'info'")

        writer = (
            alerts.writeStream.format("json")
            .outputMode("append")
            .option("path", str(output_dir / "alerts"))
            .option("checkpointLocation", str(checkpoint_dir))
        )
        query = writer.trigger(availableNow=True).start() if once else writer.start()
        query.awaitTermination()
    finally:
        spark.stop()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Spark Structured Streaming over homelab telemetry files.")
    parser.add_argument("--input-dir", type=Path, default=Path("data/homelab/raw"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/homelab/curated"))
    parser.add_argument("--checkpoint-dir", type=Path, default=Path("data/homelab/checkpoints/alerts"))
    parser.add_argument("--once", action="store_true", help="Process currently available files and stop.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_file_stream(args.input_dir, args.output_dir, args.checkpoint_dir, args.once)


if __name__ == "__main__":
    main()
