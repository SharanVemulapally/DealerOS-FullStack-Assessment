from django.core.management.base import BaseCommand
from reconcile.importer import import_csvs

class Command(BaseCommand):
    help = "Import all source CSV rows idempotently."
    def handle(self, *args, **options):
        counts = import_csvs()
        self.stdout.write(self.style.SUCCESS(
            "Import complete: " + ", ".join(f"{k}={v}" for k, v in counts.items())))
        if counts["a_read"] != counts["a_saved"] or counts["b_read"] != counts["b_saved"]:
            raise RuntimeError("Importer row count mismatch; inspect source rows.")
