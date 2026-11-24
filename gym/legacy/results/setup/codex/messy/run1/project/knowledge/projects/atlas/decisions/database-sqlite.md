---
oak:
  kind: reference
  status: current
  as_of: 2026-11-16
  sources:
    - ../arch-sync.md
    - ../NOTES.md
    - ../TODO.md
    - ../handover-2026-11-16.md
  links: [database.md]
  origin: agent
---
# Database: SQLite + Litestream

The recorded decision is to use SQLite with Litestream. The 2026-10-08
architecture sync reports that services had merged into one process with
one writer and PostgreSQL maintenance cost about four hours per month.

The checklist records the Postgres-to-SQLite migration as complete. The
2026-11-16 handover reports migration 0042 applied in production and
Litestream backups configured and verified with a successful restore test.
This summary was checked against those notes, not a live production system.

This replaces the [PostgreSQL decision](database.md).
