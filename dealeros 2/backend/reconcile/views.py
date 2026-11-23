from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Location, SystemARecord, SystemBEntry
from .compare import compare

@require_GET
def disagreements(request):
    org = request.GET.get("org")
    if org not in {"ORG-A", "ORG-B"}:
        return JsonResponse({"error": "Provide org=ORG-A or org=ORG-B."}, status=400)
    allowed_locations = set(Location.objects.filter(org_id=org).values_list("location_id", flat=True))
    a_qs = SystemARecord.objects.filter(location__org_id=org).select_related("location")
    a_rows = {a.record_id: {"total": a.total_value, "location": a.location.location_id if a.location else None,
                            "date": a.event_date.isoformat() if a.event_date else None,
                            "state": a.state} for a in a_qs}
    # Fetch matching B references to detect cross-org mismatches, but never expose the other tenant's location.
    matching_refs = list(a_rows.keys())
    b_qs = SystemBEntry.objects.filter(record_ref__in=matching_refs).select_related("location")
    # Orphans belong to the org of B's own location.
    orphan_qs = SystemBEntry.objects.filter(location__org_id=org).exclude(record_ref__in=SystemARecord.objects.values("record_id")).select_related("location")
    entries = list(b_qs) + list(orphan_qs)
    b_rows = [{"entry_id": e.entry_id, "ref": e.record_ref, "value": e.value,
               "location": e.location.location_id if e.location else None,
               "date": e.recorded_on.isoformat() if e.recorded_on else None} for e in entries]
    rows = compare(a_rows, b_rows)
    safe_rows = []
    for row in rows:
        # An A-owned disagreement belongs to A's tenant. Cross-tenant B location is masked.
        if row.get("a_location") and row["a_location"] not in allowed_locations:
            continue
        if row.get("b_location") and row["b_location"] not in allowed_locations:
            row["b_location"] = "[other tenant]"
        # Orphan rows are included only for their B-side tenant.
        if row["reason"] == "ORPHAN_IN_B" and row.get("location") not in allowed_locations:
            continue
        row.pop("a_location", None); row.pop("b_location", None); row.pop("sort_value", None)
        safe_rows.append(row)
    reason = request.GET.get("reason")
    if reason:
        safe_rows = [r for r in safe_rows if r["reason"] == reason]
    sort = request.GET.get("sort", "record_id")
    reverse = sort.startswith("-"); key = sort.lstrip("-")
    if key == "value":
        safe_rows.sort(key=lambda r: Decimal(str(r.get("a_value") or r.get("b_value") or 0)), reverse=reverse)
    else:
        safe_rows.sort(key=lambda r: str(r.get(key) or ""), reverse=reverse)
    return JsonResponse({"count": len(safe_rows), "results": safe_rows})
