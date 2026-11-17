---
oak:
  kind: spec
  status: current
  as_of: 2026-11-16
  sources:
    - journal/handover-2026-11-16.md
---
# TODO

- [x] Merge services into one process
- [x] Migrate data from Postgres to SQLite (migration 0042)
- [x] Set up Litestream backups (done 2026-11-16, per handover: configured and restore-tested)
- [ ] Add index on orders.created_at
