# Wiki — enrich-eval

## How to add a new entity type
1. Add a regex + function in `enrich/extractors.py`, register it in `EXTRACTORS`.
2. Extend `corpus/generate.py` so the seeded text contains the entity, and append
   the exact surface form to gold. Fixtures are exact by construction.
3. Add a unit test in `tests/test_extractors.py` (positive + adversarial case,
   e.g. the ABN checksum test that rejects `...557`).
4. Run `pytest -q` — the corpus gate (`test_full_corpus_gate`) must stay green.

## Design rules (do not break)
- Originals are read-only. Tags carry `source_sha256`; `test_tags_are_sidecars_not_edits`
  fails the build if any input byte changes.
- Empty extractions dead-letter with a reason. Never emit empty tag sets.
- Eval is strict exact-match on (type, value). No partial credit.
- Deterministic: no randomness outside `corpus/generate.py` (seed 42). Same
  inputs must produce byte-identical `tags.json`.

## Where ML would plug in
Current extractors are rules. A learned NER model (e.g. spaCy) would replace
individual functions in `EXTRACTORS` behind the same interface; gold fixtures
and the eval gate stay unchanged, so model swaps are measured, not vibes.
Honest limit: no model is bundled — stdlib only, zero dependencies at runtime.
