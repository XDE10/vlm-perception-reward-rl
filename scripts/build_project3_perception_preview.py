"""Incremental supplement; does not modify the frozen 200-case prototype."""
import hashlib
import json
from pathlib import Path
from collections import Counter
from src.data.project3_perception_preview import preview,VERSION

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/project3_perception_preview'
REPORT=ROOT/'reports/project3_perception_review'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(path):return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
def jsonl(path,values):path.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in values),encoding='utf-8')

def run():
    if DATA.exists() or REPORT.exists():raise FileExistsError('Incremental supplement exists; preserve historical artifacts')
    DATA.mkdir();REPORT.mkdir()
    source=ROOT/'data/project3_perception_prototype/prototype_200.jsonl'
    manual_source=ROOT/'data/project3_perception_prototype/manual_image_review_30_pending.jsonl'
    cases=rows(source);by_id={x['original_id']:x for x in cases}
    result=[]
    for case in cases:
        value=preview(case['diagram_facts'])
        value.update(original_id=case['original_id'],split='train',wrapper_locator=case['wrapper_locator'],
                     image_path=case['image_path'],source_visual_candidate_count=sum(x['category']=='visual_candidate' for x in case['diagram_facts']))
        result.append(value)
    jsonl(DATA/'canonical_perception_preview.jsonl',result)
    review=[]
    md=['# 30 题包装记录与原始标注关联核查（全部 pending）','',
        '`wrapper_locator` 是 Geometry3K 包装 parquet 的 split:行偏移定位；包装不含原始官方 ID，不能将行偏移当作官方 ID。`intergps_original_id` 才是 InterGPS 原始 data.json ID。','',
        '原图为真实 InterGPS train 原图；下面展示的是待审工作单，不代表已完成人工或 AI 复核。','']
    for old in rows(manual_source):
        case=by_id[old['original_id']]
        value=dict(old,wrapper_locator=case['wrapper_locator'],intergps_original_id=old['original_id'],
                   wrapper_id_note='Packaging has no official original ID; wrapper_locator is split:row_offset only',
                   source_locator=case['source_locator'])
        review.append(value)
        image=Path(case['image_path']).as_posix()
        md += [f"## InterGPS 原始 ID {case['original_id']} / Geometry3K 包装定位 {case['wrapper_locator']}",'',
               f"原始源定位：`{case['source_locator']}`；题面：{case['question']}",'',
               f"参考答案：`{case['answer']}`",'',f'[打开原图]({image})','',f'![原图 {case["original_id"]}]({image})','',
               '原始 diagram logic forms：','','```text',*case['diagram_raw'],'```','',
               '原始 text logic forms：','','```text',*case['text_raw'],'```','',
               '人工审核 pending：关联正确性 / 图像支持 / 题干蕴含 / 视觉独占性 / 坐标适用性均待签字；training_approved=false。','']
    jsonl(REPORT/'manual_link_review_30.jsonl',review)
    dump(REPORT/'manual_link_review_30.json',review)
    (REPORT/'manual_link_review_30.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    schema=dict(version=VERSION,relation_order=['Angle','Length','Parallel','Perpendicular','Tangent'],
                sort='relation order, normalized entity lexical order, canonical rational value, unit; then exact deduplication',
                angle='Sort only outer endpoints; preserve middle vertex.',tangent='First argument is line endpoint pair, second is circle center; never exchange roles.',
                line='Sort the two line endpoints. Sort both lines only for symmetric Parallel/Perpendicular.',
                values='Fraction canonical rational, e.g. 1.0=>1 and 2/4=>1/2; Angle deg, Length unspecified source unit (no invented unit).',
                conflicts='Different numeric values for same relation/entities, or same line pair both Parallel and Perpendicular: quarantine all conflicting candidates.',
                scope='Only existing visual_candidate facts are serialized. No Congruent extension and no production reward parser modification.',
                semantics='Review-only serialization; unreviewed source coordinate/image/prose issues remain. Empty perception means no retained candidate, not that image contains no facts.',
                human_review='pending',training_approved=False)
    dump(DATA/'schema.json',schema)
    summary=dict(cases=len(result),split_counts=dict(Counter(x['split'] for x in result)),manual_links=len(review),
                 input_visual_candidates=sum(x['source_visual_candidate_count'] for x in result),
                 canonical_after_dedup=sum(len(x['canonical_facts']) for x in result),
                 cases_with_nonempty_preview=sum(bool(x['canonical_facts']) for x in result),
                 quarantined_count=sum(len(x['quarantined']) for x in result),
                 human_reviewed_count=0,training_approved_count=0)
    dump(REPORT/'summary.json',summary)
    lines=['# 项目三规范序列化增量预览说明','',
           '[30 题双定位原图核查单](manual_link_review_30.md)。机器预览：`data/project3_perception_preview/canonical_perception_preview.jsonl`。','',
           'Angle → Length → Parallel → Perpendicular → Tangent；每类按规范实体字典序及规范有理数值排序、去重，保留角顶点与相切角色。冲突隔离；原事实、原顺序和旧封存产物均未改变。','',
           '所有预览均 review_only=true、human_review=pending、training_approved=false；它们不能直接作为感知奖励金标。','']
    lines += ['- `'+key+'`: '+str(value) for key,value in summary.items()]
    lines += ['', '## 200 题规范预览','']
    for value in result:
        lines += [f"### ID {value['original_id']} / {value['wrapper_locator']}",'','```text',value['canonical_perception_preview'],'```','']
    (REPORT/'canonical_preview_说明与200题预览.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    frozen=ROOT/'reports/project3_perception_prototype/manifest.json'
    frozen_record=json.loads(frozen.read_text(encoding='utf-8'))
    mismatches=[path for path,digest in frozen_record['artifacts'].items() if sha(Path(path))!=digest]
    scripts_mismatches=[path for path,digest in frozen_record['scripts'].items() if sha(Path(path))!=digest]
    assert not mismatches and not scripts_mismatches
    artifacts=[p for base in [DATA,REPORT] for p in base.rglob('*') if p.is_file()]
    dump(REPORT/'manifest.json',dict(version=VERSION,inputs={str(source):sha(source),str(manual_source):sha(manual_source),str(frozen):sha(frozen)},
                                    frozen_prototype_artifact_mismatches=mismatches,frozen_prototype_script_mismatches=scripts_mismatches,
                                    artifacts={str(path):sha(path) for path in artifacts}))
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':run()
