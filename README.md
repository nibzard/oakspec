# OAK: Open Agent Knowledge

A plain-text convention for memory that people and AI agents share.

## Repository layout

- **Specification & site (`publish/`):**
  - Published spec (v0.5): [`publish/oak-0001.txt`](publish/oak-0001.txt) — live at https://oakspec.dev and https://oakspec.dev/oak-0001.txt
  - Evidence summary: [`publish/evidence.txt`](publish/evidence.txt) — https://oakspec.dev/evidence.txt
  - Blog: [`publish/posts/`](publish/posts/), built by [`publish/blog.py`](publish/blog.py) — https://oakspec.dev/blog/
- **Standardized OAK Gym (`gym/`):**
  - Unified runner & OAK v0.5 linter: [`gym/harness/`](gym/harness/) (`python3 gym/harness/run.py --help`)
  - Vendored substrates: [`gym/substrates/itsdangerous/`](gym/substrates/itsdangerous/) (Code Gym, BSD-3-Clause) and [`gym/substrates/antimemetics/`](gym/substrates/antimemetics/) (Prose Gym, SCP Antimemetics Division Hub by qntm, CC BY-SA 3.0)
  - Active benchmark suites: [`gym/suites/code/`](gym/suites/code/), [`gym/suites/prose/`](gym/suites/prose/), and [`gym/suites/micro/`](gym/suites/micro/)
  - Earlier v0.2–v0.4 pilots: [`gym/legacy/`](gym/legacy/)
- **Research & results (`docs/`):**
  - [Four-model OSS Code Gym results](docs/oss-gym-four-models-results.md)
  - [OAK v0.5 Gondolin experiment results](docs/v05-experiments-results.md)
  - [OAK v1 decision brief](docs/oak-v1-decision-brief.md)
  - Historical v0.2 draft (`RFC.md`), synthesis (`research.md`), and log (`learnings.md`)
- **Brand (`brand/`):** "The Keeping Oak" mark and favicons.

## Run the OAK Gym

```sh
python3 gym/harness/run.py list
python3 gym/harness/run.py check path/to/knowledge
python3 gym/harness/run.py code --mode single --agents claude_opus_5_5
python3 gym/harness/run.py prose --mode all --agents claude_opus_5_5,codex_gpt_6_2_sol,pi_glm_5_4,agy_gemini_4_neon
```

## Publish the site

1. `python3 publish/build_site.py`
2. `cd publish && wrangler deploy`

The site is a static-assets Cloudflare Worker serving `oakspec.dev`.
