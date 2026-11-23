import csv
from pathlib import Path
from django.conf import settings
from .models import Location, SystemARecord, SystemBEntry
from .cleaning import normalize_ref, parse_amount, parse_date

DATA_DIR = Path(settings.BASE_DIR) / "data"

def import_csvs():
    counts = {"locations_read": 0, "a_read": 0, "b_read": 0, "a_saved": 0, "b_saved": 0}
    with (DATA_DIR / "locations.csv").open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            counts["locations_read"] += 1
            loc, _ = Location.objects.update_or_create(
                location_id=(row.get("location_id") or "").strip(),
                defaults={"org_id": (row.get("org_id") or "").strip(),
                          "name": (row.get("location_name") or "").strip()})
    with (DATA_DIR / "system_a.csv").open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            counts["a_read"] += 1
            loc_id = (row.get("location_id") or "").strip()
            loc = Location.objects.filter(location_id=loc_id).first()
            SystemARecord.objects.update_or_create(
                record_id=(row.get("record_id") or "").strip(),
                defaults={"location": loc, "event_date": parse_date(row.get("event_date")),
                    "category_code": (row.get("category_code") or "").strip(),
                    "actor_id": (row.get("actor_id") or "").strip() or None,
                    "base_value": parse_amount(row.get("base_value")),
                    "adjustment": parse_amount(row.get("adjustment")),
                    "total_value": parse_amount(row.get("total_value")),
                    "state": (row.get("state") or "").strip()})
            counts["a_saved"] += 1
    with (DATA_DIR / "system_b.csv").open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            counts["b_read"] += 1
            loc_id = (row.get("location_id") or "").strip()
            SystemBEntry.objects.update_or_create(
                entry_id=(row.get("entry_id") or "").strip(),
                defaults={"record_ref_raw": (row.get("record_ref") or "").strip(),
                    "record_ref": normalize_ref(row.get("record_ref")),
                    "location": Location.objects.filter(location_id=loc_id).first(),
                    "recorded_on": parse_date(row.get("recorded_on")),
                    "value_raw": (row.get("value") or "").strip(),
                    "value": parse_amount(row.get("value")),
                    "label": (row.get("label") or "").strip()})
            counts["b_saved"] += 1
    return counts
