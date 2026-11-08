"""Run only local CPU audit, after prepare_project3_sources.py."""
import json
import hashlib
from pathlib import Path
from src.data.project3_audit import run

if __name__=='__main__':
    summary=run(Path('data/project3_sources'),Path('data/project3_audit'))
    target=Path('reports/project3_cpu_20261023')
    target.mkdir(parents=True,exist_ok=True)
    (target/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# 项目三 CPU 数据关联与重叠审计（2026-10-23）','',
           '本报告来自实际下载的固定 revision 数据和本地 CPU 审计。未运行 GPU、未调用付费 API、未宣称人工检查已完成。','',
           '## 原始来源与复现','',
           '- InterGPS: `99e6b5293c7bb4a5eaf2a370e6b213c79ab33ebb`，MIT 仓库许可。',
           '- hiyouga/geometry3k: `fd21e533e1e50d0662a2bf7b223e60511bd5f8b7`，包装卡 MIT。',
           '- AI4Math/MathVista: `2b6ad69445fbb5695c9b165475e8decdbeb97747`，数据卡 CC-BY-SA-4.0。',
           '- 原 textbook 内容及各来源可能有独立条款；保留源 README/LICENSE，包装许可不能自动重许可底层素材。',
           '- 文件、来源 URL、大小和 SHA256 见 `data/project3_sources/manifest.json`。',
           '- 本轮实际解释器：Python 3.11.4（独立安装，不依赖 PATH），Pillow 11.2.1、pyarrow 20.0.0、requests 2.32.4。不能假定 PATH 的 `python` 或训练 venv 已具备这些可选依赖。',
           '- 本机复现：从仓库根目录执行 `python scripts/data/prepare_project3_sources.py`，然后执行 `python -m scripts.data.audit_project3_overlap`。',
           '- 推荐隔离安装：`py -3.11 -m venv .venv-project3-cpu`；`& .\\.venv-project3-cpu\\Scripts\\python.exe -m pip install -r requirements/project3-cpu.txt`；再使用该解释器运行上述两个入口。不修改训练环境的依赖。',
           '- 测试：`$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD="1"; & .\\.venv-project3-cpu\\Scripts\\python.exe -m pytest tests/test_project3_audit.py -q`。本轮在上述 D 盘解释器运行，3 passed；训练 venv 缺少可选 Pillow/pyarrow 时该模块明确 skip，不是审核成功。',
           '', '## 真实关联方法','',
           '包装数据没有原始 ID，`train:0` 等仅是文件定位。先按解码后的 RGB 像素与尺寸哈希查找原图，再以保留数学符号的规范化题面核验；从原始 data.json 读取 ID 与 split。',
           '标注使用官方 logic_forms.zip 的 diagram_logic_forms_annot.json、text_logic_forms_annot.json 和 text_logic_forms_annot_dissolved.json，不使用解析器预测。同时保留每题 zip 内 logic_form.json，比较其与全局标注包的集合一致性，冲突不覆盖。','',
           '## 实际统计','']
    for key,value in summary.items():
        if key!='limitations':
            lines.append(f'- `{key}`: {json.dumps(value,ensure_ascii=False)}')
    lines += ['', '## 产物与边界','',
              '- `intergps_annotations.jsonl` 保留原始题面、选择题答案、原图哈希与三类源标注。',
              '- `geometry3k_intergps_links.jsonl` 逐条记录候选 ID、题面/答案/划分检查和状态。',
              '- `mathvista_testmini_overlap.jsonl` 保留每题来源、精确图像与题面命中 ID/划分。',
              '- `mathvista_source_disjoint_ids.json` 是排除 Geometry3K 来源及已知精确重叠的自定义子集；官方完整 testmini 仍是 1000 题，应分别报告。',
              '- `manual_link_review_30_pending.jsonl` 是三划分各 10 题的待审工作单，状态全部 pending，不能当作人工抽检通过。',
              '- 标注存在不等于它们都是图像独占事实，AST/文字蕴含排除/100～200 训练题独立审计仍未完成，因此项目三训练还没有数据准入结论。', '']
    lines += ['- '+item for item in summary['limitations']]
    (target/'审计报告.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    files=[p for p in Path('data/project3_audit').glob('*') if p.is_file()]
    (target/'artifact_hashes.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
