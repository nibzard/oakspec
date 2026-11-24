# OAK Gym

Standardized, self-contained evaluation environments for iterating on the
[OAK-0001](../publish/oak-0001.txt) specification across both **software
repositories** and **long-form prose manuscripts**.

## Layout

```text
gym/
├── harness/
│   ├── run.py          Unified CLI runner (`list`, `check`, `code`, `prose`)
│   ├── check_oak.py    Deterministic OAK v0.5 linter (C1–C10, YAML/.oak.json, links)
│   ├── sandboxes.py    Bubblewrap multi-CLI isolation (Claude Code, Codex, Antigravity, Pi)
│   └── gondolin/       Gondolin micro-VM Pi extensions (`pi-gondolin.ts`, `package.json`)
├── substrates/
│   ├── itsdangerous/   Vendored pallets/itsdangerous (BSD-3-Clause, 297 pytest tests)
│   └── antimemetics/   Vendored SCP Antimemetics Division tales by qntm (CC BY-SA 3.0)
├── suites/
│   ├── code/           Code Gym: real serializer work + policy supersession + parallel merges
│   ├── prose/          Prose Gym: book chapter authoring + cut reveals + editorial relay
│   └── micro/          Gondolin micro-VM ablations (cold bootstrap, R1/R4/R5, W9 digests)
└── legacy/             Archived v0.2–v0.4 pilot harnesses and fixtures
```

All trial outputs default to `../runs/` (gitignored) so multi-megabyte agent
logs stay outside Git history while every harness, substrate, and scorer lives
in this single repository.

## Quick start

```sh
# List suites and supported agent CLIs
python3 gym/harness/run.py list

# Lint any OAK knowledge folder deterministically (Section 5.1 & 10)
python3 gym/harness/run.py check path/to/project/knowledge

# Run the Code Gym (itsdangerous) on one or all four agent CLIs
python3 gym/harness/run.py code --mode single \
  --agents claude_opus_5_5,codex_gpt_6_2_sol,agy_gemini_4_neon,pi_glm_5_4

# Run the Prose Gym (Antimemetics Division manuscript) — single or parallel relay
python3 gym/harness/run.py prose --mode all \
  --agents claude_opus_5_5,codex_gpt_6_2_sol,pi_glm_5_4,agy_gemini_4_neon
```

## Licensing note on substrates

- `gym/substrates/itsdangerous/` is licensed under **BSD-3-Clause** (`LICENSE.txt`).
- `gym/substrates/antimemetics/` is derived from **qntm**'s *Antimemetics
  Division Hub* on the SCP Wiki and is licensed strictly under **CC BY-SA 3.0**
  (`LICENSE-CC-BY-SA-3.0.md`).
