"""Pipeline tests: determinism, non-destructive originals, dead-letter behaviour."""

import hashlib
import json

from enrich.pipeline import enrich_doc, run_corpus


def test_deterministic_identical_inputs_identical_outputs():
    text = "Invoice INV-10421 issued 15/03/2027. ABN 51 824 753 556. Total $1,200.00."
    assert enrich_doc("a", text) == enrich_doc("a", text)


def test_tags_are_sidecars_not_edits(tmp_path):
    doc = tmp_path / "d.txt"
    doc.write_text("Contact intake@example.com, due 15/03/2027.", encoding="utf-8")
    before = hashlib.sha256(doc.read_bytes()).hexdigest()
    out, dead = tmp_path / "tags.json", tmp_path / "dead.jsonl"
    summary = run_corpus(tmp_path, out, dead)
    assert hashlib.sha256(doc.read_bytes()).hexdigest() == before  # untouched
    assert summary == {"tagged": 1, "dead_lettered": 0}
    assert len(json.loads(out.read_text())) == 1


def test_empty_doc_dead_letters_with_reason(tmp_path):
    (tmp_path / "empty.txt").write_text("lorem ipsum\n", encoding="utf-8")
    out, dead = tmp_path / "tags.json", tmp_path / "dead.jsonl"
    assert run_corpus(tmp_path, out, dead) == {"tagged": 0, "dead_lettered": 1}
    row = json.loads(dead.read_text().strip())
    assert row["reason"] == "no entities extracted"
