"""Real audit acceptance; run after tokenizer_audit (no downloads in pytest)."""
import json
from pathlib import Path


def test_real_four_model_audit():
    report = json.loads(Path('reports/tokenizer_alignment_report.json').read_text(encoding='utf-8'))
    assert len(report['models']) == 4 and report['case_count'] >= 50
    assert all(m['revision'] and m['files'] and m['len_tokenizer'] == 151665 for m in report['models'])
    support = report['common_support']
    assert support['ids'] == list(range(support['size']))
    assert support['size'] == 151665 and report['mapping_difference_count'] == 0
    assert report['all_raw_encodings_identical']
    assert report['no_weights_downloaded']
    for p in Path('data/tokenizers').rglob('*'):
        assert p.suffix not in {'.safetensors','.bin','.pt','.pth'}
