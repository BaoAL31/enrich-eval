"""CLI: python -m enrich.check — eval tags vs gold, exit 1 if gate fails."""

import sys
from pathlib import Path

from .evaluate import evaluate, gate

ROOT = Path(__file__).resolve().parent.parent
THRESHOLD = 0.85

if __name__ == "__main__":
    result = evaluate(ROOT / "tags.json", ROOT / "corpus" / "gold.json")
    print(f"overall F1: {result['overall_f1']} (gate {THRESHOLD})")
    for t, m in result["per_type"].items():
        print(f"  {t}: P {m['precision']} R {m['recall']} F1 {m['f1']}")
    sys.exit(0 if gate(result, THRESHOLD) else 1)
