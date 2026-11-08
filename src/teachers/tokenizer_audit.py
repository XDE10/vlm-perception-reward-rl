"""Download only explicitly allowlisted tokenizer/config files at pinned commits.

Run from repository root: python -m src.teachers.tokenizer_audit
Never loads AutoModel or executes remote model code.
"""
import hashlib
import json
from pathlib import Path

MODELS = ['Qwen/Qwen2.5-1.5B-Instruct', 'Qwen/Qwen2.5-Math-7B-Instruct',
          'Qwen/Qwen2.5-Coder-7B-Instruct', 'Qwen/Qwen2.5-7B-Instruct']
ALLOWED = ['config.json', 'tokenizer.json', 'tokenizer_config.json', 'vocab.json',
           'merges.txt', 'special_tokens_map.json', 'added_tokens.json', 'chat_template.jinja']


def examples():
    math = [r'\frac{1}{2}+\sqrt{2}', r'\boxed{\frac{-3}{7}}', 'x² + y² = r²',
            '#### -1,234.50', r'\int_0^1 x^2 dx', 'P(A|B)=0.25',
            r'\angle ABC=90^\circ', '1e-9 != 10**(-8)']
    code = ['def f(x):\n    return x + 1\n', '\tif x:\n\t\tprint(x)',
            'class A:\n    def __init__(self):\n        self.x = []',
            's = "\\n\\t" # Unicode 中文', 'async def f():\n    await g()',
            'a=[i**2 for i in range(10)]', 'print(f"{1/3:.3f}")', 'x = {"a": None, "b": True}']
    unicode = ['你好，世界！', 'é e\u0301 café', 'αβγ → ∞ ∑ ∆', '😀👩\u200d💻🚀',
               'العربية עברית', '日本語 한국어', '\u200b\u00a0\n\r\t', '𠮷𝕏𝄞']
    special = ['<|im_start|>user\nHi<|im_end|>', '<|endoftext|>', '<think>x</think>',
               '<perception>Length(A,B)=5</perception>', '$ \\ { } [ ] # @ & %',
               '```python\nprint(1)\n```', '  a    b\n\n c ', '<|fim_prefix|>x<|fim_suffix|>']
    base = [('math',x) for x in math]+[('code',x) for x in code]+[('unicode',x) for x in unicode]+[('special',x) for x in special]
    return [{'category':c,'text':t} for c,t in base]+[{'category':c,'text':'Problem:\n'+t+'\nAnswer:'} for c,t in base]


def compare_vocabularies(vocabs):
    shared = set.intersection(*(set(v) for v in vocabs))
    aligned = sorted(vocabs[0][s] for s in shared if all(v[s] == vocabs[0][s] for v in vocabs))
    differences = []
    for token in sorted(set.union(*(set(v) for v in vocabs))):
        ids = [v.get(token) for v in vocabs]
        if len(set(ids)) != 1:
            differences.append({'token':token,'ids':ids})
    contiguous = aligned == list(range(len(aligned)))
    return {'size':len(aligned),'ids':aligned,'contiguous_from_zero':contiguous,
            'exclusive_upper_bound':len(aligned) if contiguous else None,
            'mapping_identical':not differences}, differences


def run(root=Path('.')):
    from huggingface_hub import HfApi, snapshot_download
    from transformers import AutoTokenizer
    report_dir = root/'reports'
    report_dir.mkdir(exist_ok=True)
    api = HfApi()
    tokenizers, models = [], []
    for name in MODELS:
        revision = api.model_info(name).sha
        folder = Path(snapshot_download(name, revision=revision, allow_patterns=ALLOWED,
                                        local_dir=root/'data/tokenizers'/name.split('/')[-1], max_workers=2))
        files = [p for p in folder.iterdir() if p.is_file()]
        if any(p.name not in ALLOWED for p in files):
            raise RuntimeError('Unexpected file in tokenizer-only download')
        tokenizer = AutoTokenizer.from_pretrained(folder,local_files_only=True,trust_remote_code=False)
        tokenizers.append(tokenizer)
        config = json.loads((folder/'config.json').read_text(encoding='utf-8'))
        models.append({'model':name,'revision':revision,'config_vocab_size':config['vocab_size'],
                       'len_tokenizer':len(tokenizer),'base_vocab_size':tokenizer.vocab_size,
                       'added_tokens':tokenizer.get_added_vocab(),
                       'special_tokens':{k:str(v) for k,v in tokenizer.special_tokens_map.items()},
                       'special_token_ids':tokenizer.all_special_ids,
                       'chat_template_sha256':hashlib.sha256(str(tokenizer.chat_template).encode()).hexdigest(),
                       'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}})
        print('Tokenizer metadata verified:',name,flush=True)
    support,differences = compare_vocabularies([t.get_vocab() for t in tokenizers])
    cases = []
    for example in examples():
        ids = [t.encode(example['text'],add_special_tokens=False) for t in tokenizers]
        chat = [t.apply_chat_template([{'role':'user','content':example['text']}],tokenize=True,add_generation_prompt=True) for t in tokenizers]
        cases.append({**example,'input_ids':ids,'identical':all(x==ids[0] for x in ids),
                      'chat_template_encoding_identical':all(x==chat[0] for x in chat)})
    contiguous = support['contiguous_from_zero']
    support['rule'] = ('Slice [:N] only for these audited revisions; mask all other output rows BEFORE generation, '
                       'then independently renormalize teacher/student probabilities on common support. '
                       'Track removed probability mass on real logits before masking. No real-logit mass measured tonight.'
                       if contiguous else 'Use explicit token mapping/index_select; no safe contiguous slice.')
    report = {'models':models,'common_support':support,'mapping_difference_count':len(differences),
              'mapping_differences':differences,'encoding_cases':cases,'case_count':len(cases),
              'all_raw_encodings_identical':all(x['identical'] for x in cases),
              'all_chat_encodings_identical':all(x['chat_template_encoding_identical'] for x in cases),
              'prefix_encoding_rule':'Use student-produced token IDs as the identical teacher/student prefix after audit. Do not independently render each models chat template. Raw token IDs align but templates can inject different system defaults.',
              'no_weights_downloaded':True,'scope':'Tokenizer files and config only; finite corpus encoding checks are not proof for all strings.'}
    output = report_dir/'tokenizer_alignment_report.json'
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    lines = ['# 四模型真实词表审计', '',f'共同有效 ID 数量：{support["size"]}；连续边界：{support["exclusive_upper_bound"]}。',
             f'逐项 token→ID 差异数：{len(differences)}；编码案例：{len(cases)}。',
             f'裸文本全部一致：{report["all_raw_encodings_identical"]}；chat template 编码全部一致：{report["all_chat_encodings_identical"]}。','']
    for m in models:
        lines.append(f'- {m["model"]}: config={m["config_vocab_size"]}, len={m["len_tokenizer"]}, revision={m["revision"]}')
    lines += ['',support['rule'],'','本轮不加载模型，不能测实际尾部概率质量，也不证明 GPU 蒸馏已可运行。']
    (report_dir/'tokenizer_alignment_summary.md').write_text('\n'.join(lines),encoding='utf-8')
    return report


if __name__ == '__main__':
    r = run()
    print(json.dumps({'common_support':r['common_support']['size'],'case_count':r['case_count'],
                      'encodings_identical':r['all_raw_encodings_identical']}))
