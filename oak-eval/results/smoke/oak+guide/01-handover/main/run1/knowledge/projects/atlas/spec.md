---
oak:
  version: 1
  kind: spec
  status: current
---
# Atlas orders performance

- Order history queries filtered by date must return in under 200 ms at p95.
- Add a B-tree index on `orders.created_at`.
- Migrations are applied with `atlas migrate up`; services restart with `atlas restart`.
