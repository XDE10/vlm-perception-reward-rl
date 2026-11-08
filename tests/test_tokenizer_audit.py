from src.teachers.tokenizer_audit import examples, compare_vocabularies, ALLOWED


def test_audit_corpus_and_download_allowlist():
    assert len(examples()) >= 50
    assert {x['category'] for x in examples()} == {'math','code','unicode','special'}
    assert not any('safetensors' in f or '*' in f or 'bin' in f for f in ALLOWED)


def test_mapping_detects_gaps_misalignments_and_extra_tokens():
    support, diffs = compare_vocabularies([{'a':0,'b':1,'c':2},{'a':0,'b':2,'z':1}])
    assert support['ids'] == [0]
    assert len(diffs) == 3
    support,_ = compare_vocabularies([{'a':0,'b':2}]*2)
    assert not support['contiguous_from_zero'] and support['exclusive_upper_bound'] is None
