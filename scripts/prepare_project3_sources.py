"""Download pinned public annotation/data files, preserving licenses and SHA256."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import requests

ROOT = Path('data/project3_sources')
SOURCES = {
    'intergps': ('https://raw.githubusercontent.com/lupantech/InterGPS/99e6b5293c7bb4a5eaf2a370e6b213c79ab33ebb/',
                 ['LICENSE', 'README.md', 'data/unzip_data.sh'] + ['data/geometry3k/'+x+'.zip' for x in ['train','val','test','logic_forms']]),
    'geometry3k': ('https://huggingface.co/datasets/hiyouga/geometry3k/resolve/fd21e533e1e50d0662a2bf7b223e60511bd5f8b7/',
                   ['README.md'] + ['data/'+x+'-00000-of-00001.parquet' for x in ['train','validation','test']]),
    'mathvista': ('https://huggingface.co/datasets/AI4Math/MathVista/resolve/2b6ad69445fbb5695c9b165475e8decdbeb97747/',
                 ['README.md','source.json','annot_testmini.json','data/testmini-00000-of-00001-725687bf7a18d64b.parquet']),
}

def fetch(item):
    source, base, name = item
    path = ROOT/source/name
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        response = requests.get(base+name, timeout=180)
        response.raise_for_status()
        temp = path.with_suffix(path.suffix+'.part')
        temp.write_bytes(response.content)
        temp.replace(path)
    return dict(source=source, name=name, url=base+name, bytes=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())

if __name__ == '__main__':
    jobs = [(source,base,name) for source,(base,names) in SOURCES.items() for name in names]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        files = list(pool.map(fetch,jobs))
    manifest = dict(schema='project3_sources_v1', files=files,
                    license_note='Read each pinned README/LICENSE; packaging MIT does not relicense underlying textbook material. MathVista card CC-BY-SA-4.0; individual sources retain their terms.')
    (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'files':len(files),'bytes':sum(f['bytes'] for f in files)}))
