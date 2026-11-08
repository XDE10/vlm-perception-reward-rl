"""Create three self-contained migration copies without changing project sources."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import zipfile
from importlib.metadata import version

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '实习项目迁移_20261024'
NAMES = {1: '项目一_7B数学后训练', 2: '项目二_双教师在线蒸馏', 3: '项目三_多模态几何推理'}
BLUEPRINTS = {1: '项目一_7B数学后训练_详细实施方案.md', 2: '项目二_双教师在线蒸馏_详细实施方案.md', 3: '项目三_多模态几何推理_详细实施方案.md'}
RELEASE = 'data/strict_v8_20261024/release'
SKIP = {'__pycache__', '.pytest_cache', '.git', '.venv', 'backups', 'shared_api_cache', 'shared_api_cache_partial_do_not_use'}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def relative_value(value):
    if isinstance(value, dict):
        return {k: relative_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [relative_value(v) for v in value]
    if isinstance(value, str):
        normalized = value.replace('\\', '/')
        prefix = ROOT.as_posix() + '/'
        if normalized.lower().startswith(prefix.lower()):
            return normalized[len(prefix):]
    return value


VERIFY = r'''"""Offline migration verification; run from any working directory."""
import argparse,hashlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0,str(ROOT))

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--full',action='store_true',help='Also hash all archived files and source snapshots')
    args=parser.parse_args()
    m=json.loads(Path('migration_manifest.json').read_text(encoding='utf8'))
    errors=[]
    for f in m['files']:
        p=Path(f['path'])
        if not p.is_file():errors.append('missing: '+str(p))
        elif p.stat().st_size!=f['bytes']:errors.append('size changed: '+str(p))
        elif args.full and sha(p)!=f['sha256']:errors.append('hash changed: '+str(p))
    release=Path('data/portable_release')
    rm=json.loads((release/'manifest.json').read_text(encoding='utf8'))
    from src.data.approved_training_inputs import load_approved,model_view
    counts={}
    for name,digest in rm['files'].items():
        p=release/name
        if sha(p)!=digest:errors.append('release hash changed: '+name)
    for name in rm['approved_training_files']:
        rows=load_approved(release/'manifest.json',name)
        counts[name]=len(rows)
        profile='perception_sft' if name.startswith('project3') else ('opd' if name.startswith('project2') else 'math_sft')
        for row in rows:model_view(row,profile)
    for name in rm.get('approved_evaluation_files',[]):
        counts[name]=sum(bool(line.strip()) for line in (release/name).read_text(encoding='utf8').splitlines())
    for name in rm['files']:
        if not name.endswith('.jsonl'):continue
        with (release/name).open(encoding='utf8') as f:
            for line in f:
                if not line.strip():continue
                row=json.loads(line)
                if 'image_path' in row:
                    p=Path(row['image_path'])
                    if p.is_absolute() or not p.is_file():errors.append('image path invalid: '+str(p))
                    elif row.get('image_sha256') and sha(p)!=row['image_sha256']:errors.append('image changed: '+str(p))
    for p in Path('configs').glob('*.json'):
        c=json.loads(p.read_text(encoding='utf8'))
        for k in ['data_manifest','tokenizer_path','tokenizer_audit']:
            if k in c and (re_absolute(c[k]) or not Path(c[k]).exists()):errors.append('config path invalid: '+str(p)+' '+k)
        for k in ['model','output_dir']:
            if k in c and re_absolute(c[k]):errors.append('absolute config path: '+str(p)+' '+k)
    result={'project':m['project'],'files':len(m['files']),'full_hash_check':args.full,'release_rows':counts,'errors':errors,'gpu_run':False}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)

def re_absolute(s):
    return Path(s).is_absolute() or (len(s)>2 and s[1]==':' and s[2] in '/\\')

if __name__=='__main__':main()
'''


def build(project):
    dest = OUT / NAMES[project]
    if (dest / 'migration_manifest.json').exists():
        raise FileExistsError('Refusing to overwrite a completed package')
    dest.mkdir(parents=True, exist_ok=True)
    copied = {}

    def copy_file(source):
        rel = source.relative_to(ROOT)
        if any(part in SKIP for part in rel.parts) or source.suffix == '.pyc' or source.name.startswith('.env'):
            return
        target = dest / rel
        if target.exists():
            copied[rel.as_posix()] = {'source_sha256': sha(source)}
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied[rel.as_posix()] = {'source_sha256': sha(source)}

    def copy_tree(source):
        if source.is_file():
            copy_file(source)
            return
        for directory, dirs, files in os.walk(source):
            dirs[:] = [d for d in dirs if d not in SKIP]
            for name in files:
                copy_file(Path(directory) / name)

    # Small code modules and original evidence are shared across the pipeline.
    # Duplicating them intentionally removes all sibling-folder dependencies.
    for folder in ['src', 'scripts', 'tests', 'project_blueprints', 'reports']:
        copy_tree(ROOT / folder)
    for path in (ROOT / '.pilot_deps').iterdir():
        # sympy/mpmath are installed through the recorded requirements instead.
        if path.name.startswith(('math_verify', 'latex2sympy2_extended', 'antlr4')):
            copy_tree(path)
    cache_archive = OUT / '_shared_api_cache.zip'
    cache_target = dest / 'reports/data_release_preparation_20261024/shared_api_cache.zip'
    cache_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(cache_archive, cache_target)
    for name in ['pytest.ini', 'requirements-project3-cpu.txt', 'OVERNIGHT_CPU_README.md', '.gitignore']:
        copy_file(ROOT / name)
    common = {'math', 'raw_math_cache', 'tokenizers', 'synthesis_mock', 'delegated_ai_releases_20261024',
              'topup_v6_20261024', 'finalfill_v7_20261024', 'strict_v8_20261024'}
    for path in (ROOT / 'data').iterdir():
        if path.is_file() or path.name in common or path.name.startswith(f'project{project}'):
            copy_tree(path)
        elif project == 1 and (path.name.startswith('compact_distillation') or path.name.startswith('deepseek_pilot')):
            copy_tree(path)
        elif project == 2 and path.name in {'code_benchmarks', 'code_v2_pilot', 'code_v2_sources'}:
            copy_tree(path)
    screening = ROOT / 'data/screening_sources'
    if project in (1, 2):
        copy_tree(screening / ('openr1' if project == 1 else 'code'))
        for path in screening.glob('*'):
            if path.is_file() and (('openr1' in path.name) == (project == 1)):
                copy_file(path)
    print(f'COPIED {NAMES[project]}: {len(copied)} files', flush=True)

    # Preserve original release bytes and hashes. Create an explicitly derived,
    # project-scoped runtime release; only image_path is rewritten in visual rows.
    original_manifest = json.loads((ROOT / RELEASE / 'manifest.json').read_text(encoding='utf-8'))
    runtime = dest / 'data/portable_release'
    runtime.mkdir()
    selected = [n for n in original_manifest['files'] if n.startswith(f'project{project}_')]
    selected.append(original_manifest['protected_dev_ids_file'])
    transforms = []
    for name in selected:
        source = ROOT / RELEASE / name
        target = runtime / name
        if project == 3 and name.endswith('.jsonl'):
            rows = []
            with source.open(encoding='utf-8') as f:
                for line in f:
                    row = json.loads(line)
                    if 'image_path' in row:
                        rel = relative_value(row['image_path'])
                        if rel == row['image_path']:
                            raise ValueError('Unknown image location: ' + rel)
                        image = ROOT / rel
                        if sha(image) != row['image_sha256']:
                            raise ValueError('Source image changed: ' + rel)
                        copy_file(image)
                        row['image_path'] = rel
                    rows.append(row)
            target.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')
        else:
            shutil.copy2(source, target)
        transforms.append({'source': f'{RELEASE}/{name}', 'source_sha256': sha(source),
                           'portable': target.relative_to(dest).as_posix(), 'portable_sha256': sha(target),
                           'change': 'image_path_only' if project == 3 and name.endswith('.jsonl') else 'byte_identical'})
    manifest = dict(original_manifest)
    manifest['approved_training_files'] = [n for n in original_manifest['approved_training_files'] if n in selected]
    manifest['approved_evaluation_files'] = [n for n in original_manifest['approved_evaluation_files'] if n in selected]
    manifest['files'] = {name: sha(runtime / name) for name in selected}
    manifest['migration'] = {'source_manifest': f'{RELEASE}/manifest.json',
                             'source_manifest_sha256': sha(ROOT / RELEASE / 'manifest.json'),
                             'project': project, 'changes': transforms,
                             'approval_scope': 'Inherited original row approvals; no new approval or content changes'}
    dump(runtime / 'manifest.json', manifest)
    configs = dest / 'configs'
    configs.mkdir()
    for path in (ROOT / 'data/strict_v8_20261024/training_configs').glob(f'project{project}_*.json'):
        c = relative_value(json.loads(path.read_text(encoding='utf-8')))
        c['data_manifest'] = 'data/portable_release/manifest.json'
        dump(configs / path.name, c)

    # Follow existing local Markdown links so referenced notes and image previews
    # travel with each copy. Resolve original absolute links into relative links.
    link_re = re.compile(r'(!?\[[^\]\n]*\]\()(<[^>\n]+>|[^)\n]+)(\))')
    examined = set()
    while True:
        pending = [p for p in dest.rglob('*.md') if p.relative_to(dest).as_posix() not in examined]
        if not pending:
            break
        for path in pending:
            rel_path = path.relative_to(dest)
            examined.add(rel_path.as_posix())
            try:
                text = path.read_text(encoding='utf-8')
            except UnicodeError:
                continue

            def replace_link(match):
                from urllib.parse import unquote
                raw = match.group(2).strip('<>')
                if re.match(r'^(?:https?://|mailto:|#|data:|codex:|plugin:)', raw):
                    return match.group(0)
                value, sep, fragment = raw.partition('#')
                value = unquote(value).replace('\\', '/')
                prefix = ROOT.as_posix() + '/'
                if value.lower().startswith(prefix.lower()):
                    source = ROOT / value[len(prefix):]
                elif re.match(r'^[A-Za-z]:', value) or value.startswith('/'):
                    return match.group(0)
                else:
                    source = (ROOT / rel_path.parent / value).resolve()
                if not source.is_relative_to(ROOT) or not source.is_file():
                    return match.group(0)
                copy_file(source)
                local = os.path.relpath(dest / source.relative_to(ROOT), path.parent).replace('\\', '/')
                if sep:
                    local += '#' + fragment
                return match.group(1) + '<' + local + '>' + match.group(3)

            revised = link_re.sub(replace_link, text)
            # Old venv paths are local setup details, not transferable runtimes.
            revised = re.sub(r'(?:\.\\)?tiny_posttrain\\\.venv\\Scripts\\python\.exe', 'python', revised)
            revised = revised.replace('tiny_posttrain/.venv/Scripts/python.exe', 'python')
            if revised != text:
                path.write_text(revised, encoding='utf-8')

    (dest / 'tools').mkdir()
    (dest / 'tools/verify_migration.py').write_text(VERIFY, encoding='utf-8')
    packages = ['torch','transformers','trl','peft','datasets','accelerate','pytest','numpy','sympy','tokenizers','pyarrow','requests','Pillow']
    pins = [p + '==' + version(p).replace('+cpu', '') for p in packages]
    (dest / 'requirements-cpu-snapshot.txt').write_text(
        '# Recorded local CPU versions; not a validated Linux/CUDA lock file.\n' + '\n'.join(pins) + '\n', encoding='utf-8')
    tests = {1: 'tests/test_approved_training_inputs.py tests/test_training_entries_cpu.py tests/test_losses_and_masks.py',
             2: 'tests/test_approved_training_inputs.py tests/test_training_entries_cpu.py tests/test_opd_contract.py tests/test_losses_and_masks.py',
             3: 'tests/test_approved_training_inputs.py tests/test_training_entries_cpu.py tests/test_perception_v4.py tests/test_geometry_model_serialization.py'}
    entries = {1: 'python -m scripts.train_project1_sft --config configs/project1_raw_sft_smoke.json\npython -m scripts.train_project1_sft --config configs/project1_compact_sft_smoke.json\npython -m scripts.train_project1_rl --config configs/project1_compact_grpo_smoke.json',
               2: 'python -m scripts.train_project2_opd --config configs/project2_opd_smoke.json',
               3: 'python -m scripts.train_project3 --config configs/project3_fact_sft_smoke.json\npython -m scripts.train_project3 --config configs/project3_sparse_v4_grpo_smoke.json'}
    status = {1: '当前批准的原生/精炼同题轨迹各 1500 条；另有 4810 条 RL 优先候选，候选不是 rollout 筛选后的正式 RL 池。',
              2: '数学 2500 train / 256 dev；代码 2500 train / 200 dev，代码 train 函数和 stdin/stdout 各 1250 条。',
              3: '当前逐事实批准子集 609 train / 82 validation；图片随包保留，只有已认证事实可用于稀疏奖励。'}
    (dest / 'README.md').write_text(f'''# {NAMES[project]}

本文件夹是 2026-10-24 的独立迁移副本。直接把整个文件夹复制到新位置即可，不依赖原 modern_genai 目录或另外两个项目文件夹。原仓库文件保留。

{status[project]}

数据批准沿用 Strict v8 的逐项 AI 审核及确定性检查，不是人工金标。GPU/A100 训练和验收尚未运行，smoke 配置默认仅 2 步。

## 从这里开始

- [本项目详细方案](project_blueprints/{BLUEPRINTS[project]})。
- [最新数据封板说明](project_blueprints/Strict_v8_数据封板与上卡说明.md)。
- [最新执行报告](reports/strict_v8_20261024/执行报告.md)。
- [可迁移数据清单](data/portable_release/manifest.json)：本项目运行入口只使用这个清单。
- `configs/`：已改成相对路径的本项目最新配置。`project_blueprints/configs/` 和原始数据目录下的配置属于历史留档。
- `src/`、`scripts/`、`tests/`：保留共用代码及其导入依赖；部分脚本服务于其他项目或历史流水线，运行主线见下方命令。
- `data/`：本项目历史数据、源快照、共用数学集、tokenizer、审核依据和图片。共用 release/报告保留交叉审核证据，并不扩大本项目训练范围。

## 迁移后先校验

任何目录下都可以执行下列校验脚本；训练和测试命令需先进入本文件夹根目录。

```bash
python tools/verify_migration.py
python tools/verify_migration.py --full
```

第一条核对文件存在性/大小、当前数据 SHA、批准范围、模型输入白名单、配置依赖和图片 SHA；第二条额外核对全部归档文件 SHA。均离线执行，不下载模型、不调用 API。

## 环境与本地检查

本机原环境使用 Python 3.12。新电脑请新建虚拟环境，不能直接迁移 Windows venv。`requirements-cpu-snapshot.txt` 记录本次本机 CPU 环境版本，可用于恢复模块检查环境；CUDA/PyTorch 安装需匹配目标 GPU，尚未提供已经实测的 Linux GPU 锁文件。数学验证依赖 `.pilot_deps/` 已随包保留（含许可证），无需借用原仓库的隐藏目录。

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements-cpu-snapshot.txt
python -m pytest {tests[project]} -q
```

## GPU 工程入口

以下命令留给目标 GPU 环境，本次整理未启动训练：

```bash
{entries[project]}
```

SFT 后的 RL 配置依赖前一步实际导出的 `runs/.../merged/` 及权重身份清单；本包未附模型权重或训练结果。项目三视觉诊断可以使用 `data/portable_release/project3_validation_fact_pruned.jsonl`，保持与训练划分隔离。模型仍按配置固定 revision 下载。

## 归档与修改范围

原始 JSON/JSONL、源文件与审核缓存按字节复制，源 SHA 记录在 `migration_manifest.json`。`data/portable_release/` 为独立派生运行副本：只保留本项目文件，项目三仅将 `image_path` 改为包内相对路径并重算其文件 SHA；题目、答案、标签、图片内容与批准状态不变。其 manifest 记录原始/派生哈希和转换范围。

共用 API 审核缓存包含 15119 个小文件，已完整压缩为 `reports/data_release_preparation_20261024/shared_api_cache.zip` 随包保留。查阅原始请求或恢复历史审核流水线前可执行：`python -m zipfile -e reports/data_release_preparation_20261024/shared_api_cache.zip reports/data_release_preparation_20261024/shared_api_cache`。当前训练及离线迁移校验无需解压。

Markdown 内已有且能定位到源文件的本地链接已改为包内链接，并补齐链接目标。历史报告中的绝对路径文字和旧配置保留为溯源，不用作当前运行入口。跨项目历史说明中的旧数量以本 README 和 Strict v8 清单为准。

没有打包 `.git/`、虚拟环境、`__pycache__/`、pytest 缓存和 `reports/backups/` 的重复备份；无模型权重、密钥文件或原仓库其他无关课程目录。不能仅凭迁移校验通过声称 GPU 训练已完成。
''', encoding='utf-8')

    # Bundle metadata hashes every payload file. Metadata itself is excluded.
    files = []
    for path in sorted(dest.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(dest).as_posix()
        item = {'path': rel, 'bytes': path.stat().st_size, 'sha256': sha(path)}
        if rel in copied:
            item.update(copied[rel])
            item['changed_for_portability'] = item['sha256'] != item['source_sha256']
        files.append(item)
    dump(dest / 'migration_manifest.json', {'project': NAMES[project], 'date': '2026-10-24',
         'source_root': str(ROOT), 'files': files,
         'omitted': ['.git', 'virtual environments', '__pycache__', '.pytest_cache', 'reports/backups', 'unrelated raw source shards'],
         'gpu_runs_during_migration': 0})
    summary = {'project': NAMES[project], 'files': len(files), 'bytes': sum(f['bytes'] for f in files)}
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return summary


def main():
    if OUT.exists() and any(OUT.glob('*/migration_manifest.json')):
        raise FileExistsError('Refusing to overwrite completed migration output: ' + str(OUT))
    OUT.mkdir(exist_ok=True)
    archive = OUT / '_shared_api_cache.zip'
    if not archive.exists():
        source = ROOT / 'reports/data_release_preparation_20261024/shared_api_cache'
        with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as z:
            for p in source.rglob('*'):
                if p.is_file():
                    z.write(p, p.relative_to(source).as_posix())
        print('ARCHIVED complete API review cache', flush=True)
    summaries = [build(p) for p in [1, 2, 3]]
    if all(sha(OUT / NAMES[p] / 'reports/data_release_preparation_20261024/shared_api_cache.zip') == sha(archive) for p in [1, 2, 3]):
        archive.unlink()
    dump(OUT / '迁移汇总.json', summaries)
    lines = ['# 实习项目迁移副本', '', '三个文件夹可分别独立复制出去；原仓库保持不变。每个文件夹先阅读 README.md。', '']
    for project, summary in zip([1, 2, 3], summaries):
        lines.append(f'- [{NAMES[project]}]({NAMES[project]}/README.md)：{summary["files"]} 个文件，约 {summary["bytes"]/1024**3:.2f} GiB。')
    lines.extend(['', '各包包含代码、项目资料、数据、审核报告、源快照及必要图片；共用代码/证据在每包中各保留一份。', '', '校验：`python tools/verify_migration.py --full`。校验记录见同目录迁移验收文件。'])
    (OUT / 'README.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
