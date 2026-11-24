---
oak:
  version: 1
  kind: reference
  status: current
---
# Release process

1. Open a PR against `main`; one approving review.
2. CI runs the full test suite — required for every release, hotfixes included.
3. Merge, tag `vX.Y.Z`, and deploy with `atlas deploy`.
4. Watch error rates for 15 minutes.
