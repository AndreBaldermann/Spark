"""Pure-Python anomaly and root-cause rules shared by tests and Spark jobs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TelemetrySnapshot:
    host: str
    cpu_usage: float
    ram_usage: float
    disk_usage: float
    temperature_c: float
    incoming_mbps: float
    outgoing_mbps: float
    packet_loss_pct: float
    db_latency_ms: float
    api_error_rate: float


def severity_score(snapshot: TelemetrySnapshot) -> int:
    """Return a simple additive severity score for operational risk."""
    score = 0
    score += 3 if snapshot.cpu_usage >= 95 else 2 if snapshot.cpu_usage >= 85 else 0
    score += 2 if snapshot.ram_usage >= 90 else 1 if snapshot.ram_usage >= 80 else 0
    score += 2 if snapshot.disk_usage >= 92 else 1 if snapshot.disk_usage >= 85 else 0
    score += 3 if snapshot.temperature_c >= 82 else 1 if snapshot.temperature_c >= 75 else 0
    score += 2 if snapshot.packet_loss_pct >= 3 else 1 if snapshot.packet_loss_pct >= 1 else 0
    score += 2 if snapshot.db_latency_ms >= 750 else 1 if snapshot.db_latency_ms >= 350 else 0
    score += 2 if snapshot.api_error_rate >= 0.15 else 1 if snapshot.api_error_rate >= 0.05 else 0
    return score


def classify_severity(score: int) -> str:
    if score >= 6:
        return "critical"
    if score >= 3:
        return "warning"
    return "info"


def infer_root_cause(snapshot: TelemetrySnapshot) -> str:
    """Infer a human-readable likely root cause from correlated symptoms."""
    if snapshot.cpu_usage >= 85 and snapshot.temperature_c >= 80 and snapshot.ram_usage < 75:
        return "thermal_throttling_suspected"
    if snapshot.db_latency_ms >= 600 and snapshot.api_error_rate >= 0.10:
        return "database_latency_causing_api_errors"
    if snapshot.packet_loss_pct >= 2 and (snapshot.incoming_mbps >= 150 or snapshot.outgoing_mbps >= 150):
        return "network_saturation_or_packet_loss"
    if snapshot.cpu_usage >= 85 and snapshot.ram_usage >= 80 and snapshot.outgoing_mbps >= 120:
        return "backup_or_batch_job_suspected"
    if snapshot.disk_usage >= 92:
        return "disk_capacity_risk"
    if snapshot.cpu_usage >= 85:
        return "cpu_pressure"
    return "no_clear_root_cause"


def is_anomalous(snapshot: TelemetrySnapshot, cpu_mean: float = 30.0, cpu_stddev: float = 15.0) -> bool:
    """Detect anomalies with a baseline threshold plus hard safety limits."""
    dynamic_cpu_limit = cpu_mean + 3 * cpu_stddev
    return any(
        [
            snapshot.cpu_usage > dynamic_cpu_limit,
            snapshot.temperature_c >= 82,
            snapshot.packet_loss_pct >= 3,
            snapshot.db_latency_ms >= 750,
            snapshot.api_error_rate >= 0.15,
            snapshot.disk_usage >= 95,
        ]
    )
