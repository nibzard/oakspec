---
oak:
  kind: spec
  status: current
  sources:
    - handover-2026-11-16.md
---
# TODO

- [x] Merge services into one process
- [x] Migrate data from Postgres to SQLite (migration 0042)
- [x] Set up Litestream backups (done per handover-2026-11-16.md: configured, restore test passed)
- [ ] Add index on orders.created_at
