"""Run the API experiment with a hidden, memory-only credential and redacted logs."""
import argparse
import getpass
import json
import logging
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone

logging.disable(logging.CRITICAL)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage', choices=['all', 'generate', 'evaluate'], default='all')
parser.add_argument('--workers', type=int, default=4)
parser.add_argument('--eval-workers', type=int, default=4)
parser.add_argument('--background', action='store_true',
                    help='Detach after hidden credential entry; keep progress in logs/')
parser.add_argument('--background-child', action='store_true', help=argparse.SUPPRESS)
args = parser.parse_args()
if not (1 <= args.workers <= 64 and 1 <= args.eval_workers <= 64):
    parser.error('workers must be between 1 and 64')
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from geobench.run_state import atomic_text, run_lock

key = (os.environ.pop('GEOBENCH_ACCOUNT_KEY') if args.background_child else
       getpass.getpass('BlockRun account key (hidden; not saved): ')).strip().replace('\\_', '_')
if not key.startswith('brk_live_'):
    raise SystemExit('Expected a BlockRun account key')
environment = dict(os.environ, OPENAI_API_KEY=key,
    GEOBENCH_API_PROVIDER='blockrun-openai', OPENAI_BASE_URL='https://api.blockrun.ai/v1',
    GEOBENCH_API_WORKERS=str(args.workers), GEOBENCH_EVAL_WORKERS=str(args.eval_workers),
    GEOBENCH_ALLOW_TRUNCATED='1', PYTHON_BIN=sys.executable,
    GEOBENCH_USAGE_LOG=str(root / 'logs/api_usage.jsonl'),
    PYTHONUNBUFFERED='1', OPENBLAS_NUM_THREADS='4', OMP_NUM_THREADS='4')
environment.pop('OPENAI_LOG', None)
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
log_path = root / 'logs' / f'revision_api_{stamp}.log'
state_path = root / 'logs' / 'revision_api_status.json'
state = dict(stage=args.stage, started_utc=stamp, log=str(log_path),
             workers=args.workers, eval_workers=args.eval_workers, status='starting')
log_path.parent.mkdir(parents=True, exist_ok=True)
if args.background:
    child_environment = dict(os.environ, GEOBENCH_ACCOUNT_KEY=key)
    with (root / 'logs/revision_api_supervisor.log').open('a') as startup_log:
        supervisor = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), '--stage', args.stage,
             '--workers', str(args.workers), '--eval-workers', str(args.eval_workers),
             '--background-child'], cwd=root, env=child_environment,
            start_new_session=True, stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=startup_log)
    print(json.dumps(dict(supervisor_pid=supervisor.pid, status_file=str(state_path))), flush=True)
    raise SystemExit(0)
state.update(supervisor_pid=os.getpid(), background=args.background_child)
with run_lock(root / 'logs/revision_api.lock'):
    with log_path.open('w', buffering=1) as log:
        process = subprocess.Popen(['bash', 'scripts/run_revision_api.sh', args.stage],
            cwd=root, env=environment, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        state.update(status='running', pid=process.pid)
        atomic_text(state_path, json.dumps(state, indent=2) + '\n')
        print(json.dumps(state), flush=True)
        for line in process.stdout:
            safe = re.sub(r'brk_live_[A-Za-z0-9]+', '[REDACTED]', line.replace(key, '[REDACTED]'))
            log.write(safe)
            print(safe, end='', flush=True)
        code = process.wait()
        state.update(status='complete' if code == 0 else 'failed', exit_code=code,
                     finished_utc=datetime.now(timezone.utc).isoformat())
        atomic_text(state_path, json.dumps(state, indent=2) + '\n')
        key = None
        environment.pop('OPENAI_API_KEY', None)
        print(json.dumps(state), flush=True)
        sys.exit(code)
