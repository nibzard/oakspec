# Architecture sync, 8 Oct 2026

Present: Ana, Mira, Nikola.

- Services were merged into a single process in September; only one writer remains.
- Postgres upgrades and backups cost about 4 hours a month of on-call time.
- Agreed: move to SQLite + Litestream. Mira updates the decision doc.
