"""Seeded synthetic corpus: 24 docs (invoice/email/report) + 1 empty dead-letter case.

Gold labels are built from the same structured rows that render the text,
so fixtures are exact by construction. Fixed seed -> byte-identical reruns.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

VALID_ABN = "51 824 753 556"   # well-known test ABN, valid checksum
INVALID_ABN = "51 824 753 557"  # checksum fails -> extractor must reject

OUT = Path(__file__).resolve().parent


def invoice(i: int, rng: random.Random) -> tuple[str, list[dict]]:
    n = 10420 + i
    amount = f"${rng.randint(1, 90)},{rng.randint(100, 999)}.00"
    abn = VALID_ABN if i % 4 else INVALID_ABN
    text = (f"TAX INVOICE {n}\nInvoice INV-{n} issued 15/03/2027.\n"
            f"Supplier ABN {abn}.\nAmount due {amount} (incl. GST).\n"
            f"Payment terms 14 days. Queries: billing{100 + i}@example.com.au.\n")
    gold = [
        {"type": "invoice_no", "value": f"INV-{n}"},
        {"type": "date", "value": "15/03/2027"},
        {"type": "money", "value": amount},
        {"type": "email", "value": f"billing{100 + i}@example.com.au"},
    ]
    if abn == VALID_ABN:
        gold.append({"type": "abn", "value": abn})
    return text, gold


def email(i: int, rng: random.Random) -> tuple[str, list[dict]]:
    phone = f"04{rng.randint(10, 99)} {rng.randint(100, 999)} {rng.randint(100, 999)}"
    addr = f"case.officer{i}@example.com"
    text = (f"From: intake@example.com\nTo: {addr}\nSubject: Document review {200 + i}\n"
            f"Sent: 02/04/2027\n\nPlease review the attached bundle. Regards,\n"
            f"Intake team, contact {phone}.\n")
    gold = [
        {"type": "email", "value": "intake@example.com"},
        {"type": "email", "value": addr},
        {"type": "date", "value": "02/04/2027"},
        {"type": "phone", "value": phone},
    ]
    return text, gold


def report(i: int, rng: random.Random) -> tuple[str, list[dict]]:
    amount = f"${rng.randint(5, 400)},{rng.randint(100, 999)}.50"
    text = (f"EXECUTIVE SUMMARY\nIncident IR-{300 + i} reviewed 20/05/2027.\n"
            f"Finding: anomalous transfers totalling {amount}.\n"
            f"Recommendation: escalate to review board. See appendix.\n"
            f"Contact: reviewer{i}@example.com.\n")
    gold = [
        {"type": "date", "value": "20/05/2027"},
        {"type": "money", "value": amount},
        {"type": "email", "value": f"reviewer{i}@example.com"},
    ]
    return text, gold


def main() -> None:
    rng = random.Random(42)
    OUT.mkdir(parents=True, exist_ok=True)
    for f in list(OUT.glob("*.txt")) + [OUT / "gold.json"]:
        if f.exists():
            f.unlink()
    gold_docs = []
    makers = [invoice, email, report]
    for i in range(24):
        text, gold = makers[i % 3](i, rng)
        name = f"doc-{i:02d}"
        (OUT / f"{name}.txt").write_text(text, encoding="utf-8")
        gold_docs.append({"doc_id": name, "entities": gold})
    (OUT / "doc-99.txt").write_text("lorem ipsum dolor sit amet\n", encoding="utf-8")
    (OUT / "gold.json").write_text(json.dumps(gold_docs, indent=2), encoding="utf-8")
    n_gold = sum(len(d["entities"]) for d in gold_docs)
    print(f"corpus: 25 docs (24 tagged + 1 dead-letter probe), {n_gold} gold entities")


if __name__ == "__main__":
    main()
