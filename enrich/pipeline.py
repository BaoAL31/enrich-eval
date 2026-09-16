"""Enrichment pipeline: docs in -> sidecar tags out, originals never touched.

A document with zero extracted entities dead-letters with a reason instead
of emitting an empty tag set (fail-closed: no silent gaps downstream).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .extractors import EXTRACTORS, classify_record


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def enrich_doc(doc_id: str, text: str) -> dict:
    entities = []
    for etype, fn in EXTRACTORS.items():
        entities.extend(fn(text))
    entities.sort(key=lambda e: (e["span"][0], e["type"]))
    record_type = classify_record(text)
    return {"doc_id": doc_id, "record_type": record_type, "entities": entities}


def run_corpus(corpus_dir: Path, out_path: Path, dead_path: Path) -> dict:
    corpus_dir = Path(corpus_dir)
    tagged, dead = [], []
    for doc_file in sorted(corpus_dir.glob("*.txt")):
        text = doc_file.read_text(encoding="utf-8")
        result = enrich_doc(doc_file.stem, text)
        result["source_sha256"] = sha256_file(doc_file)
        if not result["entities"]:
            dead.append({"doc_id": result["doc_id"], "reason": "no entities extracted"})
        else:
            tagged.append(result)
    out_path.write_text(json.dumps(tagged, indent=2), encoding="utf-8")
    dead_path.write_text("\n".join(json.dumps(d) for d in dead), encoding="utf-8")
    return {"tagged": len(tagged), "dead_lettered": len(dead)}
