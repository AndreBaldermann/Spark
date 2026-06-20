from pathlib import Path

from src.ai_assistant import build_prompt, read_context


def test_read_context_supports_spark_output_directory(tmp_path: Path) -> None:
    alerts = tmp_path / "alerts"
    alerts.mkdir()
    (alerts / "part-00000.json").write_text('{"host":"pi-3","root_cause":"thermal"}\n', encoding="utf-8")

    context = read_context(alerts)

    assert "pi-3" in context
    assert "thermal" in build_prompt("Warum ist Pi 3 langsam?", alerts)
