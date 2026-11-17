# Atlas knowledge

Memory here follows [OAK-0001](oak-0001.txt) (local copy of the
convention; the original was provided at setup). Read and write by
those rules.

## Journal (records)

- [Architecture sync, 2026-10-08](journal/arch-sync.md): agreed move from PostgreSQL to SQLite + Litestream.
- [Handover, 2026-11-16](journal/handover-2026-11-16.md): migration 0042 and Litestream backups done; open: index on orders.created_at.
- [2026-11-17](journal/2026-11-17.md): OAK setup record.

## Decisions (references)

- [Database: SQLite + Litestream](decisions/database-sqlite.md): current decision.
- [Database: PostgreSQL 16](decisions/database.md): superseded by the above.

## Notes and plans

- [Notes](notes.md): deploy target (fly.io), review preference, latency budget.
- [TODO](TODO.md): open work — index on orders.created_at.
- [ideas.txt](ideas.txt): loose ideas; plain text, intentionally no oak block.
