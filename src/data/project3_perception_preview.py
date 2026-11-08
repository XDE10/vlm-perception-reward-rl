"""Review-only canonical serializer, independent of production reward parser."""
from fractions import Fraction
import json
import re

VERSION='project3-review-canonical-preview-v1'
ORDER={name:index for index,name in enumerate(['Angle','Length','Parallel','Perpendicular','Tangent'])}
POINT=re.compile(r'[A-Z][0-9]*\Z')

def entity(value):
    if not isinstance(value,str) or not POINT.fullmatch(value):raise ValueError('invalid_point')
    return value

def segment(value):
    if len(value)!=2:raise ValueError('line_requires_two_endpoints')
    result=sorted(map(entity,value))
    if result[0]==result[1]:raise ValueError('degenerate_line')
    return result

def normalize(value):
    relation=value['relation']
    if relation not in ORDER:raise ValueError('outside_finite_schema')
    points=value['entities'];number='';unit=''
    if relation=='Angle':
        if len(points)!=3:raise ValueError('angle_requires_three_points')
        a,b,c=map(entity,points)
        if len({a,b,c})!=3:raise ValueError('degenerate_angle')
        a,c=sorted((a,c));points=[a,b,c]
        unit=value['unit']
        if unit!='deg':raise ValueError('unsupported_angle_unit')
        numeric=Fraction(value['value'])
        if not 0<numeric<=360:raise ValueError('angle_out_of_range')
        number=str(numeric)
    elif relation=='Length':
        points=segment(points);unit=value['unit']
        if unit!='unspecified_source_unit':raise ValueError('unsupported_length_unit')
        numeric=Fraction(value['value'])
        if numeric<=0:raise ValueError('nonpositive_length')
        number=str(numeric)
    elif relation in {'Parallel','Perpendicular'}:
        if len(points)!=2:raise ValueError('requires_two_lines')
        points=sorted(map(segment,points))
        if points[0]==points[1]:raise ValueError('identical_line_pair')
    else:
        if len(points)!=2:raise ValueError('tangent_requires_line_and_center')
        points=[segment(points[0]),entity(points[1])]
    return dict(relation=relation,entities=points,value=number,unit=unit)

def token(value):
    relation=value['relation'];points=value['entities']
    if relation in {'Angle','Length'}:
        args=','.join(points)
    elif relation in {'Parallel','Perpendicular'}:
        args=','.join(''.join(line) for line in points)
    else:
        args=''.join(points[0])+','+points[1]
    return relation+'('+args+')'+('='+value['value']+('deg' if relation=='Angle' else '') if value['value'] else '')

def identity(value,with_value=True):
    result={key:value[key] for key in ['relation','entities']+(['value','unit'] if with_value else [])}
    return json.dumps(result,sort_keys=True,separators=(',',':'))

def sort_key(value):
    # Entity lexical order is separate from exact numerical canonicalization.
    points=value['entities']
    if value['relation'] in {'Parallel','Perpendicular'}:points=tuple(tuple(x) for x in points)
    elif value['relation']=='Tangent':points=(tuple(points[0]),points[1])
    else:points=tuple(points)
    return ORDER[value['relation']],points,value['value'],value['unit']

def preview(records):
    accepted=[];quarantine=[];slots={};line_relations={}
    for record in records:
        if record.get('category')!='visual_candidate':continue
        try:value=normalize(record['fact'])
        except (KeyError,TypeError,ValueError,ZeroDivisionError) as error:
            quarantine.append(dict(fact_id=record.get('fact_id'),reason='normalization_error:'+str(error)));continue
        accepted.append((record,value))
        slots.setdefault(identity(value,False),set()).add(identity(value))
        if value['relation'] in {'Parallel','Perpendicular'}:
            line_relations.setdefault(json.dumps(value['entities']),set()).add(value['relation'])
    conflict_slots={slot for slot,values in slots.items() if len(values)>1}
    unique={}
    for record,value in accepted:
        conflict=identity(value,False) in conflict_slots
        conflict=conflict or (value['relation'] in {'Parallel','Perpendicular'} and len(line_relations[json.dumps(value['entities'])])>1)
        if conflict:
            quarantine.append(dict(fact_id=record.get('fact_id'),fact=value,reason='conflicting_numeric_value_or_parallel_perpendicular'))
            continue
        label=identity(value)
        entry=unique.setdefault(label,dict(fact=value,canonical=token(value),source_fact_ids=[],source_raw=[]))
        entry['source_fact_ids'].append(record.get('fact_id'))
        entry['source_raw'].append(record.get('raw'))
    ordered=sorted(unique.values(),key=lambda x:sort_key(x['fact']))
    return dict(schema_version=VERSION,canonical_facts=ordered,
                canonical_perception_preview='<perception>'+'; '.join(x['canonical'] for x in ordered)+'</perception>',
                quarantined=quarantine,review_only=True,human_review='pending',visual_trust_signed=False,training_approved=False)
