from pathlib import Path
import hashlib
import json

from huggingface_hub import snapshot_download

root=Path(__file__).resolve().parent
expected=json.loads((root/'model-identity.json').read_text())
snapshot=Path(snapshot_download(expected['repo'], revision=expected['revision'], cache_dir=str(root/'hf/hub'),
    allow_patterns=list(expected['files']), max_workers=6))
assert snapshot.name==expected['revision']
for name, identity in expected['files'].items():
    path=snapshot/name
    assert path.is_file() and path.stat().st_size==identity['bytes'], name
    if 'sha256' in identity:
        with path.open('rb') as stream:
            assert hashlib.file_digest(stream, 'sha256').hexdigest()==identity['sha256'], name
    else:
        blob=path.read_bytes()
        assert hashlib.sha1(f'blob {len(blob)}\0'.encode()+blob).hexdigest()==identity['git_blob_sha1'], name
index=json.loads((snapshot/'model.safetensors.index.json').read_text())
assert set(index['weight_map'].values())=={name for name in expected['files'] if name.endswith('.safetensors')}
link=root/'model-snapshot'
if not link.is_symlink():
    link.symlink_to(snapshot, target_is_directory=True)
assert link.resolve()==snapshot.resolve()
print('Pinned base local snapshot verified', link, expected['revision'], flush=True)
