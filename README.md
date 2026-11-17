# OAK: Open Agent Knowledge

A plain-text convention for memory that people and AI agents share.

- Spec (published): https://oakspec.dev, plain text at
  https://oakspec.dev/oak-0001.txt
- Spec source: `publish/oak-0001.txt`
- Long-form RFC draft with design notes: `RFC.md`
- Evaluation suite and harness: `oak-eval/`
- Test plan for the time test: `docs/test-plan-time.md`

## Publish the site

1. `python3 publish/build_site.py`
2. `cd publish && wrangler deploy`

The site is a static-assets Worker with the custom domain `oakspec.dev`.
