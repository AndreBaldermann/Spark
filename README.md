# Spark Portfolio Toy System: Web Log Analytics

This repository contains a small, portfolio-ready demo system for a scalable data engineering pipeline built with PySpark. It simulates web log events, cleans invalid records, calculates common business metrics, and writes the results to Parquet.

## Why This Project Stands Out in Job Applications

This project demonstrates key skills relevant to data engineering and big data roles:

* Building a reproducible batch-processing pipeline with Apache Spark.
* Generating large, realistic test datasets without external dependencies.
* Data cleaning and validation of event data.
* Aggregations for user metrics, top pages, and error rates.
* Storing analytical results in the columnar Parquet format.
* Local execution via Docker or directly with Python.

## Architecture

```text
+------------------+      +----------------------+      +-------------------+
| Fake Log Events  | ---> | PySpark ETL Pipeline | ---> | Parquet Outputs   |
| JSONL generator  |      | clean + aggregate    |      | metrics by hour   |
+------------------+      +----------------------+      +-------------------+
```

## Project Structure

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

## Quick Start Without Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/generate_logs.py --rows 10000 --output data/raw/events.jsonl
python src/spark_pipeline.py --input data/raw/events.jsonl --output data/curated
```

## Quick Start With Docker

```bash
docker compose run --rm spark-demo python src/generate_logs.py --rows 10000 --output data/raw/events.jsonl
docker compose run --rm spark-demo python src/spark_pipeline.py --input data/raw/events.jsonl --output data/curated
```

## Output Data

The pipeline generates three Parquet datasets:

* `data/curated/users_per_hour` — unique users per hour.
* `data/curated/top_pages` — pages ranked by valid event count.
* `data/curated/error_rates` — error rates grouped by HTTP status class.

## Resume Example

> Built a local big-data demonstration pipeline using Docker, PySpark, and Parquet to simulate scalable web log analytics, including data cleansing, aggregations, and reproducible execution.

## Recommended Next Enhancements

* Add a Notebook or Streamlit dashboard for visualization.
* Include benchmark results for different dataset sizes.
* Implement a Structured Streaming version with a Kafka-compatible event producer.
* Add a CI workflow for testing and code quality validation.
