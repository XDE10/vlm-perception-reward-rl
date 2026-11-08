"""Evidence-based joins for Geometry3K, InterGPS annotations and MathVista.

Parquet row offsets are locators ONLY, never original IDs. Join candidates are
retrieved by exact decoded RGB pixels, then checked against normalized question.
No relation here is promoted to visual-only gold supervision.
"""
import hashlib
import io
import json
import re
import unicodedata
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
import pyarrow.parquet as pq
from PIL import Image

def digest(data):
    return hashlib.sha256(data).hexdigest()

def norm(text):
    text = unicodedata.normalize('NFKC', str(text)).replace('<image>', '')
    return re.sub(r'\s+', '', text).casefold()

def question_forms(record):
    data=record['original_data']
    return {field:norm(data[field]).rstrip('.') for field in ['problem_text','compact_text','annotat_text'] if data.get(field)}

def image_hash(data):
    image = Image.open(io.BytesIO(data)).convert('RGB')
    return digest(str(image.size).encode()+b'\0'+image.tobytes())

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2),encoding='utf-8')

def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w',encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row,ensure_ascii=False)+'\n')

def original_records(root):
    archive = zipfile.ZipFile(root/'intergps/data/geometry3k/logic_forms.zip')
    diagram = json.loads(archive.read('logic_forms/diagram_logic_forms_annot.json'))
    text = json.loads(archive.read('logic_forms/text_logic_forms_annot.json'))
    dissolved = json.loads(archive.read('logic_forms/text_logic_forms_annot_dissolved.json'))
    records = []
    for split in ['train','val','test']:
        z = zipfile.ZipFile(root/f'intergps/data/geometry3k/{split}.zip')
        for name in sorted(z.namelist()):
            if not name.endswith('/data.json'):
                continue
            data = json.loads(z.read(name))
            folder = name.rsplit('/',1)[0]
            oid = str(data['id'])
            pixels = image_hash(z.read(folder+'/img_diagram.png'))
            bundled = json.loads(z.read(folder+'/logic_form.json'))
            answer_index = ord(data['answer'])-ord('A') if len(data.get('answer',''))==1 else -1
            answer = data.get('choices',[])[answer_index] if 0<=answer_index<len(data.get('choices',[])) else None
            records.append(dict(original_id=oid, split={'val':'validation'}.get(split,split),
                                question=data['problem_text'], answer=answer,
                                image_pixel_sha256=pixels, original_data=data,
                                diagram_annotation=diagram.get(oid),text_annotation=text.get(oid),
                                dissolved_annotation=dissolved.get(oid), bundled_logic_form=bundled,
                                annotation_provenance='official human-annotation package *_annot.json; not parser predictions',
                                diagram_bundle_agrees=set(bundled.get('diagram_logic_form',[]))==set(diagram.get(oid,{}).get('diagram_logic_forms',[])),
                                text_bundle_agrees=set(bundled.get('text_logic_form',[]))==set(text.get(oid,{}).get('text_logic_forms',[])),
                                original_locator=f'{split}.zip::{name}'))
    return records

def run(root, output):
    originals = original_records(root)
    by_pixels = defaultdict(list)
    for record in originals:
        by_pixels[record['image_pixel_sha256']].append(record)
    write_rows(output/'geometry3k_image_reuse_groups.jsonl',[
        dict(image_pixel_sha256=key,originals=[dict(original_id=x['original_id'],split=x['split'],question=x['question'],answer=x['answer']) for x in value],
             cross_split=len({x['split'] for x in value})>1)
        for key,value in by_pixels.items() if len(value)>1])
    joins=[]
    for split in ['train','validation','test']:
        rows=pq.read_table(root/f'geometry3k/data/{split}-00000-of-00001.parquet').to_pylist()
        for row_number,row in enumerate(rows):
            image=row['images'][0]
            pixels=image_hash(image['bytes'])
            candidates=by_pixels.get(pixels,[])
            agreeing=[x for x in candidates if norm(row['problem']).rstrip('.') in question_forms(x).values()]
            status='matched' if len(agreeing)==1 else ('ambiguous' if len(agreeing)>1 else ('question_conflict' if candidates else 'missing_image'))
            matched=agreeing[0] if len(agreeing)==1 else None
            joins.append(dict(wrapper_locator=f'{split}:{row_number}',wrapper_split=split,question=row['problem'],answer=row['answer'],
                              image_pixel_sha256=pixels,wrapper_image_path=image.get('path'),status=status,
                              candidate_original_ids=[x['original_id'] for x in candidates],
                              original_id=matched['original_id'] if matched else None,
                              matched_original_question_fields=[field for field,value in question_forms(matched).items() if value==norm(row['problem']).rstrip('.')] if matched else [],
                              split_agrees=matched['split']==split if matched else None,
                              normalized_answer_agrees=norm(matched['answer'])==norm(row['answer']) if matched else None,
                              has_diagram_annotation=bool(matched and matched['diagram_annotation']),
                              has_text_annotation=bool(matched and matched['text_annotation'])))
    write_rows(output/'intergps_annotations.jsonl', originals)
    write_rows(output/'geometry3k_intergps_links.jsonl',joins)
    # Review worklist only; no automatic declaration of visual-only facts.
    review=[]
    for split in ['train','validation','test']:
        review.extend([dict(x, manual_review_status='pending', link_correct=None,
                            diagram_relation_valid=None, visual_exclusive=None)
                       for x in joins if x['wrapper_split']==split and x['status']=='matched'][:10])
    write_rows(output/'manual_link_review_30_pending.jsonl',review)
    # Cross-source audit; all 3 original splits are indexed so train leakage and
    # domain overlap are distinguished. No benchmark answers affect training.
    by_question=defaultdict(list)
    for record in originals:
        for value in set(question_forms(record).values()):
            by_question[value].append(record)
    overlap=[]
    mathpath=next((root/'mathvista/data').glob('testmini-*.parquet'))
    for row in pq.read_table(mathpath).to_pylist():
        source=row['metadata'].get('source','')
        pixels=image_hash(row['decoded_image']['bytes'])
        images=by_pixels.get(pixels,[])
        questions=by_question.get(norm(row['question']).rstrip('.'),[])
        hits={x['original_id']:x for x in images+questions}
        question_ids={x['original_id'] for x in questions}
        joint=[x for x in images if x['original_id'] in question_ids]
        geometry_source='geometry3k' in str(source).casefold()
        overlap.append(dict(pid=row['pid'],source=source,image_pixel_sha256=pixels,
                            geometry3k_source=geometry_source,
                            image_matches=[{'original_id':x['original_id'],'split':x['split']} for x in images],
                            question_matches=[{'original_id':x['original_id'],'split':x['split']} for x in questions],
                            joint_image_question_matches=[{'original_id':x['original_id'],'split':x['split']} for x in joint],
                            exact_image_train_overlap=any(x['split']=='train' for x in images),
                            joint_image_question_train_overlap=any(x['split']=='train' for x in joint),
                            potential_text_train_overlap=any(x['split']=='train' for x in questions),
                            source_disjoint_no_exact_overlap=not geometry_source and not hits))
    write_rows(output/'mathvista_testmini_overlap.jsonl',overlap)
    write_json(output/'mathvista_source_disjoint_ids.json',[x['pid'] for x in overlap if x['source_disjoint_no_exact_overlap']])
    summary=dict(original_count=len(originals),original_splits=dict(Counter(x['split'] for x in originals)),
                 wrapper_count=len(joins),wrapper_splits=dict(Counter(x['wrapper_split'] for x in joins)),
                 link_status=dict(Counter(x['status'] for x in joins)),
                 split_conflicts=sum(x['split_agrees'] is False for x in joins),
                 normalized_answer_conflicts=sum(x['normalized_answer_agrees'] is False for x in joins),
                 original_missing_diagram_annotation=sum(not x['diagram_annotation'] for x in originals),
                 original_missing_text_annotation=sum(not x['text_annotation'] for x in originals),
                 wrapper_unlinked_or_missing_diagram_annotation=sum(not x['has_diagram_annotation'] for x in joins),
                 wrapper_unlinked_or_missing_text_annotation=sum(not x['has_text_annotation'] for x in joins),
                 original_diagram_bundle_conflicts=sum(not x['diagram_bundle_agrees'] for x in originals),
                 original_text_bundle_conflicts=sum(not x['text_bundle_agrees'] for x in originals),
                 repeated_original_pixel_groups=sum(len(v)>1 for v in by_pixels.values()),
                 cross_split_original_pixel_groups=sum(len({x['split'] for x in v})>1 for v in by_pixels.values()),
                 mathvista_count=len(overlap),mathvista_sources=dict(Counter(x['source'] for x in overlap)),
                 mathvista_geometry3k_source=sum(x['geometry3k_source'] for x in overlap),
                 mathvista_exact_image_matches=sum(bool(x['image_matches']) for x in overlap),
                 mathvista_exact_question_matches=sum(bool(x['question_matches']) for x in overlap),
                 mathvista_exact_image_train_overlap=sum(x['exact_image_train_overlap'] for x in overlap),
                 mathvista_joint_image_question_train_overlap=sum(x['joint_image_question_train_overlap'] for x in overlap),
                 mathvista_potential_text_train_overlap=sum(x['potential_text_train_overlap'] for x in overlap),
                 mathvista_source_disjoint_no_exact_overlap=sum(x['source_disjoint_no_exact_overlap'] for x in overlap),
                 limitations=['Exact decoded-pixel matching misses resized, cropped, JPEG-recompressed and relabeled images.',
                              'Normalized text match may flag generic repeated questions; inspect evidence, not automatic semantic identity.',
                              'Source-disjoint IDs are a custom subset, not the official 1000-question score and not guaranteed OOD.',
                              'No human image/link audit or visual-exclusive label certification has been performed.',
                              'Answer string conflicts require mathematical equivalence audit; they are not confirmed label errors.'])
    write_json(output/'summary.json',summary)
    return summary
