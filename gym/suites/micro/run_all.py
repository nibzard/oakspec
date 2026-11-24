#!/usr/bin/env python3
"""Freeze protocol hashes and run all OAK v0.5 Pi + Gondolin experiments."""
import json
from pathlib import Path
import sys
import time

from common import HERE, RUNNER, SPEC_V04, SPEC_V05, sha256_file
import exp1_bootstrap
import exp2_r4_backfire
import exp3_receipt_and_merge


def freeze_protocol(out_root: Path) -> dict[str, str]:
    tracked = [
        RUNNER,
        SPEC_V04,
        SPEC_V05,
        HERE / "launch_pi.py",
        HERE / "common.py",
        HERE / "exp1_bootstrap.py",
        HERE / "exp2_r4_backfire.py",
        HERE / "exp3_receipt_and_merge.py",
        HERE / "run_all.py",
        Path("/home/agent/oak-tools/pi-gondolin.ts"),
    ]
    hashes = {str(p): sha256_file(p) for p in tracked}
    lines = [f"{digest}  {path}" for path, digest in hashes.items()]
    (out_root / "protocol.sha256").write_text("\n".join(lines) + "\n")
    return hashes


def main():
    out_root = Path(sys.argv[1]).resolve()
    out_root.mkdir(parents=True, exist_ok=False)
    t0 = time.monotonic()
    hashes = freeze_protocol(out_root)
    print(f"Protocol frozen ({len(hashes)} files) -> {out_root / 'protocol.sha256'}", flush=True)

    e1 = exp1_bootstrap.run_experiment(out_root / "exp1-bootstrap", reps=3, max_workers=3)
    e2 = exp2_r4_backfire.run_experiment(out_root / "exp2-r4-backfire", reps=3, max_workers=3)
    e3 = exp3_receipt_and_merge.run_experiment(
        out_root / "exp3-receipt-and-merge", reps=3, merge_rounds=2, max_workers=3
    )

    combined = {
        "wall_seconds": round(time.monotonic() - t0, 1),
        "protocol_sha256": hashes,
        "exp1_bootstrap": e1["summary"],
        "exp2_r4_backfire": e2["summary"],
        "exp3_receipt": e3["receipt_summary"],
        "exp3_merge": e3["merge_summary"],
    }
    (out_root / "summary.json").write_text(json.dumps(combined, indent=2) + "\n")
    print("\n=== ALL EXPERIMENTS COMPLETE ===", flush=True)
    print(json.dumps(combined, indent=2), flush=True)


if __name__ == "__main__":
    main()
