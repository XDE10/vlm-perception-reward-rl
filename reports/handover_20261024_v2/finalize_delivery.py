"""Seal delivery evidence without altering any source release or migration SHA."""
import ast
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()

def main():
    log=(OUT/'acceptance_final.log').read_text(encoding='utf8')
    assert re.search(r'34 passed',log) and 'failed' not in log and 'ERROR' not in log
    pip=(OUT/'pip_check.log').read_text(encoding='utf8');assert 'No broken requirements found' in pip
    sampling=json.loads((OUT/'sampling_report.json').read_text(encoding='utf8'))
    assert sampling['api_calls']==0 and sampling['source_sha256_before']==sampling['source_sha256_after']
    checked={p:sha(ROOT/p) for p in sampling['source_sha256_before']}
    assert checked==sampling['source_sha256_before']
    migration=json.loads((OUT/'verify_migration_full.log').read_text(encoding='utf8'))
    assert not migration['errors'] and migration['full_hash_check']
    original=json.loads((ROOT/'migration_manifest.json').read_text(encoding='utf8'))
    tracked={r['path']:r['sha256'] for r in original['files']}
    frozen=['src/data/perception_v4.py','src/training/approved_hf.py','src/data/approved_training_inputs.py','scripts/diagnose_project3_vision.py',
            'configs/project3_fact_sft_smoke.json','configs/project3_sparse_v4_grpo_smoke.json','README.md','AGENTS.md',
            'data/portable_release/manifest.json','data/portable_release/project3_train_fact_pruned.jsonl','data/portable_release/project3_validation_fact_pruned.jsonl']
    assert all(sha(ROOT/p)==tracked[p] for p in frozen)
    maps=[]
    for p in sorted(OUT.glob('*.py')):
        tree=ast.parse(p.read_text(encoding='utf8'),filename=str(p))
        for node in tree.body:
            if isinstance(node,(ast.ClassDef,ast.FunctionDef)):
                maps.append(f"- `{p.name}:{node.lineno}` — `{node.name}`")
    (OUT/'源码地图.md').write_text('# v2源码入口与行号\n\n'+ '\n'.join(maps)+'\n\n原冻结逻辑：src/data/perception_v4.py:103（scoped_score）；src/data/perception_v4.py:7（审核SYSTEM）；scripts/build_geometry_funnel_v8.py:12（漏斗分类）；src/data/approved_training_inputs.py:6（准入加载）。原文件未修改。\n',encoding='utf8')
    with zipfile.ZipFile(OUT/'blind_review_only.zip') as z:
        assert len(z.namelist())==82 and all(n.startswith('blind/') and 'key.jsonl' not in n for n in z.namelist())
        for name in z.namelist():
            assert hashlib.sha256(z.read(name)).hexdigest()==sampling['blind_export_files'][name.removeprefix('blind/')]
    record={'date':'2026-10-24','python':'D:/anaconda3/envs/genai-test/python.exe',
        'README_original_tests':'15 passed; original tests unchanged','final_combined_tests':'34 passed (15 original + 19 new cases)',
        'final_log':'acceptance_final.log','pip_check':pip.strip(),'migration_full_hash':migration,
        'frozen_source_files_unchanged':{p:sha(ROOT/p) for p in frozen},'sampling_sources_rechecked':checked,
        'blind_only_zip_sha256':sha(OUT/'blind_review_only.zip'),'api_calls':0,'model_downloads':0,'GPU_training_runs':0,
        'unverified':['actual VL processor assistant-label token counts','actual Qwen trainable-module mapping','VL forward/backward and visual rollout','checkpoint optimizer/RNG recovery','Linux/CUDA/Colab installation','A100 memory peak','human blind reviews and error rates']}
    (OUT/'delivery_checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (OUT/'验收记录.md').write_text('''# 本轮验收记录

日期：2026-10-24。已完成的是离线实现、文档、盲审材料和CPU验收，没有模型下载、付费API或GPU训练。

- genai-test：Python3.12.15，最终pip安装命令退出0；pip check无冲突，pip freeze留档。
- 原README四文件测试：15 passed（readme_pytest.log）；既有测试未改。
- 最终合并：**34 passed**，包括15个原用例和19个新用例，见acceptance_final.log。中途33/34等日志只作开发历史，不重复相加。
- NumPy899个、PEFT227个安装RECORD哈希逐项匹配，排除先前文件锁造成这两个包文件不完整的疑问（installation_record_integrity.json）。
- 原迁移4258个清单文件完整SHA检查通过，609/82不变；关键冻结源码/配置/数据与旧清单再次比对一致。
- 691条target新旧评分差异0；V3/V4仅感知权重不同；新V1/V2数据视图不改原行；真实TRL奖励派发测试无train/generate/backward。
- 75题抽样固定、train/validation限定、五批各15、长边≤1200；PNG输出元数据清除，所有blind图片像素在清理ICC前后不变，原图未动。
- blind目录泄漏检测通过；数字巧合按用户确认单列。盲审ZIP仅82个blind文件，不含key/manifest。其SHA见blind_review_only.sha256。
- 原始AI状态与解析状态分列：75题中1条原pass因task_issues被解析降级为uncertain，原抽样与批准不改。不是把AI原始pass改写为AI原始uncertain。
- 采样输入SHA前后匹配，交付封存时再次检查仍一致；api_calls=0。

可运行入口与原文审核提示词见README.md；按函数的源码行号见源码地图.md；原始命令结果与所有指纹见delivery_checks.json、各log及delivery_inventory.json。

真实VL监督token数、实际Qwen前后向/rollout/恢复、视觉模块实机冻结、Colab/Linux/CUDA安装和A100显存均**未验证**。colab_bootstrap.sh只做静态阅读，未在Linux执行或以bash -n验收；候选依赖不是实测CUDA锁。75题还未进行独立人工复核，误杀/误放率**未验证**。
''',encoding='utf8')
    inventory={p.relative_to(OUT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='delivery_inventory.json'}
    (OUT/'delivery_inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'final_tests':'34 passed','blind_zip_files':82,'inputs_unchanged':True,'api_calls':0,'files_in_inventory':len(inventory)},ensure_ascii=False))

if __name__=='__main__':main()
