"""Read-only scoped handover checks. Run from project root with Python >=3.9 + Pillow."""
import hashlib,json,sys,zipfile,subprocess,platform,importlib.metadata as metadata
from pathlib import Path
from collections import Counter
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):return [json.loads(x) for x in Path(p).read_text(encoding='utf8').splitlines() if x.strip()]
def save(name,data):(OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')

def main():
    import os
    os.chdir(ROOT);sys.path.insert(0,str(ROOT))
    from src.data.approved_training_inputs import load_approved,model_view
    from src.data.geometry_split_guard import guard
    manifest=json.loads(Path('data/portable_release/manifest.json').read_text(encoding='utf8'))
    links=rows('data/project3_audit/geometry3k_intergps_links.jsonl');by={r['wrapper_locator']:r for r in links}
    annotation={r['original_id']:r for r in rows('data/project3_audit/intergps_annotations.jsonl')}
    protected=set(json.loads(Path('data/portable_release/reserved_dev_ids_never_train.json').read_text(encoding='utf8'))['sample_ids'])
    errors=[];splits={};allrows=[];archives={};image_cache={}
    for change in manifest['migration']['changes']:
        if not change['portable'].endswith('.jsonl'):continue
        portable=rows(change['portable']);original=rows(change['source'])
        if sha(change['source'])!=change['source_sha256']:errors.append('source SHA '+change['source'])
        if sha(change['portable'])!=change['portable_sha256']:errors.append('portable SHA '+change['portable'])
        if len(portable)!=len(original):errors.append('row count mismatch')
        for n,(r,s) in enumerate(zip(portable,original),1):
            if {k:v for k,v in r.items() if k!='image_path'}!={k:v for k,v in s.items() if k!='image_path'}:errors.append('non-path change '+r['sample_id'])
            p=Path(r['image_path'])
            if p.is_absolute() or not p.resolve().is_relative_to(ROOT):errors.append('image path escape '+r['sample_id'])
            if str(p) not in image_cache:
                raw=p.read_bytes();im=Image.open(p).convert('RGB')
                pixel=hashlib.sha256(str(im.size).encode()+b'\0'+im.tobytes()).hexdigest()
                image_cache[str(p)]={'byte_sha256':hashlib.sha256(raw).hexdigest(),'pixel_sha256':pixel,'size':im.size}
                a=annotation[r['original_id']];archive,member=a['original_locator'].split('::')
                if archive not in archives:archives[archive]=zipfile.ZipFile(Path('data/project3_sources/intergps/data/geometry3k')/archive)
                source_bytes=archives[archive].read(str(Path(member).parent).replace('\\','/')+'/img_diagram.png')
                if raw!=source_bytes:errors.append('archive image bytes differ '+r['sample_id'])
            imeta=image_cache[str(p)];link=by[r['sample_id']]
            if not imeta['byte_sha256']==r['image_sha256']:errors.append('byte SHA '+r['sample_id'])
            if not imeta['pixel_sha256']==r['image_pixel_sha256']==link['image_pixel_sha256']==annotation[r['original_id']]['image_pixel_sha256']:errors.append('pixel SHA '+r['sample_id'])
            if link['original_id']!=r['original_id'] or link['wrapper_split']!=r['split']:errors.append('link identity '+r['sample_id'])
            if r['split']=='train':
                v=model_view(r,'perception_sft')
                if set(v['input'])!={'problem','image_path'} or r['sample_id'] in protected:errors.append('training whitelist/reserved ID '+r['sample_id'])
            elif not r['evaluation_approved'] or r['training_approved']:errors.append('validation approval '+r['sample_id'])
            if 'radius_' in r['problem']+r['model_perception'] or 'source_radius_id' in r['problem']+r['model_perception']:errors.append('source ID visible '+r['sample_id'])
        kept,excluded=guard(portable,links)
        if excluded:errors.append('split guard '+str(len(excluded)))
        splits[portable[0]['split']]={'rows':len(portable),'unique_sample_ids':len({r['sample_id'] for r in portable}),'unique_original_ids':len({r['original_id'] for r in portable}),'unique_pixel_images':len({r['image_pixel_sha256'] for r in portable}),'split_guard_kept':len(kept),'positive_fact_count':sum(len(r['certified_positive_tokens']) for r in portable),'negative_fact_count':sum(len(r['certified_negative_tokens']) for r in portable),'relations':dict(Counter(t.split('(')[0] for r in portable for t in r['certified_positive_tokens']))}
        allrows+=portable
    for z in archives.values():z.close()
    train=[r for r in allrows if r['split']=='train'];valid=[r for r in allrows if r['split']=='validation']
    intersect=sorted({r['image_pixel_sha256'] for r in train}&{r['image_pixel_sha256'] for r in valid})
    if intersect:errors.append('cross split pixels')
    overlap=rows('data/project3_audit/mathvista_testmini_overlap.jsonl')
    mv={'rows':len(overlap),**{k:sum(bool(r[k]) for r in overlap) for k in ['geometry3k_source','exact_image_train_overlap','joint_image_question_train_overlap','potential_text_train_overlap','source_disjoint_no_exact_overlap']},'exact_image_matches':sum(bool(r['image_matches']) for r in overlap)}
    sample=train[0];case=next(r for r in rows('data/strict_v8_20261024/geometry/all_case_audit.jsonl') if r['sample_id']==sample['sample_id'])
    save('sample_trace.json',{'release_row_line':1,'release_row':sample,'original_annotation':annotation[sample['original_id']],'audit_case':case,'image':image_cache[str(Path(sample['image_path']))]})
    save('data_checks.json',{'splits':splits,'image_files_checked':len(image_cache),'portable_only_image_path_changed':not errors,'archive_image_bytes_checked':len(image_cache),'cross_split_pixel_intersection':intersect,'mathvista_archived_overlap_recount':mv,'errors':errors,'note':'No model execution; image archive bytes and current linkage were checked, not new human fact certification.'})
    packages={d.metadata['Name']:d.version for d in metadata.distributions()}
    save('environment.json',{'python':sys.executable,'version':sys.version,'platform':platform.platform(),'packages':packages})
    commands=[('verify_migration',[sys.executable,'tools/verify_migration.py']),('verify_migration_full',[sys.executable,'tools/verify_migration.py','--full']),('readme_tests',[sys.executable,'-m','pytest','tests/test_approved_training_inputs.py','tests/test_training_entries_cpu.py','tests/test_perception_v4.py','tests/test_geometry_model_serialization.py','-q']),('data_tests',[sys.executable,'-m','pytest','tests/test_approved_training_inputs.py','tests/test_perception_v4.py','tests/test_geometry_model_serialization.py','tests/test_geometry_split_guard.py','tests/test_geometry_parser.py','tests/test_project3_perception_v2.py','tests/test_project3_audit.py','-q'])]
    results=[]
    for name,cmd in commands:
        env=dict(os.environ,PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
        p=subprocess.run(cmd,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (OUT/(name+'.log')).write_bytes(p.stdout)
        results.append({'name':name,'argv':cmd,'exit_code':p.returncode,'log':name+'.log'})
        print(name,p.returncode,flush=True)
    save('commands.json',results)
    files=['AGENTS.md','README.md','data/portable_release/manifest.json','scripts/train_project3.py','src/training/approved_hf.py','src/data/approved_training_inputs.py','src/data/perception_v4.py','src/training/perception_reward_v4.py','src/data/geometry_model_serialization.py','src/data/geometry_split_guard.py','src/evaluation/geometry_perception_parser.py','scripts/diagnose_project3_vision.py','src/data/perception_text_guards.py','src/data/project3_perception_v2.py','reports/strict_v8_20261024/执行报告.md','project_blueprints/项目三_多模态几何推理_详细实施方案.md']
    save('source_snapshot_sha256.json',{p:sha(p) for p in files})
    print(json.dumps({'splits':splits,'errors':errors},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
