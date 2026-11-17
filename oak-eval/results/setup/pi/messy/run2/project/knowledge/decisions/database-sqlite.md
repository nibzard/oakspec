---
oak:
  kind: reference
  status: current
  as_of: 2026-11-16
  sources:
    - ../journal/arch-sync.md
    - ../journal/handover-2026-11-16.md
  links:
    - database.md
---
# Database decision: SQLite + Litestream

Atlas uses SQLite with Litestream for backups. This replaces the
PostgreSQL decision in [database.md](database.md).

What was said (arch-sync, 2026-10-08):
- Services were merged into a single process in September; only one
  writer remains, so a single-writer database is enough.
- Postgres upgrades and backups cost about 4 hours a month of on-call
  time.
- Agreed: move to SQLite + Litestream.

Rollout status (handover, 2026-11-16): migration 0042 applied on
production; Litestream configured and verified with a restore test.
