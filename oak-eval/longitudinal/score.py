"""Check a saved project against one session's external answer key."""
import argparse
import json
from pathlib import Path
from prepare import load_world


def score(world, project, number):
    expected = world['sessions'][number - 1]['expected']
    checks = []
    for name, fields in expected.get('files', {}).items():
        try:
            actual = json.loads((project / name).read_text())
        except (OSError, ValueError):
            actual = {}
        for key, value in fields.items():
            checks.append({'check': name + ':' + key, 'pass': actual.get(key) == value})
    for name, fragments in expected.get('text', {}).items():
        path = project / name
        actual = path.read_text() if path.exists() else ''
        for fragment in fragments:
            checks.append({'check': name + ':' + fragment, 'pass': fragment in actual})
    try:
        report = json.loads((project / 'report.json').read_text())
    except (OSError, ValueError):
        report = {}
    report_fields = dict(expected['report'])
    report_fields.setdefault('conflict', False)
    task_states = expected['files']['tasks.json']
    report_fields['open_tasks'] = sorted(key for key, value in task_states.items() if value == 'open')
    for key, value in report_fields.items():
        actual = report.get(key)
        if key == 'open_tasks' and isinstance(actual, list):
            actual = sorted(actual)
        checks.append({'check': 'report.json:' + key, 'pass': actual == value})
    return checks


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('world', choices=['service', 'cli', 'docs'])
    parser.add_argument('project', type=Path)
    parser.add_argument('session', type=int, choices=range(1, 11))
    args = parser.parse_args()
    checks = score(load_world(args.world), args.project, args.session)
    print(json.dumps({'checks': checks, 'passed': sum(item['pass'] for item in checks),
                      'total': len(checks)}, indent=2))
