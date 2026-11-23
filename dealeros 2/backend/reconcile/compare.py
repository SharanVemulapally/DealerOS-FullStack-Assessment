from collections import defaultdict
from decimal import Decimal

def compare(a_rows, b_rows):
    """Return disagreement dictionaries. Inputs are plain dictionaries keyed by record id."""
    output = []
    by_ref = defaultdict(list)
    for entry in b_rows:
        by_ref.setdefault(entry.get("ref"), []).append(entry)

    for ref, entries in by_ref.items():
        if ref not in a_rows:
            for entry in entries:
                output.append({"reason": "ORPHAN_IN_B", "record_id": ref or "",
                               "entry_id": entry["entry_id"], "a_value": None,
                               "b_value": entry.get("value"), "a_location": None,
                               "b_location": entry.get("location"), "location": entry.get("location"),
                               "sort_value": entry.get("value")})
    for record_id, a in a_rows.items():
        entries = by_ref.get(record_id, [])
        base = {"record_id": record_id, "a_value": a.get("total"),
                "a_location": a.get("location"), "b_location": None,
                "location": a.get("location"), "sort_value": a.get("total")}
        if not entries:
            output.append({**base, "reason": "MISSING_IN_B", "b_value": None})
            continue
        values = [e.get("value") for e in entries]
        if any(v is None for v in values):
            output.append({**base, "reason": "VALUE_MISMATCH",
                           "b_value": None if len(entries) == 1 else values})
            continue
        if len(entries) > 1:
            if sum(values, Decimal("0")) != a.get("total"):
                output.append({**base, "reason": "DUPLICATE_IN_B", "b_value": values})
            # Multiple parts that add to total are a valid split.
            continue
        entry = entries[0]
        if entry.get("value") != a.get("total"):
            output.append({**base, "reason": "VALUE_MISMATCH", "b_value": entry.get("value")})
        if entry.get("location") != a.get("location"):
            output.append({**base, "reason": "LOCATION_MISMATCH",
                           "b_value": entry.get("value"), "b_location": entry.get("location")})
        if entry.get("date") != a.get("date"):
            output.append({**base, "reason": "DATE_MISMATCH", "b_value": entry.get("value"),
                           "b_location": entry.get("location")})
    return output
