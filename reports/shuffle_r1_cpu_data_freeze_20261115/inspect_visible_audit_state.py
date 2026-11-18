import hashlib,json
from pathlib import Path

base=Path("/home/xde10/.local/state/vlm-perception-reward-rl")
report=Path("/home/xde10/projects/vlm-perception-reward-rl/reports/shuffle_r1_cpu_data_freeze_20261115")
files=[]
for p in base.rglob("*"):
    if p.is_file() and (p.name.endswith(".jsonl") or "visible" in p.name.lower() or "audit" in p.name.lower()):
        try:
            files.append({"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.file_digest(p.open("rb"),"sha256").hexdigest() if p.suffix==".jsonl" else None})
        except Exception as e: files.append({"path":str(p),"error":repr(e)})
visible=report/"mmrl30k-visible-audit.json"
out={"candidate_files":files,"report_visible_audit_exists":visible.exists()}
if visible.exists():
    d=json.loads(visible.read_text())
    out["visible_audit"]=d
    target=d.get("row_manifest_sha256")
    matches=[x for x in files if x.get("sha256")==target]
    out["row_manifest_hash_matches"]=matches
old=base/"mmrl30k-b362381"/"rows.jsonl"
if old.exists():
    out["old_rows_sha256"]=hashlib.file_digest(old.open("rb"),"sha256").hexdigest()
(report/"visible_audit_state.json").write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
print("saved",report/"visible_audit_state.json","candidate files",len(files),"visible audit",visible.exists())
