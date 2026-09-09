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
parser.add_argument('--workers', type=int, default=16)
parser.add_argument('--eval-workers', type=int, default=32)
args = parser.parse_args()
if not (1 <= args.workers <= 64 and 1 <= args.eval_workers <= 64):
    parser.error('workers must be between 1 and 64')
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from geobench.run_state import atomic_text, run_lock

key = getpass.getpass('BlockRun account key (hidden; not saved): ').strip().replace('\\_', '_')
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
