---
oak:
  kind: reference
  status: current
  as_of: 2026-11-17
  origin: agent
  sources:
    - ../arch-sync.md
    - ../TODO.md
    - ../handover-2026-11-16.md
---
# Database: SQLite and Litestream

The 2026-10-08 architecture sync records agreement to replace PostgreSQL with SQLite and Litestream because the services now run in one process with one writer, and PostgreSQL maintenance cost about four hours per month.

The task list marks migration 0042 complete. The 2026-11-16 handover reports migration 0042 applied in production and Litestream backups configured and verified by a restore test.

Checked against these project notes on 2026-11-17; production and code were not independently inspected. This consolidates the recorded decision and replaces [the PostgreSQL decision](database.md).
