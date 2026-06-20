from src.load_alerts_to_postgres import ensure_alerts_schema


class RecordingCursor:
    def __init__(self) -> None:
        self.statements: list[str] = []

    def execute(self, statement: str) -> None:
        self.statements.append(" ".join(statement.split()))


def test_ensure_alerts_schema_creates_unique_index_for_conflict_target() -> None:
    cursor = RecordingCursor()

    ensure_alerts_schema(cursor)

    joined = "\n".join(cursor.statements)
    assert "CREATE TABLE IF NOT EXISTS alerts" in joined
    assert "CREATE UNIQUE INDEX IF NOT EXISTS alerts_unique_event_idx" in joined
    assert "ON alerts (event_ts, host, severity, root_cause)" in joined
