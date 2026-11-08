"""Rebuild monitoring from durable per-rollout logs, including interrupted runs."""
import argparse,json
from pathlib import Path
from .project3_v2 import summarize_rollouts

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    records=[json.loads(x) for x in Path(a.input).read_text(encoding='utf8').splitlines() if x.strip()]
    Path(a.output).write_text(json.dumps(summarize_rollouts(records),ensure_ascii=False,indent=2),encoding='utf8')
