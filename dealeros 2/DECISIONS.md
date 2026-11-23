# Decisions

## Compare B's value with A's total_value
- Rejected: comparing with base_value only.
- Why: B stores the final event amount; A's total includes base plus adjustment.

## Keep dirty values without losing source text
- Rejected: converting blanks or malformed values to zero, or skipping the row.
- Why: blank is unknown; raw B text remains available for audit.

## Accept valid split entries
- Rejected: flagging every record with multiple B entries.
- Why: multiple parts are a valid split when their exact Decimal sum equals A's total.

## Attribute disagreements to a tenant safely
- Rejected: exposing the other tenant's location in a mismatch row.
- Why: A-side records belong to A's location org; a cross-tenant B location is masked. Orphans belong to B's location org.

## Reconcile VOIDED rows
- Rejected: silently ignoring VOIDED records.
- Why: the supplied brief leaves this as a business decision; this implementation continues comparison and surfaces actual discrepancies.
