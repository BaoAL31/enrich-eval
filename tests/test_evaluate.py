"""Eval tests: scoring math + full-corpus gate (the CI quality bar)."""

from pathlib import Path

from enrich.evaluate import evaluate, gate, score

ROOT = Path(__file__).resolve().parent.parent


def test_score_math():
    gold = [{"type": "email", "value": "a@x.com"}, {"type": "email", "value": "b@x.com"}]
    pred = [{"type": "email", "value": "a@x.com"}, {"type": "email", "value": "zzz@x.com"}]
    r = score(pred, gold)["per_type"]["email"]
    assert (r["precision"], r["recall"], r["f1"]) == (0.5, 0.5, 0.5)


def test_strict_exact_match():
    r = score([{"type": "money", "value": "$500.00"}], [{"type": "money", "value": "$500"}])
    assert r["per_type"]["money"]["f1"] == 0.0


def test_full_corpus_gate():
    from enrich.pipeline import run_corpus
    import subprocess
    import sys
    subprocess.run([sys.executable, "corpus/generate.py"], cwd=ROOT, check=True)
    summary = run_corpus(ROOT / "corpus", ROOT / "tags.json", ROOT / "dead.jsonl")
    assert summary == {"tagged": 24, "dead_lettered": 1}
    result = evaluate(ROOT / "tags.json", ROOT / "corpus" / "gold.json")
    print("\noverall F1:", result["overall_f1"],
          "| per-type:", {k: v["f1"] for k, v in result["per_type"].items()})
    assert gate(result, 0.85), result
