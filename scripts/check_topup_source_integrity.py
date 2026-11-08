from scripts.topup_common import *
def run():
    m=read(ROOT/'data/screening_sources/code_source.json');checked=[]
    for i,r in enumerate(m['files'],1):
        p=ROOT/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'];checked.append(r['path'])
        if i%2==0:print('Pinned code source hashes',i,'/',len(m['files']),flush=True)
    old=read(ROOT/'data/project2_code_v2/manifest.json')
    for r in old['files'].values():assert sha(ROOT/r['path'])==r['sha256']
    math=read(ROOT/'data/math_manifest.json')
    for r in math['files'].values():assert sha(ROOT/r['path'])==r['sha256']
    dump(REPORT/'source_integrity.json',{'code_source_revision':m['revision'],'code_source_shards_sha_verified':len(checked),'source_bytes_verified':sum(r['bytes'] for r in m['files']),'old_code_v2_files_sha_verified':len(old['files']),'old_math_manifest_files_sha_verified':len(math['files']),'no_source_mutation':True});print('Source integrity passed',flush=True)
if __name__=='__main__':run()
