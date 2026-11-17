---
oak:
  version: 1
  kind: reference
  status: current
  sources:
    - ../meetings/arch-sync.md
---
# Database

Atlas uses SQLite in WAL mode, with Litestream for backups.

Rationale: Atlas runs as a single process on one node; a separate database
server added operational work without benefit.
