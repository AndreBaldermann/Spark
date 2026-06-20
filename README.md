# Homelab AI Operations Platform

Eine bewerbungsstarke Mini-Version von Datadog, Splunk, Dynatrace oder New Relic für dein eigenes Homelab: Edge-Geräte erzeugen Telemetrie, Spark verarbeitet die Daten nahezu in Echtzeit, Regeln erkennen Anomalien, Grafana visualisiert Alerts und ein lokaler Ollama-Assistent kann Ursachen erklären.

## Warum dieses Projekt stärker wirkt als ein normaler Spark-ETL

Ein klassisches Portfolio-Projekt ist oft nur `CSV -> Spark -> CSV`. Dieses Projekt zeigt dagegen eine komplette Operations-Datenplattform:

```text
Raspberry Pis / Homeserver / Container
        |
        | metrics + logs + network telemetry
        v
Kafka-compatible event bus (Redpanda)
        |
        v
Spark Structured Streaming
        |
        | anomaly detection + root-cause guesses
        v
PostgreSQL history  --->  Grafana dashboards
        |
        v
Ollama / local LLM assistant
```

Damit demonstrierst du Data Engineering, Streaming, Distributed Systems, Monitoring, MLOps-nahe Denkweise, AI-Integration und Infrastruktur-Know-how.

## Enthaltene Features

- Simulierter Pi-/Homeserver-Agent für CPU, RAM, Disk, Temperatur, Netzwerk, Datenbanklatenz, API-Fehler und Logs.
- Spark-Structured-Streaming-Job für laufende Telemetriedaten aus einem JSONL-Verzeichnis.
- Regelbasierte Anomalie-Erkennung als robuste erste Version.
- Root-Cause-Vermutungen, z. B. `thermal_throttling_suspected` oder `database_latency_causing_api_errors`.
- Docker Compose Stack mit Redpanda/Kafka, PostgreSQL, Grafana, optional Ollama und Spark-Demo-Container.
- PostgreSQL-Schema, Grafana-Provisioning und ein Loader, der Spark-JSON-Alerts in die `alerts`-Tabelle schreibt.
- Minimaler Ollama-Assistent, der lokale Alert-Kontexte in eine Antwort übersetzt.

## Schnellstart mit Docker

Docker ist empfohlen, weil der Spark-Container Python 3.11 und OpenJDK 17 enthält.

```bash
docker compose build
docker compose up -d redpanda postgres grafana
docker compose run --rm spark-demo
```

Grafana läuft danach auf <http://localhost:3000>. Standard-Login bei frischen Grafana-Containern ist meist `admin` / `admin`.

Optionaler lokaler LLM-Service:

```bash
docker compose --profile ai up -d ollama
# danach im Ollama-Container ein Modell ziehen, z. B. llama3.1 oder qwen2.5
```

## Lokaler Schnellstart ohne Docker

Voraussetzungen: Python 3.11 und Java/OpenJDK 17. PySpark startet lokal eine JVM; ohne Java erscheint sonst ein `JAVA_GATEWAY_EXITED`-Fehler.

```bash
sudo apt update
sudo apt install openjdk-17-jre-headless python3.11 python3.11-venv
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/homelab_agent.py --minutes 120 --output data/homelab/raw/events.jsonl
python src/homelab_streaming.py --input-dir data/homelab/raw --output-dir data/homelab/curated --once
python src/load_alerts_to_postgres.py --alerts-path data/homelab/curated/alerts
```

## End-to-End Smoke Test

Vor einem Bewerbungs-Screenshot oder Demo-Video kannst du den kompletten Docker-Pfad prüfen:

```bash
./scripts/smoke_test.sh
```

Der Smoke Test baut den Spark-Container, startet Redpanda, PostgreSQL und Grafana, erzeugt Telemetrie, führt Spark Structured Streaming aus, lädt JSON-Alerts nach PostgreSQL und prüft, dass Grafana über die PostgreSQL-Zieldaten Daten sehen kann.

## Beispiel: Chatbot-Frage

Wenn Ollama läuft und Alert-Kontext vorhanden ist:

```bash
python src/ai_assistant.py "Warum ist Pi 3 langsam?" --context data/homelab/curated/alerts --model llama3.1
```

Der Assistent baut aus lokalen Alert-Daten einen Prompt und fragt dein lokales Ollama-Modell.

## Projektstruktur

```text
.
├── Dockerfile
├── docker-compose.yml
├── grafana/
├── sql/
│   └── 001_init.sql
├── src/
│   ├── ai_assistant.py
│   ├── homelab_agent.py
│   ├── homelab_streaming.py
│   ├── load_alerts_to_postgres.py
│   ├── homelab/rules.py
│   └── spark_pipeline.py
└── tests/
```

## Roadmap für eine echte Homelab-Installation

1. **Echte Agents:** Auf jedem Raspberry Pi einen kleinen systemd-Service installieren, der `psutil`-Metriken und relevante Logzeilen sendet.
2. **Kafka Topics:** `metrics`, `logs`, `network`, `alerts` trennen und Schema Registry ergänzen.
3. **Spark Streaming:** Kafka-Quelle aktivieren, Watermarks und Fensteraggregationen einbauen.
4. **Persistenz:** Alerts werden bereits nach PostgreSQL geladen; als nächster Schritt können aggregierte Metriken nach PostgreSQL oder TimescaleDB geschrieben werden.
5. **Grafana:** Panels für Host-Zustand, Top-Root-Causes, Error Budgets und Netzwerkprobleme ausbauen.
6. **ML:** Regelbasierte Erkennung durch Isolation Forest, DBSCAN oder Autoencoder ergänzen.
7. **AI Assistant:** Retrieval über historische Alerts und Logs, dann lokale Ollama-Antworten.

## Lebenslauf-Text

> Entwickelte eine verteilte Observability-Plattform mit Apache Spark Structured Streaming und Kafka-kompatiblem Event-Bus zur Echtzeit-Analyse von Telemetriedaten von Edge-Geräten. Implementierte Anomalie-Erkennung, Root-Cause-Vermutungen, Alerting-Grundlagen, PostgreSQL-Historisierung, Grafana-Dashboards und einen lokalen LLM-Assistenten für Infrastrukturfragen.
