---
oak:
  version: 1
  kind: record
  at: 2026-10-08
---
# Architecture sync

- Services were merged into a single process in September; only one writer remains.
- Postgres upgrades and backups took about 4 hours a month of on-call time.
- Agreed: move to SQLite + Litestream. Mira to update the decision doc.
