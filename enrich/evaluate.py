"""Eval: precision / recall / F1 per entity type against gold labels.

A predicted entity counts as a true positive only on exact (type, value)
match — strict, reproducible, no partial-credit vibes. `gate()` fails CI
when overall F1 drops below threshold.
"""

from __future__ import annotations

import json
from pathlib import Path


def key(entity: dict) -> tuple:
    return (entity["type"], entity["value"].strip())


def score(predicted: list[dict], gold: list[dict]) -> dict:
    per_type: dict[str, dict] = {}
    types = {e["type"] for e in predicted} | {e["type"] for e in gold}
    for t in sorted(types):
        p = {key(e) for e in predicted if e["type"] == t}
        g = {key(e) for e in gold if e["type"] == t}
        tp = len(p & g)
        precision = tp / len(p) if p else 1.0
        recall = tp / len(g) if g else 1.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        per_type[t] = {"precision": round(precision, 4), "recall": round(recall, 4),
                       "f1": round(f1, 4), "predicted": len(p), "gold": len(g)}
    tp_all = sum(1 for e in predicted if key(e) in {key(g) for g in gold})
    p_all, g_all = len(predicted), len(gold)
    precision = tp_all / p_all if p_all else 1.0
    recall = tp_all / g_all if g_all else 1.0
    overall = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"per_type": per_type, "overall_f1": round(overall, 4)}


def evaluate(tags_path: Path, gold_path: Path) -> dict:
    tags = {t["doc_id"]: t for t in json.loads(Path(tags_path).read_text(encoding="utf-8"))}
    gold_docs = json.loads(Path(gold_path).read_text(encoding="utf-8"))
    predicted = [e for doc_id, t in tags.items() for e in t["entities"]]
    gold = [e for d in gold_docs for e in d["entities"]]
    result = score(predicted, gold)
    result["docs_tagged"] = len(tags)
    result["docs_gold"] = len(gold_docs)
    return result


def gate(result: dict, threshold: float = 0.85) -> bool:
    return result["overall_f1"] >= threshold
