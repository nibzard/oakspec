---
oak:
  kind: reference
  status: current
  as_of: 2026-11-17
---
# Notes

- 2026-09-03: Main database is PostgreSQL 16. Backups via pg_dump nightly. *(Superseded 2026-10-08: we moved to SQLite + Litestream — see decisions/database-sqlite.md; migration 0042 applied 2026-11-16. Line kept for history.)*
- 2026-10-08: Arch sync — services merged into one process, so we move to SQLite + Litestream. See arch-sync.md.
- Deploy target is fly.io (checked 2026-10-20 against flyctl 0.3.1).
- Ana prefers code reviews in the morning.
- Order history queries must stay under 200 ms at p95.

Origins: pre-existing project notes, brought into knowledge/ during OAK setup on
2026-11-17. Dated lines carry their own dates. as_of 2026-11-17 covers the
database lines only (checked against handover-2026-11-16.md and
decisions/database-sqlite.md); the deploy target, review preference, and latency
budget were not re-verified.
