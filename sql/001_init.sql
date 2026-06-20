CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    event_ts TIMESTAMPTZ NOT NULL,
    host TEXT NOT NULL,
    severity TEXT NOT NULL,
    root_cause TEXT NOT NULL,
    cpu_usage DOUBLE PRECISION,
    ram_usage DOUBLE PRECISION,
    disk_usage DOUBLE PRECISION,
    temperature_c DOUBLE PRECISION,
    packet_loss_pct DOUBLE PRECISION,
    db_latency_ms DOUBLE PRECISION,
    api_error_rate DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT alerts_unique_event UNIQUE (event_ts, host, severity, root_cause)
);

CREATE INDEX IF NOT EXISTS idx_alerts_host_ts ON alerts (host, event_ts DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_severity_ts ON alerts (severity, event_ts DESC);
