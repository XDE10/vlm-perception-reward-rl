"""Remaining train-only reserve for a second fact audit if 1000 are insufficient."""
import zipfile
from scripts.common.topup_common import *
def run():
    out=DATA/'project3_reserve';out.mkdir(exist_ok=True);(out/'images').mkdir(exist_ok=True)
    if (out/'manifest.json').exists():return
    ids={r['sample_id'] for r in rows(DATA/'project3/cases.jsonl')};cases=[];archives={}
    for r in rows(ROOT/'data/project3_all_split_candidates_v2/train.jsonl'):
        if r['sample_id'] in ids:continue
        archive,member=r['image_source_locator'].split('::',1)
        if archive not in archives:archives[archive]=zipfile.ZipFile(ROOT/'data/project3_sources/intergps/data/geometry3k'/archive)
        p=out/'images'/(r['original_id']+'.png');p.write_bytes(archives[archive].read(member));cases.append({**r,'image_path':str(p),'image_sha256':sha(p)})
    for z in archives.values():z.close()
    write(out/'cases.jsonl',cases);dump(out/'manifest.json',{'train_reserve':len(cases),'validation_and_test_included':False,'files':{'cases.jsonl':sha(out/'cases.jsonl')},'purpose':'Use same fact-level criteria only if approved train count remains below500; stop at shared total $8'});print('Geometry reserve',len(cases),flush=True)
if __name__=='__main__':run()
