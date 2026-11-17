---
oak:
  kind: spec
  status: current
  as_of: 2026-11-17
  sources:
    - ../../journal/2026-11-16-handover.md
---
# TODO

- [x] Merge services into one process
- [x] Migrate data from Postgres to SQLite (migration 0042)
- [x] Set up Litestream backups (done 2026-11-16, restore test passed, per [handover](../../journal/2026-11-16-handover.md))
- [ ] Add index on orders.created_at

Status checked 2026-11-17 against the 2026-11-16 handover, not against production.
