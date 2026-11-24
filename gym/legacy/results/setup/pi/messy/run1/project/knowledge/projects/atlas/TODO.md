---
oak:
  kind: spec
  status: current
  as_of: 2026-11-17
  sources:
    - handover-2026-11-16.md
---
# TODO

- [x] Merge services into one process
- [x] Migrate data from Postgres to SQLite (migration 0042)
- [x] Set up Litestream backups (closed 2026-11-17: done per handover 2026-11-16 — configured and verified, restore test passed)
- [ ] Add index on orders.created_at
