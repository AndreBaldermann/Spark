FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless procps \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PYTHONPATH=/app

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["bash", "-lc", "python src/homelab_agent.py --minutes 120 --output data/homelab/raw/events.jsonl && python src/homelab_streaming.py --input-dir data/homelab/raw --output-dir data/homelab/curated --once && python src/load_alerts_to_postgres.py --alerts-path data/homelab/curated/alerts"]
