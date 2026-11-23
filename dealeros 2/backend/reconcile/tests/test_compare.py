from decimal import Decimal
from reconcile.cleaning import normalize_ref, parse_amount
from reconcile.compare import compare

def A(total="100.00", location="L1", date="2026-03-01"):
    return {"REC-1": {"total": Decimal(total), "location": location, "date": date}}
def B(value="100.00", ref="REC-1", location="L1", date="2026-03-01", entry="E1"):
    return {"entry_id": entry, "ref": ref,
            "value": Decimal(value) if value is not None else None,
            "location": location, "date": date}

def reasons(a, b):
    return [x["reason"] for x in compare(a, b)]

def test_missing_in_b():
    assert reasons(A(), []) == ["MISSING_IN_B"]

def test_orphan_in_b():
    assert reasons({}, [B(ref="REC-999")]) == ["ORPHAN_IN_B"]

def test_duplicate_same_amount_is_flagged():
    assert reasons(A(), [B(entry="E1"), B(entry="E2")]) == ["DUPLICATE_IN_B"]

def test_value_mismatch():
    assert reasons(A(), [B(value="90.00")]) == ["VALUE_MISMATCH"]

def test_blank_value_is_not_zero():
    assert reasons(A(), [B(value=None)]) == ["VALUE_MISMATCH"]

def test_split_that_sums_is_not_error():
    assert compare(A(), [B(value="40.00", entry="E1"), B(value="60.00", entry="E2")]) == []

def test_messy_references_normalize():
    assert normalize_ref("rec1034") == "REC-1034"
    assert normalize_ref(" REC - 1070 ") == "REC-1070"
    assert normalize_ref("1112") == "REC-1112"

def test_clean_row():
    assert compare(A(), [B()]) == []

def test_location_and_date_mismatches():
    found = reasons(A(), [B(location="L2", date="2026-03-02")])
    assert found == ["LOCATION_MISMATCH", "DATE_MISMATCH"]
