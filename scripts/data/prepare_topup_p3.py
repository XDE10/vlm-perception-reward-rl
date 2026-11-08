import zipfile
from scripts.common.topup_common import *
def run():
    out=DATA/'project3';out.mkdir(exist_ok=True);(out/'images').mkdir(exist_ok=True)
    if (out/'manifest.json').exists():return
    old={r['original_id'] for r in rows(ROOT/'data/project3_perception_v2/prototype_200.jsonl')}
    train=rows(ROOT/'data/project3_all_split_candidates_v2/train.jsonl');train.sort(key=lambda r:(r['original_id'] not in old,stable('geometry-topup6/'+r['original_id'])))
    selected=train[:1000]+rows(ROOT/'data/project3_all_split_candidates_v2/validation.jsonl');cases=[];archives={}
    for r in selected:
        archive,member=r['image_source_locator'].split('::',1)
        if archive not in archives:archives[archive]=zipfile.ZipFile(ROOT/'data/project3_sources/intergps/data/geometry3k'/archive)
        p=out/'images'/(r['original_id']+'.png');p.write_bytes(archives[archive].read(member));cases.append({**r,'image_path':str(p),'image_sha256':sha(p)})
    for z in archives.values():z.close()
    write(out/'cases.jsonl',cases);dump(out/'manifest.json',{'train':1000,'validation':300,'old_200_included':len(old & {r['original_id'] for r in train[:1000]}),'test_used':False,'files':{'cases.jsonl':sha(out/'cases.jsonl')},'source_manifest_sha':sha(ROOT/'data/project3_all_split_candidates_v2/manifest.json')});print('P3 frozen',len(cases),flush=True)
if __name__=='__main__':run()
