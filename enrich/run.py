"""CLI: python -m enrich.run — enrich corpus -> tags.json + dead.jsonl."""

from pathlib import Path

from .pipeline import run_corpus

ROOT = Path(__file__).resolve().parent.parent

if __name__ == "__main__":
    summary = run_corpus(ROOT / "corpus", ROOT / "tags.json", ROOT / "dead.jsonl")
    print(summary)
