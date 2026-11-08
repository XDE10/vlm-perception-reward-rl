"""Enforce file-scoped engineering approval and whitelist actual model inputs."""
import hashlib,json
from pathlib import Path


def load_approved(manifest_path,filename):
    manifest_path=Path(manifest_path).resolve();root=manifest_path.parent
    m=json.loads(manifest_path.read_text(encoding='utf-8'))
    if filename not in m.get('approved_training_files',[]):raise ValueError('File is outside explicit training approval scope')
    p=(root/filename).resolve()
    if not p.is_relative_to(root):raise ValueError('Path escapes approved release')
    expected=m['files'][filename];expected=expected['sha256'] if isinstance(expected,dict) else expected
    if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:raise ValueError('Approved file digest changed')
    with p.open(encoding='utf-8') as f:rows=[json.loads(l) for l in f if l.strip()]
    if not rows or not all(r.get('training_approved') is True for r in rows):raise ValueError('Empty or unapproved training rows')
    if len({r['sample_id'] for r in rows})!=len(rows):raise ValueError('Duplicate training IDs')
    return rows


def model_view(row,profile):
    if not row.get('training_approved'):raise ValueError('Row is not approved')
    if profile=='opd':
        # Math system is rendered exactly once by the student contract. Code
        # preserves the sealed interface-bearing user prompt.
        prompt=row['problem'] if row['domain']=='math' else row.get('prompt',row['problem'])
        return {'input':{'prompt':prompt,'domain':row['domain']},'target':None}
    if profile=='math_sft':return {'input':{'problem':row['problem']},'target':row['solution']}
    if profile=='perception_sft':
        target=row['model_perception']
        if not target or 'source_radius_id' in target or 'radius_' in target:raise ValueError('Internal source identity in model target')
        if row.get('model_input_whitelist')!=['problem','image_path'] or row.get('model_target_whitelist')!=['model_perception']:
            raise ValueError('Visual training field contract absent')
        return {'input':{'problem':row['problem'],'image_path':row['image_path']},'target':target}
    raise ValueError('Unknown training profile')
