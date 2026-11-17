---
oak:
  kind: reference
  status: current
  sources:
    - ../arch-sync.md
    - ../handover-2026-11-16.md
  links:
    - database.md
  origin: agent
---
# Database decision: SQLite + Litestream

Atlas uses SQLite, with backups via Litestream. Replaces
[database.md](database.md) (PostgreSQL 16).

Why (from the 2026-10-08 arch sync, attended by Ana, Mira, Nikola):
- Services were merged into a single process; only one writer remains.
- Postgres upgrades and backups cost about 4 hours a month of on-call time.

Status (from the 2026-11-16 handover): migration 0042 applied on production;
Litestream backups configured and a restore test passed.

Note: the arch sync says Mira would update the decision doc. This file was
written by an agent during OAK setup from the records above, not by Mira.
