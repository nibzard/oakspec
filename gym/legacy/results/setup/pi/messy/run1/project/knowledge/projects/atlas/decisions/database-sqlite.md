---
oak:
  kind: reference
  status: current
  as_of: 2026-11-17
  sources:
    - ../arch-sync.md
    - ../handover-2026-11-16.md
---
# Database decision (current)

Atlas runs on SQLite with Litestream replication.

- Agreed at the architecture sync (2026-10-08): the services had been merged
  into a single process with one writer, and Postgres upgrades/backups cost
  about 4 hours a month of on-call time.
- Migration 0042 was applied on production 2026-11-16; Litestream backups are
  configured and verified (restore test passed).

Replaces database.md (PostgreSQL 16, 2026-09-03).
