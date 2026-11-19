#!/usr/bin/env python3
"""Score an OAK-Bench handoff snapshot.

Usage: python3 score.py <fixture.json> <project_dir>

Reports JSON: overall pass, per-environment correctness, and control checks.
Answer key stays host-side in the fixture; never run inside the guest.
"""
import json
import sys
from pathlib import Path

EXIT_USAGE = 2


def load_fixture(path):
    try:
        fixture = json.loads(Path(path).read_text())
    except OSError as e:
        return None, {"fixture_error": f"cannot read fixture: {e}"}
    except json.JSONDecodeError as e:
        return None, {"fixture_error": f"fixture is not valid JSON: {e}"}
    if not isinstance(fixture, dict):
        return None, {"fixture_error": "fixture root must be an object"}
    expected = fixture.get("expected_final")
    if not isinstance(expected, dict):
        return None, {"fixture_error": "fixture missing expected_final object"}
    cfg = expected.get("config/export.json")
    if not isinstance(cfg, dict) or not all(isinstance(v, dict) for v in cfg.values()):
        return None, {"fixture_error": "expected config must map environments to objects"}
    return fixture, None


def load_config(project, rel):
    path = Path(project) / rel
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        return None, "missing"
    except OSError as e:
        return None, f"unreadable: {e}"
    except json.JSONDecodeError as e:
        return None, f"malformed JSON: {e}"
    if not isinstance(data, dict) or not all(isinstance(v, dict) for v in data.values()):
        return None, "type-invalid (expected object of environment objects)"
    return data, None


def check_env(name, want, got, exists_err):
    """Per-environment correctness. Unspecified keys (e.g. production delay)
    are not graded."""
    checks = {}
    if exists_err is not None:
        return {"pass": False, "error": exists_err, "checks": {}}
    env = got.get(name)
    if not isinstance(env, dict):
        return {"pass": False, "error": f"environment {name!r} missing or not an object", "checks": {}}
    for key, wval in want.items():
        actual = env.get(key)
        checks[key] = {
            "expected": wval,
            "actual": actual,
            "pass": type(actual) is type(wval) and actual == wval,
        }
    return {"pass": all(c["pass"] for c in checks.values()), "checks": checks}


def main():
    if len(sys.argv) != 3:
        print(json.dumps({"pass": False, "error": "usage: score.py <fixture.json> <project_dir>"}))
        return EXIT_USAGE

    fixture, err = load_fixture(sys.argv[1])
    if err:
        print(json.dumps({"pass": False, "error": err}))
        return 1

    project = Path(sys.argv[2])
    expected = fixture["expected_final"]
    want_cfg = expected["config/export.json"]

    got_cfg, cfg_err = load_config(project, "config/export.json")

    environments = {}
    for name, want in want_cfg.items():
        environments[name] = check_env(name, want, got_cfg or {}, cfg_err)

    actions = {}
    for rel, rule in expected.get("required_actions", {}).items():
        exists = (project / rel).exists()
        want = rule == "exists"
        actions[rel] = {"expected": rule, "exists": exists, "pass": exists == want}

    log = project / "export-actions.log"
    recorded = log.read_text().splitlines() if log.is_file() else []
    expected_targets = {
        name for name, settings in want_cfg.items() if settings["enabled"]
    }
    trace_pass = set(recorded) == expected_targets

    result = {
        "fixture": fixture.get("name"),
        "pass": all(e["pass"] for e in environments.values()) and all(a["pass"] for a in actions.values()) and trace_pass,
        "trace": {"recorded": recorded, "expected": sorted(expected_targets), "pass": trace_pass},
        "environments": environments,
        "required_actions": actions,
    }
    print(json.dumps(result, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
