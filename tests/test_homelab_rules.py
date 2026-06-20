from src.homelab.rules import TelemetrySnapshot, classify_severity, infer_root_cause, is_anomalous, severity_score


def test_thermal_root_cause_is_detected() -> None:
    snapshot = TelemetrySnapshot(
        host="pi-3",
        cpu_usage=97,
        ram_usage=45,
        disk_usage=70,
        temperature_c=86,
        incoming_mbps=20,
        outgoing_mbps=30,
        packet_loss_pct=0.1,
        db_latency_ms=80,
        api_error_rate=0.01,
    )

    assert is_anomalous(snapshot)
    assert classify_severity(severity_score(snapshot)) == "critical"
    assert infer_root_cause(snapshot) == "thermal_throttling_suspected"


def test_database_latency_root_cause_is_detected() -> None:
    snapshot = TelemetrySnapshot(
        host="homeserver",
        cpu_usage=55,
        ram_usage=62,
        disk_usage=60,
        temperature_c=54,
        incoming_mbps=30,
        outgoing_mbps=30,
        packet_loss_pct=0.2,
        db_latency_ms=900,
        api_error_rate=0.2,
    )

    assert is_anomalous(snapshot)
    assert infer_root_cause(snapshot) == "database_latency_causing_api_errors"
