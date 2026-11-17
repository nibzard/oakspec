---
oak:
  version: 1
  kind: spec
  status: current
---
# Authentication

Implement password reset: single-use token, valid 30 minutes, delivered by email.
Use secure session cookies: HttpOnly, Secure, SameSite=Lax, 12-hour expiry.
Rate-limit login: 5 failed attempts per 15 minutes per account.
Add TOTP-based MFA for admin accounts.
