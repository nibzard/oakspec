---
oak:
  kind: reference
  sources: [arch-sync.md]
---
# Notes

- 2026-09-03: Main database is PostgreSQL 16. Backups via pg_dump nightly.
- 2026-10-08: Arch sync — services merged into one process, so we move to SQLite + Litestream. See arch-sync.md.
- Deploy target is fly.io (checked 2026-10-20 against flyctl 0.3.1).
- Ana prefers code reviews in the morning.
- Order history queries must stay under 200 ms at p95.

## Setup context

The dated PostgreSQL entry is historical; see [the replacement decision](decisions/database-sqlite.md). The [handover](handover-2026-11-16.md) reports Litestream backups configured and restore-tested. The review preference has no known date or attribution. The latency target is a stated requirement, not a measured result.
