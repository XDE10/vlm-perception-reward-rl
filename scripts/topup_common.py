import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/topup_v6_20261024';REPORT=ROOT/'reports/topup_v6_20261024'
BUDGET=ROOT/'reports/data_release_preparation_20261024/shared_api_cache'
DATA.mkdir(exist_ok=True);REPORT.mkdir(exist_ok=True)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def rows(p):
    with Path(p).open(encoding='utf-8') as f:return [json.loads(l) for l in f if l.strip()]
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for c in iter(lambda:f.read(8*1024*1024),b''):h.update(c)
    return h.hexdigest()
def dump(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def write(p,rs):
    with Path(p).open('w',encoding='utf-8') as f:
        for r in rs:f.write(json.dumps(r,ensure_ascii=False)+'\n')
def stable(s):return hashlib.sha256(s.encode()).hexdigest()
def snapshot():
    for name in ['ledger.json','budget_policy.json']:
        p=REPORT/('before_'+name)
        if not p.exists():p.write_bytes((BUDGET/name).read_bytes())
