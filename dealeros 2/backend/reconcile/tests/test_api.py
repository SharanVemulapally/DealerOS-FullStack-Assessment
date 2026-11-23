from datetime import date
from decimal import Decimal
import pytest
from django.test import Client
from reconcile.models import Location, SystemARecord, SystemBEntry

@pytest.mark.django_db
def test_tenant_scoping_and_cross_tenant_location_masking():
    a_loc = Location.objects.create(location_id="LOC-A", org_id="ORG-A", name="A")
    b_loc = Location.objects.create(location_id="LOC-B", org_id="ORG-B", name="B")
    SystemARecord.objects.create(record_id="REC-1", location=a_loc, event_date=date(2026, 1, 1),
        total_value=Decimal("100.00"), state="CONFIRMED")
    SystemBEntry.objects.create(entry_id="E-1", record_ref_raw="REC-1", record_ref="REC-1",
        location=b_loc, recorded_on=date(2026, 1, 1), value=Decimal("100.00"))
    client = Client()
    response = client.get("/api/disagreements/?org=ORG-A")
    assert response.status_code == 200
    result = response.json()["results"]
    assert len(result) == 1
    assert result[0]["reason"] == "LOCATION_MISMATCH"
    assert result[0]["location"] == "LOC-A"
    assert "LOC-B" not in str(result)
    assert client.get("/api/disagreements/?org=ORG-B").json()["results"] == []

@pytest.mark.django_db
def test_orphan_is_visible_only_to_b_location_tenant():
    b_loc = Location.objects.create(location_id="LOC-B", org_id="ORG-B", name="B")
    SystemBEntry.objects.create(entry_id="E-ORPHAN", record_ref_raw="REC-999", record_ref="REC-999",
        location=b_loc, recorded_on=date(2026, 1, 1), value=Decimal("10.00"))
    client = Client()
    assert client.get("/api/disagreements/?org=ORG-A").json()["results"] == []
    result = client.get("/api/disagreements/?org=ORG-B").json()["results"]
    assert len(result) == 1 and result[0]["reason"] == "ORPHAN_IN_B"
