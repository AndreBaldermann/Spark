"""Minimal Ollama-backed assistant prompt builder for homelab root-cause questions."""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path


def read_context(context_path: Path) -> str:
    """Read alert context from one file or from Spark JSON output files in a directory."""
    if not context_path.exists():
        return "No local alert context found."
    if context_path.is_file():
        return context_path.read_text(encoding="utf-8")
    chunks: list[str] = []
    for file_path in sorted(context_path.glob("part-*"))[:20]:
        chunks.append(file_path.read_text(encoding="utf-8"))
    return "\n".join(chunks) if chunks else "No alert files found in the context directory."


def build_prompt(question: str, context_path: Path) -> str:
    context = read_context(context_path)
    return (
        "You are a homelab SRE assistant. Answer using only the telemetry context.\n\n"
        f"Question: {question}\n\nTelemetry context:\n{context[:6000]}"
    )


def ask_ollama(prompt: str, model: str = "llama3.1", url: str = "http://localhost:11434/api/generate") -> str:
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    request = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))
    return str(data.get("response", ""))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ask the local Ollama assistant about homelab alerts.")
    parser.add_argument("question")
    parser.add_argument("--context", type=Path, default=Path("data/homelab/curated/alerts"))
    parser.add_argument("--model", default="llama3.1")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    prompt = build_prompt(args.question, args.context)
    print(ask_ollama(prompt, args.model))


if __name__ == "__main__":
    main()
