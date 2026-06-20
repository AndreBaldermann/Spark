import json
from pathlib import Path

from src.load_alerts_to_postgres import ALERT_COLUMNS, iter_alert_files, iter_alert_records


def test_iter_alert_records_reads_spark_part_files(tmp_path: Path) -> None:
    alerts = tmp_path / "alerts"
    alerts.mkdir()
    (alerts / "_SUCCESS").write_text("", encoding="utf-8")
    (alerts / "part-00001.json").write_text("\n", encoding="utf-8")
    (alerts / "part-00000.json").write_text(
        json.dumps(
            {
                "event_ts": "2026-06-16T10:25:00.000Z",
                "host": "pi-3",
                "severity": "critical",
                "root_cause": "thermal_throttling_suspected",
                "cpu_usage": 98.2,
                "temperature_c": 85.1,
                "extra_field": "ignored",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    records = list(iter_alert_records(alerts))

    assert len(records) == 1
    assert records[0]["host"] == "pi-3"
    assert records[0]["root_cause"] == "thermal_throttling_suspected"
    assert set(records[0]) == set(ALERT_COLUMNS)


def test_iter_alert_files_accepts_single_jsonl_file(tmp_path: Path) -> None:
    file_path = tmp_path / "alerts.jsonl"
    file_path.write_text("{}\n", encoding="utf-8")

    assert list(iter_alert_files(file_path)) == [file_path]
