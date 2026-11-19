"""Summarize trajectory scores and Pi usage from a calibration batch."""
import argparse
from collections import Counter
import json
from pathlib import Path


def usage_for(trajectory):
    usage = Counter()
    calls = 0
    for log in sorted(trajectory.glob("session-*/agent.stdout")):
        with log.open() as stream:
            for line in stream:
                event = json.loads(line)
                if event.get("type") == "tool_execution_start":
                    calls += 1
                if event.get("type") == "message_end":
                    message = event.get("message", {})
                    if message.get("role") == "assistant":
                        tokens = message.get("usage", {})
                        for key in ("input", "output", "cacheRead", "cacheWrite"):
                            usage[key] += tokens.get(key, 0)
    return calls, dict(usage)


def summarize(root):
    results = {}
    for trajectory in sorted(p for p in root.iterdir() if p.is_dir()):
        score_file = trajectory / "score.json"
        score = json.loads(score_file.read_text()) if score_file.is_file() else None
        tool_calls, usage = usage_for(trajectory)
        results[trajectory.name] = {
            "score": score,
            "tool_calls": tool_calls,
            "usage": usage,
        }
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch", type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.batch), indent=2))
