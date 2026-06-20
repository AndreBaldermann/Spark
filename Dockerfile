FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PYTHONPATH=/app

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["bash", "-lc", "python src/generate_logs.py --rows 10000 --output data/raw/events.jsonl && python src/spark_pipeline.py --input data/raw/events.jsonl --output data/curated"]
