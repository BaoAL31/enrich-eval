"""Extractor unit tests: each entity type + ABN checksum + record classifier."""

from enrich.extractors import (abn_valid, classify_record, extract_abns,
                               extract_dates, extract_emails, extract_invoice_nos,
                               extract_money, extract_phones)


def test_email():
    ents = extract_emails("Contact intake@example.com or bob.smith@example.com.au")
    assert {e["value"] for e in ents} == {"intake@example.com", "bob.smith@example.com.au"}
    assert all(e["span"][1] - e["span"][0] == len(e["value"]) for e in ents)


def test_phone_mobile_and_landline():
    ents = extract_phones("Call 0412 345 678 or 02 9876 5432.")
    assert {e["value"] for e in ents} == {"0412 345 678", "02 9876 5432"}


def test_abn_checksum_accepts_valid_rejects_invalid():
    assert abn_valid("51824753556")
    assert not abn_valid("51824753557")
    ents = extract_abns("ABN 51 824 753 556 vs ABN 51 824 753 557.")
    assert [e["value"] for e in ents] == ["51 824 753 556"]


def test_dates_money_invoice():
    assert [e["value"] for e in extract_dates("Due 15/03/2027, sent 02-04-27.")] == ["15/03/2027", "02-04-27"]
    assert [e["value"] for e in extract_money("Total $12,345.00, deposit $500.00.")] == ["$12,345.00", "$500.00"]
    assert [e["value"] for e in extract_invoice_nos("Invoice INV-10421, ref IR-300.")] == ["INV-10421"]


def test_record_classifier():
    assert classify_record("Tax invoice, ABN, amount due, payment terms, GST.") == "invoice"
    assert classify_record("From: a\nTo: b\nSubject: hi\nSent: x\nRegards,") == "email"
    assert classify_record("Executive summary. Finding. Recommendation. Appendix.") == "report"
    assert classify_record("lorem ipsum dolor") == "unknown"
