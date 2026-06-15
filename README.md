# Spark Portfolio Toy System: Web Log Analytics

Dieses Repository enthält ein kleines, bewerbungstaugliches Demo-System für eine skalierbare Data-Engineering-Pipeline mit PySpark. Es simuliert Web-Log-Events, bereinigt fehlerhafte Datensätze, berechnet typische Business-Metriken und schreibt die Ergebnisse in Parquet.

## Warum dieses Projekt in Bewerbungen punktet

Das Projekt zeigt zentrale Fähigkeiten für Data-Engineering- und Big-Data-Rollen:

- Aufbau einer reproduzierbaren Batch-Pipeline mit Apache Spark.
- Generierung großer, realistischer Testdaten ohne externe Abhängigkeiten.
- Data Cleaning und Validierung von Eventdaten.
- Aggregationen für Nutzer, Top-Seiten und Fehlerraten.
- Speicherung analytischer Ergebnisse im spaltenbasierten Parquet-Format.
- Lokale Ausführung per Docker oder direkt mit Python.

## Architektur

```text
+------------------+      +----------------------+      +-------------------+
| Fake Log Events  | ---> | PySpark ETL Pipeline | ---> | Parquet Outputs   |
| JSONL generator  |      | clean + aggregate    |      | metrics by hour   |
+------------------+      +----------------------+      +-------------------+
```

## Projektstruktur

```text
.
├── docker-compose.yml
├── requirements.txt
├── src/
│   ├── generate_logs.py
│   └── spark_pipeline.py
└── tests/
    └── test_generate_logs.py
```

## Schnellstart ohne Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/generate_logs.py --rows 10000 --output data/raw/events.jsonl
python src/spark_pipeline.py --input data/raw/events.jsonl --output data/curated
```

## Schnellstart mit Docker

```bash
docker compose run --rm spark-demo python src/generate_logs.py --rows 10000 --output data/raw/events.jsonl
docker compose run --rm spark-demo python src/spark_pipeline.py --input data/raw/events.jsonl --output data/curated
```

## Ergebnisdaten

Die Pipeline schreibt drei Parquet-Datasets:

- `data/curated/users_per_hour`: eindeutige Nutzer pro Stunde.
- `data/curated/top_pages`: Seiten nach Anzahl gültiger Events.
- `data/curated/error_rates`: Fehlerrate pro HTTP-Statusklasse.

## Beispieltext für den Lebenslauf

> Aufbau einer lokalen Big-Data-Demo-Pipeline mit Docker, PySpark und Parquet zur Simulation skalierbarer Web-Log-Analysen inklusive Datenbereinigung, Aggregationen und reproduzierbarer Ausführung.

## Nächste sinnvolle Erweiterungen

- Notebook oder Streamlit-Dashboard für Visualisierung.
- Benchmark-Tabelle für verschiedene Datenmengen.
- Structured-Streaming-Variante mit Kafka-kompatiblem Event-Producer.
- CI-Workflow für Tests und Codequalität.
