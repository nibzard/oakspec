"""Run the six longitudinal trajectories with host Pi and Gondolin tools."""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import signal
import subprocess
import time

from prepare import load_world, prepare
from score import score

ROOT = Path(__file__).resolve().parent


def run_trajectory(job, args, launcher):
    world_name, condition = job
    world = load_world(world_name)
    directory = args.output / (world_name + '-' + condition)
    project = directory / 'project'
    directory.mkdir()
    rows = []
    for number in range(1, 11):
        session_dir = directory / ('session-' + str(number))
        session_dir.mkdir()
        prompt = prepare(world, condition, project, number)
        (session_dir / 'prompt.txt').write_text(prompt)
        command = [
            'sudo', '-n', 'python3', str(launcher), str(project),
            str(args.agent_dir), str(args.node), str(args.pi_cli),
            '-p', '--mode', 'json', '--no-session', '--no-extensions',
            '--no-mcp', '--no-skills', '--no-prompt-templates',
            '--no-context-files', '--provider', 'zai', '--model', 'glm-5.3',
            '--thinking', 'low', '-e', str(args.extension), prompt,
        ]
        start = time.monotonic()
        with (session_dir / 'events.jsonl').open('w') as out:
            with (session_dir / 'stderr.txt').open('w') as err:
                process = subprocess.Popen(
                    command, stdout=out, stderr=err, start_new_session=True,
                )
                try:
                    rc = process.wait(timeout=args.timeout)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                    rc = 124
        elapsed = time.monotonic() - start
        shutil.copytree(project, session_dir / 'project')
        checks = score(world, session_dir / 'project', number)
        calls = 0
        usage = []
        agent_finished = False
        for line in (session_dir / 'events.jsonl').read_text().splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            calls += event.get('type') == 'tool_execution_end'
            agent_finished |= event.get('type') == 'agent_end'
            if event.get('type') == 'message_end':
                message = event.get('message', {})
                if message.get('role') == 'assistant' and message.get('usage'):
                    usage.append(message['usage'])
        row = {
            'world': world_name, 'condition': condition, 'session': number,
            'exit_code': rc, 'agent_finished': agent_finished,
            'seconds': round(elapsed, 2), 'tool_calls': calls,
            'passed': sum(item['pass'] for item in checks),
            'total': len(checks), 'checks': checks, 'usage': usage,
        }
        (session_dir / 'score.json').write_text(json.dumps(row, indent=2))
        rows.append(row)
        print(json.dumps({key: value for key, value in row.items()
                          if key not in ('checks', 'usage')}), flush=True)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--extension', type=Path, required=True)
    parser.add_argument('--agent-dir', type=Path, required=True)
    parser.add_argument('--node', type=Path, required=True)
    parser.add_argument('--pi-cli', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=240)
    args = parser.parse_args()
    for key in ('output', 'extension', 'agent_dir', 'node', 'pi_cli'):
        setattr(args, key, getattr(args, key).resolve())
    args.output.mkdir(parents=True, exist_ok=False)
    inputs = args.output / 'inputs'
    inputs.mkdir()
    sources = [ROOT / name for name in (
        'service.json', 'cli.json', 'docs.json', 'prepare.py', 'score.py',
        'run.py', 'README.md',
    )] + [args.extension]
    hashes = {}
    for source in sources:
        shutil.copy2(source, inputs / source.name)
        hashes[source.name] = hashlib.sha256(source.read_bytes()).hexdigest()
    jobs = [(name, condition) for name in ('service', 'cli', 'docs')
            for condition in ('oak', 'prose')]
    random.Random(20261118).shuffle(jobs)
    protocol = {
        'seed': 20261118, 'jobs': jobs, 'concurrency': 2, 'sessions': 10,
        'provider': 'zai', 'model': 'glm-5.3', 'thinking': 'low',
        'timeout_seconds': args.timeout, 'sha256': hashes,
        'failure_rule': 'Retain failed sessions and continue the trajectory.',
    }
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2))
    launcher = args.output / 'launch.py'
    launcher.write_text('''import os, grp, sys
os.setgroups([1000, grp.getgrnam("kvm").gr_gid])
os.setgid(1000)
os.setuid(1000)
os.environ["HOME"] = "/home/agent"
os.environ["PI_CODING_AGENT_DIR"] = sys.argv[2]
os.chdir(sys.argv[1])
os.execv(sys.argv[3], sys.argv[3:])
''')
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(
            lambda job: run_trajectory(job, args, launcher), jobs,
        ))
    rows = [row for trajectory in results for row in trajectory]
    (args.output / 'results.json').write_text(json.dumps(rows, indent=2))


if __name__ == '__main__':
    main()
