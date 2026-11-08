"""Optional official-source ranged fallback; validate Git blob identity before use."""
import concurrent.futures
import hashlib
from pathlib import Path
import requests
import time

if __name__=='__main__':
    revision='99e6b5293c7bb4a5eaf2a370e6b213c79ab33ebb'
    name='data/geometry3k/train.zip'
    tree=requests.get(f'https://api.github.com/repos/lupantech/InterGPS/git/trees/{revision}?recursive=1',timeout=30).json()
    entry=next(x for x in tree['tree'] if x['path']==name)
    size=entry['size']
    url=f'https://raw.githubusercontent.com/lupantech/InterGPS/{revision}/{name}'
    cache=Path('data/project3_sources/intergps/range_cache')
    cache.mkdir(exist_ok=True)
    def part(start):
        end=min(start+2**20,size)-1
        file=cache/f'{start}-{end}.part'
        if file.exists() and file.stat().st_size==end-start+1:
            return file.read_bytes()
        for attempt in range(5):
            try:
                r=requests.get(url,headers={'Range':f'bytes={start}-{end}'},timeout=120)
                r.raise_for_status()
                if r.status_code!=206 or len(r.content)!=end-start+1 or not r.headers.get('Content-Range','').startswith(f'bytes {start}-{end}/'):
                    raise ValueError('Server failed strict HTTP range contract')
                file.write_bytes(r.content)
                return r.content
            except (requests.RequestException,ValueError):
                if attempt==4: raise
                time.sleep(1+attempt)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        data=b''.join(pool.map(part,range(0,size,2**20)))
    sha=hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
    if sha!=entry['sha']:
        raise ValueError('Git blob mismatch')
    destination=Path('data/project3_sources/intergps')/name
    temp=destination.with_suffix('.ranged.zip')
    temp.write_bytes(data)
    temp.replace(destination)
    print('Verified official Git blob:',sha,'bytes:',len(data))
