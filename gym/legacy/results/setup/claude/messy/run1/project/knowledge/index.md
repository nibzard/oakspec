---
oak:
  kind: reference
  status: current
  as_of: 2026-11-17
---
# Knowledge index

Memory for Atlas (order management service). Follows OAK-0001.

## Atlas
- [Notes](projects/atlas/NOTES.md): deploy target, latency budget, team preferences.
- [TODO](projects/atlas/TODO.md): open work (index on orders.created_at).
- [Ideas](projects/atlas/ideas.txt): unsorted ideas (DuckDB exports, self-hosted CI). Unlabeled plain text.

### Decisions
- [Database: SQLite + Litestream](projects/atlas/decisions/database-sqlite.md): current.
- [Database: PostgreSQL 16](projects/atlas/decisions/database.md): superseded.

### Records
- [Arch sync, 2026-10-08](projects/atlas/arch-sync.md): agreed move to SQLite.
- [Handover, 2026-11-16](projects/atlas/handover-2026-11-16.md): migration 0042 and Litestream done.

## Journal
- [2026-11-17](journal/2026-11-17.md): OAK setup.
