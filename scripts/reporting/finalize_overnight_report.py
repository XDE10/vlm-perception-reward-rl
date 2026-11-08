"""Verify required evidence and assemble the human report without network access."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read_json(name): return json.loads((ROOT/name).read_text(encoding='utf-8'))


def audit():
    required = ['src/teachers/tokenizer_audit.py','src/data/prepare_math_data.py',
                'src/evaluation/math_verifier.py','src/losses/reference.py','src/synthesis/async_client.py',
                'src/evaluation/geometry_perception_parser.py','reports/tokenizer_alignment_report.json',
                'data/math_manifest.json','reports/pytest_full.log','reports/cpu_demo.json']
    for name in required:
        if not (ROOT/name).is_file(): raise ValueError('Missing required artifact: '+name)
    token = read_json('reports/tokenizer_alignment_report.json')
    data = read_json('data/math_manifest.json')
    demo = read_json('reports/cpu_demo.json')
    environment = read_json('reports/cpu_environment.json')
    log = (ROOT/'reports/pytest_full.log').read_text(encoding='utf-8')
    match = re.search(r'=+ (\d+) passed in ([\d.]+)s =+',log)
    if not match or int(match[1])<86 or re.search(r'\b(FAILED|ERROR|SKIPPED)\b',log):
        raise ValueError('Full verbose test log is not a passing complete run')
    assert environment['torch_cuda_version'] is None
    assert token['case_count']>=50 and token['common_support']['size']==151665
    assert token['mapping_difference_count']==0 and token['all_raw_encodings_identical']
    for meta in data['files'].values():
        path = ROOT/meta['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['sha256']
        with path.open(encoding='utf-8') as f: assert sum(1 for _ in f)==meta['rows']
    assert demo['paid_api_calls']==0 and demo['synthesis']['state']=='accepted'
    for p in (ROOT/'data').rglob('*'):
        assert p.suffix not in {'.safetensors','.bin','.pt','.pth'}
    result = {'status':'passed','test_count':int(match[1]),'test_seconds':float(match[2]),
              'scope':'All four requested CPU infrastructure tasks; no GPU or real API training validation',
              'requirements':{'task3_real_support_losses':'tests/test_losses_and_masks.py',
                              'task1_real_tokenizers':'reports/tokenizer_alignment_report.json',
                              'task2_real_data':'data/math_manifest.json',
                              'task2_adversarial_verifier':'tests/test_math_verifier.py',
                              'task4_mock_client':'tests/test_synthesis_client.py',
                              'task4_geometry_attacks':'tests/test_geometry_parser.py'}}
    return result


def finalize():
    result = audit()
    (ROOT/'reports/completion_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    artifacts = []
    for folder in ['src','tests','scripts','data','reports']:
        for path in sorted((ROOT/folder).rglob('*')):
            if not path.is_file() or any(s in path.parts for s in ['__pycache__','.cache']): continue
            if path.name in {'overnight_execution_summary.md','artifact_inventory.json'}: continue
            artifacts.append({'path':path.relative_to(ROOT).as_posix(),'bytes':path.stat().st_size,
                              'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    for name in ['pyproject.toml','docs/migration/overnight_cpu_20261023.md']:
        path = ROOT/name
        artifacts.append({'path':name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    (ROOT/'reports/artifact_inventory.json').write_text(json.dumps(artifacts,ensure_ascii=False,indent=2),encoding='utf-8')
    summary = ROOT/'reports/overnight_execution_summary.md'
    text = summary.read_text(encoding='utf-8').split('<!-- FINAL_AUDIT -->')[0]
    text = text.replace('状态：进行中。','状态：四项 CPU 交付已完成，最终验收通过。')
    data = read_json('data/math_manifest.json')
    token = read_json('reports/tokenizer_alignment_report.json')
    lines = ['','<!-- FINAL_AUDIT -->','## 最终验收','',
        f'完整命令 `python -m pytest tests -v`：**{result["test_count"]} passed in {result["test_seconds"]}s**，无失败、无跳过。',
        '真实数据与词表脚本均已执行；Mock 端到端示例已执行并保存 SQLite/JSONL 缓存。',
        '付费 API 调用 0；模型权重下载 0；GPU 训练 0。使用 CPU 专版 torch（CUDA version=None）。',
        '最终核验结果：`reports/completion_audit.json`；环境：`reports/cpu_environment.json`。','',
        '### 最终数据行数','']
    lines += [f'- `{name}`：{meta["rows"]} 行，路径 `{meta["path"]}`。' for name,meta in data['files'].items()]
    lines += ['', '### 词表核心结论','',
        '四模型 len(tokenizer)=151665；学生输出矩阵 151936 行，其余三模型 152064 行。共同有效 ID 为 0～151664。',
        '64 条裸文本编码一致，64 条应用各自 chat template 后均出现组间差异。必须固定学生原始 token 前缀，不能独立渲染模板后直接对齐。',
        '共同支持上切片并重新归一化；生成前屏蔽已确认无效行。没有加载权重，尚无尾部概率质量的真实测量。','',
        '### 额外恢复与边界检查','',
        '- 验证器崩溃后复用已落盘输出；跨重启预算累计；JSONL 可恢复 SQLite；重复并发任务只执行一次 Mock。',
        '- 原文 SHA256、规范化 SHA256 与近重复检测分别留证；独立测试检查 train 与 dev/test 仍无当前规则下重叠。',
        '- 受限表达式解析防止 eval、恶意调用和嵌套大整数幂；不是覆盖所有数学对象的官方判分器。',
        '- 几何 F1 防重复刷分，支持关系反序规范化、冲突拒绝；不完整标注按覆盖类别处理，无可信标签时感知项关闭。',
        '- 四个设计文件未修改，旧 tiny_posttrain 源码和历史结果未改动；当前借用其现有 CPU 虚拟环境。','',
        '### 文件清单','',
        '以下为源文件、测试、脚本、数据与报告的实际路径（不列 Python bytecode 和下载器内部 .cache）；逐文件 SHA256 见 `reports/artifact_inventory.json`。','']
    lines += ['- `'+a['path']+'`' for a in artifacts]
    lines += ['- `reports/artifact_inventory.json`','- `reports/overnight_execution_summary.md`','',
              '### pytest -v 完整原始输出','', '```text',
              (ROOT/'reports/pytest_full.log').read_text(encoding='utf-8').rstrip(), '```','',
              '### 尚未验证边界','',
              '不包含 GPU 训练、真实 logits 尾部质量、付费合成、真实图像标签质量、真实 OPD 性能或训练收益。',
              '词法去重不能证明消除语义/预训练污染；几何 parser 仅注册 schema；数学 verifier 有意拒绝不支持的对象和不明确的答案。',
              '后续运行说明：`docs/migration/overnight_cpu_20261023.md`。']
    summary.write_text(text+'\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'audit':result['status'],'tests':result['test_count'],'inventory_files':len(artifacts)}))


if __name__=='__main__': finalize()
