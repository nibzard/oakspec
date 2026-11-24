# Learnings

## 2026-11-18, v2 revision

- `gondolin build` needs `lz4` on the host for the initramfs step; the
  package can be installed while the binary is missing, which gives a
  confusing `lz4: not found`.
- The Gondolin VM picks guest assets via `GONDOLIN_GUEST_DIR` (highest
  priority). sudo scrubs the caller environment, so the variable must be
  set inside launch.py, not in the caller's shell.
- glm-5.3 agents verify via `cat`/`grep` in bash, not only via the read
  tool; a check_ran matcher must scan command strings for record paths
  too, and use DOTALL because agents write newline-heavy `python3 -c`
  heredocs.
- "Note-only" facts leak when the truth is an absence: a careful agent
  can derive "not authorized" from the lack of any authorization record
  (see the p2 smoke in `v2/smoke/`).
- Kept files that contradict a memory are easy to find in barista
  (README pipx vs no-pipx machine; T052 Java-absent vs installed JDK).
  The looper kept docs also teach claude-zai, which killed one planned
  note-needed task.
