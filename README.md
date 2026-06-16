# Homelab AI Operations Platform

A portfolio-grade miniature version of Datadog, Splunk, Dynatrace, or New Relic for your own homelab: edge devices generate telemetry, Spark processes the data in near real time, rules detect anomalies, Grafana visualizes alerts, and a local Ollama assistant can explain likely root causes.

## Why This Project Is More Impressive Than a Typical Spark ETL

A classic portfolio project is often just `CSV -> Spark -> CSV`. This project demonstrates a complete operations data platform instead:

```text
Raspberry Pis / Home Server / Containers
        |
        | metrics + logs + network telemetry
        v
Kafka-compatible event bus (Redpanda)
        |
        v
Spark Structured Streaming
        |
        | anomaly detection + root-cause analysis
        v
PostgreSQL history  --->  Grafana dashboards
        |
        v
Ollama / Local LLM Assistant
```

This showcases data engineering, streaming, distributed systems, monitoring, MLOps-oriented thinking, AI integration, and infrastructure expertise.

## Included Features

* Simulated Raspberry Pi / homelab agent generating CPU, RAM, disk, temperature, network, database latency, API errors, and log telemetry.
* Spark Structured Streaming job processing continuous telemetry from a JSONL directory.
* Rule-based anomaly detection as a robust first implementation.
* Root-cause suggestions such as `thermal_throttling_suspected` or `database_latency_causing_api_errors`.
* Docker Compose stack with Redpanda/Kafka, PostgreSQL, Grafana, optional Ollama, and Spark demo containers.
* PostgreSQL schema and Grafana provisioning as a starting point for dashboards.
* Minimal Ollama-powered assistant that translates local alert context into human-readable explanations.

## Quick Start with Docker

Docker is recommended because the Spark container already includes Python 3.11 and OpenJDK 17.

```bash
docker compose build
docker compose up -d redpanda postgres grafana
docker compose run --rm spark-demo
```

Grafana will be available at http://localhost:3000. The default login for a fresh Grafana container is usually `admin` / `admin`.

Optional local LLM service:

```bash
docker compose --profile ai up -d ollama
# then pull a model inside the Ollama container, e.g. llama3.1 or qwen2.5
```

## Local Quick Start Without Docker

Requirements: Python 3.11 and Java/OpenJDK 17. PySpark launches a local JVM; without Java you will encounter a `JAVA_GATEWAY_EXITED` error.

```bash
sudo apt update
sudo apt install openjdk-17-jre-headless python3.11 python3.11-venv
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/homelab_agent.py --minutes 120 --output data/homelab/raw/events.jsonl
python src/homelab_streaming.py --input-dir data/homelab/raw --output-dir data/homelab/curated --once
```

## Example Chatbot Query

If Ollama is running and alert context exists:

```bash
python src/ai_assistant.py "Why is Pi 3 running slowly?" --context data/homelab/curated/alerts --model llama3.1
```

The assistant builds a prompt from local alert data and queries your local Ollama model.

## Project Structure

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
│   ├── homelab/rules.py
│   └── spark_pipeline.py
└── tests/
```

## Roadmap for a Real Homelab Deployment

1. **Real Agents:** Install a lightweight systemd service on each Raspberry Pi to send `psutil` metrics and relevant log entries.
2. **Kafka Topics:** Separate `metrics`, `logs`, `network`, and `alerts`, and add a Schema Registry.
3. **Spark Streaming:** Enable Kafka as a source and introduce watermarks and windowed aggregations.
4. **Persistence:** Store alerts and aggregated metrics in PostgreSQL or TimescaleDB.
5. **Grafana:** Expand dashboards with host health, top root causes, error budgets, and network diagnostics.
6. **Machine Learning:** Extend rule-based detection with Isolation Forest, DBSCAN, or Autoencoders.
7. **AI Assistant:** Add retrieval over historical alerts and logs, then generate responses using a local Ollama model.
