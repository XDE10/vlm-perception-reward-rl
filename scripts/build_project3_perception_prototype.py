"""Build a frozen, train-only 200-case perception prototype and pending reviewpack."""
import hashlib
import io
import json
import platform
import shutil
import sys
import zipfile
from collections import Counter
from pathlib import Path
from PIL import Image
from src.data.project3_perception_prototype import VERSION, classify, parse_record

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/project3_perception_prototype'
REPORT=ROOT/'reports/project3_perception_prototype'
SEED='project3-train-perception-200-v1-20261023'

def rows(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]

def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

def jsonl(path,values):
    path.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in values),encoding='utf-8')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def points_in(value):
    if isinstance(value,str):yield value
    elif isinstance(value,(tuple,list)):
        for x in value:yield from points_in(x)

def section(case,include_image):
    lines=[f"## 原始 ID {case['original_id']}（train）",'',
           f"题面：{case['question']}",'',f"参考答案：`{case['answer']}`",'',
           f"原图：[打开]({case['image_path']})",'']
    if include_image:lines.extend([f"![ID {case['original_id']} 原图]({case['image_path']})",''])
    lines.extend(['原始 diagram logic forms：','','```text',*case['diagram_raw'],'```','',
                  '原始 text logic forms：','','```text',*case['text_raw'],'```','',
                  '有限 schema 结果：',''])
    for value in case['diagram_facts']:
        lines.append(f"- `{value['raw']}` → `{value['category']}`；规范事实 `{json.dumps(value['fact'],ensure_ascii=False)}`；{value['classification_reason']}")
    lines.extend(['','人工检查：**pending**。链接正确性、图像支持、题干蕴含、坐标适用性、视觉独占性均未签字；训练准入 false。',''])
    return lines

def run():
    if DATA.exists() or REPORT.exists():
        raise FileExistsError('Prototype output already exists; choose a new versioned directory rather than overwrite historical artifacts')
    DATA.mkdir(parents=True);REPORT.mkdir(parents=True);(DATA/'images').mkdir()
    links_path=ROOT/'data/project3_audit/geometry3k_intergps_links.jsonl'
    annotations_path=ROOT/'data/project3_audit/intergps_annotations.jsonl'
    eligible=[x for x in rows(links_path) if x['wrapper_split']=='train' and x['status']=='matched']
    # Source original ID drives sampling; parquet row position never selects ID.
    eligible.sort(key=lambda x:hashlib.sha256((SEED+'|'+x['original_id']).encode()).hexdigest())
    selected=eligible[:200]
    annotations={x['original_id']:x for x in rows(annotations_path)}
    archive=zipfile.ZipFile(ROOT/'data/project3_sources/intergps/data/geometry3k/train.zip')
    cases=[]
    for link in selected:
        source=annotations[link['original_id']]
        assert source['split']=='train'
        oid=source['original_id']
        image=archive.read(f'train/{oid}/img_diagram.png')
        path=DATA/f'images/{oid}.png';path.write_bytes(image)
        width,height=Image.open(io.BytesIO(image)).size
        diagram_raw=source['diagram_annotation'].get('diagram_logic_forms',[])
        text_raw=source['text_annotation'].get('text_logic_forms',[])
        diagram=[parse_record(x) for x in diagram_raw]
        text=[parse_record(x) for x in text_raw]
        facts=classify(diagram,text)
        positions=source['diagram_annotation'].get('point_positions',{})
        for index,value in enumerate(facts):
            required=list(dict.fromkeys(points_in(value['fact']['entities']))) if value['fact'] else []
            coordinates={point:positions[point] for point in required if point in positions}
            inbounds={point:len(position)==2 and 0<=position[0]<width and 0<=position[1]<height for point,position in coordinates.items()}
            value.update(fact_id=f'{oid}:diagram:{index}',image_evidence=dict(
                image_path=str(path),image_sha256=sha(path),width=width,height=height,
                source_coordinate_field='diagram_logic_forms_annot.json.point_positions',
                point_coordinates=coordinates,coordinate_in_bounds=inbounds,
                missing_point_coordinates=[point for point in required if point not in positions],
                evidence_status='pending_image_and_coordinate_review',
                warning='Source point coordinates do not prove a drawn right-angle/parallel/tangent symbol; bbox/semantic image audit is pending'))
        cases.append(dict(original_id=oid,split='train',wrapper_locator=link['wrapper_locator'],
                          question=link['question'],original_question=source['question'],answer=link['answer'],
                          image_path=str(path),image_sha256=sha(path),source_locator=source['original_locator'],
                          source_point_positions=positions,diagram_raw=diagram_raw,text_raw=text_raw,
                          diagram_facts=facts,text_parsed=text,human_review='pending',
                          visual_trust_signed=False,training_approved=False))
    jsonl(DATA/'prototype_200.jsonl',cases)
    selected_ids=[x['original_id'] for x in cases]
    dump(DATA/'selected_train_ids.json',selected_ids)
    # A separate deterministic review draw; still training data, never benchmark.
    manual=sorted(cases,key=lambda x:hashlib.sha256(('manual30|'+SEED+'|'+x['original_id']).encode()).hexdigest())[:30]
    review=[dict(original_id=x['original_id'],split='train',question=x['question'],answer=x['answer'],
                 diagram_raw=x['diagram_raw'],text_raw=x['text_raw'],image_path=x['image_path'],
                 source_point_positions=x['source_point_positions'],human_review='pending',
                 checks={'link_correct':None,'coordinates_aligned':None,'image_supports_relation':None,
                         'not_text_explicit_or_entailed':None,'visual_exclusive':None},reviewer=None,
                 visual_trust_signed=False,training_approved=False) for x in manual]
    jsonl(DATA/'manual_image_review_30_pending.jsonl',review)
    diagram_all=[v for x in cases for v in x['diagram_facts']]
    text_all=[v for x in cases for v in x['text_parsed']]
    visual_cases=sum(any(v['category']=='visual_candidate' for v in x['diagram_facts']) for x in cases)
    summary=dict(schema_version=VERSION,seed=SEED,eligible_unique_train_count=len(eligible),selected_count=len(cases),
                 selected_splits=dict(Counter(x['split'] for x in cases)),
                 cases_with_visual_candidate=visual_cases,cases_with_visual_candidate_fraction=visual_cases/len(cases),
                 diagram_count=len(diagram_all),diagram_parse_status=dict(Counter(x['parse_status'] for x in diagram_all)),
                 diagram_unsupported_reasons=dict(Counter(x['reason'] for x in diagram_all if x['parse_status']!='supported')),
                 text_count=len(text_all),text_parse_status=dict(Counter(x['parse_status'] for x in text_all)),
                 text_unsupported_reasons=dict(Counter(x['reason'] for x in text_all if x['parse_status']!='supported')),
                 categories=dict(Counter(x['category'] for x in diagram_all)),
                 supported_relations=dict(Counter(x['fact']['relation'] for x in diagram_all if x['fact'])),
                 conflicting_diagram_fact_count=sum(x['classification_reason']=='conflicting_formal_source_or_finite_consequence' for x in diagram_all),
                 visual_candidates_missing_coordinates=sum(x['category']=='visual_candidate' and bool(x['image_evidence']['missing_point_coordinates']) for x in diagram_all),
                 visual_candidates_out_of_bounds_coordinates=sum(x['category']=='visual_candidate' and not all(x['image_evidence']['coordinate_in_bounds'].values()) for x in diagram_all),
                 human_reviewed_count=0,human_precision=None,training_approved_count=0,
                 limitations=['visual_candidate means limited formal text checks found no entailment; it is not visual-exclusive ground truth.',
                              'Official text logic forms may omit prose facts or entailments; prose-level semantic review remains pending.',
                              'Only rational numeric Angle/Length and direct Parallel/Perpendicular/Tangent are supported; symbolic values, Congruent and other roots remain uncertain.',
                              'Source coordinates are evidence locators, not certified symbol bounding boxes; out-of-bounds positions are flagged.',
                              'No human or AI image adjudication is claimed by this build; all 30 review entries remain pending.'])
    dump(REPORT/'summary.json',summary)
    dump(DATA/'schema.json',dict(version=VERSION,relations=['Angle','Length','Parallel','Perpendicular','Tangent'],
                               angle_entities='[outer1,vertex,outer2]; only outer points sorted',
                               line_entities='endpoint pair sorted; line pair sorted for symmetric relations',
                               tangent_entities='[line_endpoint_pair,circle_center]; roles never sorted together',
                               units={'Angle':'deg by InterGPS convention','Length':'unspecified_source_unit'},
                               entailment_rules=['Perpendicular incident lines sharing one explicit endpoint => Angle=90deg',
                                                 'Angle=90deg => incident lines Perpendicular'],
                               unsupported='Congruent, symbolic values, unresolved entities, nonfinite schema roots',
                               production_reward_parser_modified=False))
    header=['# 项目三 200 题训练集感知事实原型','',
            '仅从唯一关联的 train 采样。所有自动输出均未签字，training_approved=false。visual_candidate 不是 image-only 金标。','',
            f'固定采样 namespace：`{SEED}`；按 SHA256(namespace|original_id) 升序取前 200。','']
    (REPORT/'prototype_200.md').write_text('\n'.join(header+[line for case in cases for line in section(case,False)]),encoding='utf-8')
    (REPORT/'manual_image_review_30_pending.md').write_text('\n'.join(
        ['# 30 题原图核查工作单（全部 pending）','',
         '本工作单包含真实源图，但尚未开展人工或 AI 看图复核。请逐项填写 JSONL，不以模型自动标签替代签字。','']+
        [line for case in manual for line in section(case,True)]),encoding='utf-8')
    overview=['# 项目三感知事实原型执行报告','',
              '本轮仅 CPU 数据原型，无 API、无训练、无人工或 AI 图像签字。现行奖励 parser 未修改。','',
              '[200 题完整可读原型](prototype_200.md)；[30 题带原图待审工作单](manual_image_review_30_pending.md)。','',
              'text_explicit 仅表示与官方 text logic form 的规范事实一致；text_entailed 仅使用 schema 中列出的有限可证规则。未发现文本匹配的有限事实仅列 visual_candidate，仍需题干语义蕴含和原图证据审核。','']
    overview += ['- `'+k+'`: '+json.dumps(v,ensure_ascii=False) for k,v in summary.items() if k!='limitations']
    overview += ['',*['- '+x for x in summary['limitations']],'',
                 '复现环境：Python 3.11.4，Pillow 11.2.1；依赖见 requirements-project3-cpu.txt。',
                 '实际入口：`& D:\\Python\\Python311\\python.exe -m scripts.build_project3_perception_prototype`。输出存在时拒绝覆盖；新版本需要另设目录与 namespace。']
    (REPORT/'执行报告.md').write_text('\n'.join(overview)+'\n',encoding='utf-8')
    files=[x for base in [DATA,REPORT] for x in base.rglob('*') if x.is_file()]
    dump(REPORT/'manifest.json',dict(schema_version=VERSION,environment={'python':sys.version,'executable':sys.executable,'platform':platform.platform()},
                                    inputs={str(links_path):sha(links_path),str(annotations_path):sha(annotations_path)},
                                    artifacts={str(x):sha(x) for x in files},
                                    scripts={str(ROOT/x):sha(ROOT/x) for x in ['src/data/project3_perception_prototype.py','scripts/build_project3_perception_prototype.py']}))
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':run()
