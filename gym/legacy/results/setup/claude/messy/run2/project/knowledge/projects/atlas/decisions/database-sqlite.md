---
oak:
  kind: reference
  status: current
  as_of: 2026-11-17
  origin: agent
  sources:
    - ../../../journal/2026-10-08-arch-sync.md
    - ../../../journal/2026-11-16-handover.md
  links:
    - database-postgres.md
---
# Database decision: SQLite + Litestream (2026-10-08)

Atlas uses SQLite, backed up with Litestream. Replaces
[the PostgreSQL decision](database-postgres.md).

Why (from the 2026-10-08 arch sync, Ana, Mira, Nikola):
- Services were merged into a single process in September; only one writer remains.
- Postgres upgrades and backups cost about 4 hours a month of on-call time.

State (per the 2026-11-16 handover): migration 0042 applied on production;
Litestream backups configured, restore test passed.

Written by an agent during OAK setup on 2026-11-17; the arch sync said Mira
would update the decision doc, and no updated version was found.
Checked against the records above, not against production.
