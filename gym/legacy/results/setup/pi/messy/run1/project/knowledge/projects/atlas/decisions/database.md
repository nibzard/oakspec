---
oak:
  kind: reference
  status: superseded
  superseded_by: database-sqlite.md
---
# Database decision (2026-09-03)

We will use PostgreSQL 16.

Why: several services write concurrently, and the team knows it well.

Origin: team decision recorded 2026-09-03; no underlying note file exists.

*Superseded by database-sqlite.md: at the architecture sync (2026-10-08) the
services had been merged into one process with one writer, and the team agreed
to move to SQLite + Litestream. Migration 0042 was applied 2026-11-16.*
