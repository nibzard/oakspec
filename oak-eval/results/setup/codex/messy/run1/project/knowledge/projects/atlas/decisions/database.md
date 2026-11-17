---
oak:
  kind: reference
  status: superseded
  as_of: 2026-09-03
  superseded_by: database-sqlite.md
---
# Database decision (2026-09-03)

We will use PostgreSQL 16.

Why: several services write concurrently, and the team knows it well.
