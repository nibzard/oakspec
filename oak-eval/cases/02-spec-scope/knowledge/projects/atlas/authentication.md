---
oak:
  version: 1
  kind: spec
  status: superseded
  superseded_by: auth-spec.md
---
# Authentication

Use secure session cookies: HttpOnly, Secure, SameSite=Strict, 8-hour expiry.
Implement password reset via a link valid for 24 hours.
