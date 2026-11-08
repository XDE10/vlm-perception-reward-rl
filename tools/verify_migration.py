"""Offline migration verification; run from any working directory."""
import argparse,hashlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0,str(ROOT))

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--full',action='store_true',help='Also hash all archived files and source snapshots')
    args=parser.parse_args()
    m=json.loads(Path('migration_manifest.json').read_text(encoding='utf8'))
    errors=[]
    for f in m['files']:
        p=Path(f['path'])
        if not p.is_file():errors.append('missing: '+str(p))
        elif p.stat().st_size!=f['bytes']:errors.append('size changed: '+str(p))
        elif args.full and sha(p)!=f['sha256']:errors.append('hash changed: '+str(p))
    release=Path('data/portable_release')
    rm=json.loads((release/'manifest.json').read_text(encoding='utf8'))
    from src.data.approved_training_inputs import load_approved,model_view
    counts={}
    for name,digest in rm['files'].items():
        p=release/name
        if sha(p)!=digest:errors.append('release hash changed: '+name)
    for name in rm['approved_training_files']:
        rows=load_approved(release/'manifest.json',name)
        counts[name]=len(rows)
        profile='perception_sft' if name.startswith('project3') else ('opd' if name.startswith('project2') else 'math_sft')
        for row in rows:model_view(row,profile)
    for name in rm.get('approved_evaluation_files',[]):
        counts[name]=sum(bool(line.strip()) for line in (release/name).read_text(encoding='utf8').splitlines())
    for name in rm['files']:
        if not name.endswith('.jsonl'):continue
        with (release/name).open(encoding='utf8') as f:
            for line in f:
                if not line.strip():continue
                row=json.loads(line)
                if 'image_path' in row:
                    p=Path(row['image_path'])
                    if p.is_absolute() or not p.is_file():errors.append('image path invalid: '+str(p))
                    elif row.get('image_sha256') and sha(p)!=row['image_sha256']:errors.append('image changed: '+str(p))
    for p in Path('configs').glob('*.json'):
        c=json.loads(p.read_text(encoding='utf8'))
        for k in ['data_manifest','tokenizer_path','tokenizer_audit']:
            if k in c and (re_absolute(c[k]) or not Path(c[k]).exists()):errors.append('config path invalid: '+str(p)+' '+k)
        for k in ['model','output_dir']:
            if k in c and re_absolute(c[k]):errors.append('absolute config path: '+str(p)+' '+k)
    result={'project':m['project'],'files':len(m['files']),'full_hash_check':args.full,'release_rows':counts,'errors':errors,'gpu_run':False}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)

def re_absolute(s):
    return Path(s).is_absolute() or (len(s)>2 and s[1]==':' and s[2] in '/\\')

if __name__=='__main__':main()
