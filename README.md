# Enrich-Eval — document-enrichment quality harness (Nuix-shaped)

Deterministic enrichment pipeline over synthetic unstructured docs (invoices,
emails, reports) plus a precision/recall eval gate — the shape of production
AI data-enrichment work: find, identify, and codify data without touching originals.

## Run
```
pip install -r requirements.txt
python corpus/generate.py          # seeded corpus + gold labels (25 docs)
python -m enrich.run               # enrich -> tags.json + dead.jsonl
python -m enrich.check             # eval vs gold, gate F1 >= 0.85
pytest -q
```

## What it proves
- Entity extraction (email, AU phone, ABN with real checksum validation, dates,
  money, invoice numbers) + record-type classification, stdlib only
- Non-destructive by design: tags are sidecars with source hashes; originals verified untouched
- Fail-closed: zero-entity docs dead-letter with reasons, never silent gaps
- Deterministic: identical inputs -> identical outputs (rerun-safe, verified by test)
- Quality bar as code: strict exact-match P/R/F1 per type, CI gate at 0.85
- Honest limits: rule-based extractors, not ML models — documented in wiki with
  guidance on where a learned NER model would plug in

## Docs
- `docs/wiki.md` — how to add a new entity type (extract, fixture, gate)
