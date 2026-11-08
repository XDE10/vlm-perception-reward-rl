from scripts.topup_common import ROOT,BUDGET,read,rows,sha,dump,write,stable
DATA=ROOT/'data/finalfill_v7_20261024';REPORT=ROOT/'reports/finalfill_v7_20261024'
DATA.mkdir(exist_ok=True);REPORT.mkdir(exist_ok=True)
def snapshot():
    for name in ['ledger.json','budget_policy.json','topup_budget_policy.json']:
        p=REPORT/('before_'+name)
        if not p.exists():p.write_bytes((BUDGET/name).read_bytes())
