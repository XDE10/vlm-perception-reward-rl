import json
from pathlib import Path
from scripts.finalize_overnight_report import read_json


def test_offline_demo_and_cpu_environment():
    demo = read_json('reports/cpu_demo.json')
    assert demo['paid_api_calls']==0 and demo['gpu_operations']==0
    assert demo['synthesis']['state']=='accepted' and demo['geometry']['score']['f1']==1
    assert read_json('reports/cpu_environment.json')['torch_cuda_version'] is None
    cache = Path('data/synthesis_mock/cache.jsonl')
    with cache.open(encoding='utf-8') as f: records = [json.loads(line) for line in f]
    assert any(r['table']=='jobs' and r['body']['state']=='accepted' for r in records)
    assert all(r['body']['response']['provider']=='local_mock' for r in records if r['table']=='calls')
