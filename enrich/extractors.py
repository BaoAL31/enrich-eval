"""Deterministic entity extractors (stdlib only — no models, no API keys).

Each extractor returns a list of {"type", "value", "span"} dicts.
Spans are (start, end) offsets into the original text so tags stay
non-destructive: originals are never modified, tags live in sidecars.
"""

from __future__ import annotations

import re

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"\b(?:\+61\s?|\(0|\()?0?[23478](?:[\s-]?\d){8}\b")
ABN_RE = re.compile(r"\b\d{2}\s?\d{3}\s?\d{3}\s?\d{3}\b")
DATE_RE = re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b")
MONEY_RE = re.compile(r"\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?")
INVOICE_RE = re.compile(r"\bINV[-\s]?\d{4,6}\b", re.IGNORECASE)


def _spans(pattern: re.Pattern, text: str, etype: str) -> list[dict]:
    return [{"type": etype, "value": m.group(0), "span": [m.start(), m.end()]}
            for m in pattern.finditer(text)]


def extract_emails(text: str) -> list[dict]:
    return _spans(EMAIL_RE, text, "email")


def extract_phones(text: str) -> list[dict]:
    return _spans(PHONE_RE, text, "phone")


def abn_valid(digits: str) -> bool:
    """Official ABN checksum: subtract 1 from first digit, weight, mod 89."""
    d = [int(c) for c in digits]
    d[0] -= 1
    weights = (10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19)
    return sum(a * b for a, b in zip(d, weights)) % 89 == 0


def extract_abns(text: str) -> list[dict]:
    out = []
    for m in ABN_RE.finditer(text):
        digits = re.sub(r"\s", "", m.group(0))
        if abn_valid(digits):
            out.append({"type": "abn", "value": m.group(0), "span": [m.start(), m.end()]})
    return out


def extract_dates(text: str) -> list[dict]:
    return _spans(DATE_RE, text, "date")


def extract_money(text: str) -> list[dict]:
    return _spans(MONEY_RE, text, "money")


def extract_invoice_nos(text: str) -> list[dict]:
    return _spans(INVOICE_RE, text, "invoice_no")


EXTRACTORS = {
    "email": extract_emails,
    "phone": extract_phones,
    "abn": extract_abns,
    "date": extract_dates,
    "money": extract_money,
    "invoice_no": extract_invoice_nos,
}

# Record-type classification by keyword signal (transparent rules, documented limits).
RECORD_SIGNALS = {
    "invoice": ("invoice", "abn", "amount due", "payment terms", "gst"),
    "email": ("from:", "to:", "subject:", "sent:", "regards"),
    "report": ("incident", "finding", "recommendation", "executive summary", "appendix"),
}


def classify_record(text: str) -> str:
    lowered = text.lower()
    scores = {k: sum(s in lowered for s in sig) for k, sig in RECORD_SIGNALS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "unknown"
