---
oak:
  version: 1
  kind: record
  at: 2026-11-16
  links:
    - spec.md
---
# Deployment handover

- [x] Applied database migration 0042
- [x] Restarted services
- [x] Notified stakeholders
- [ ] Add index on `orders.created_at` (not started — query plan in spec.md)

Remember to restart services after migration.
