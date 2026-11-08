"""Independent finite InterGPS AST/fact prototype; never certifies visual gold.

No modifications to the production perception/reward parser. Values remain exact
rationals; angle vertex and tangent line/circle roles are preserved.
"""
from fractions import Fraction
import json
import re

VERSION='intergps-perception-prototype-v1'
ENTITY=re.compile(r'[A-Z][0-9]*\Z')

def parse_ast(raw):
    raw=raw.strip()
    if not raw:
        raise ValueError('empty_expression')
    depth=0
    for char in raw:
        depth += (char=='(')-(char==')')
        if depth<0: raise ValueError('unbalanced_parenthesis')
    if depth: raise ValueError('unbalanced_parenthesis')
    match=re.match(r'^([A-Za-z_][A-Za-z_0-9]*)\(',raw)
    if not match or not raw.endswith(')'):
        return {'atom':raw}
    name=match[1]
    content=raw[match.end():-1]
    depth=0; start=0; parts=[]
    for index,char in enumerate(content):
        if char=='(': depth+=1
        if char==')': depth-=1
        if depth<0:
            # E.g. x(a)+b(c): symbolic expression, not a single call.
            return {'atom':raw}
        if char==',' and depth==0:
            parts.append(content[start:index]);start=index+1
    parts.append(content[start:])
    if any(not x.strip() for x in parts): raise ValueError('empty_argument')
    return {'op':name,'args':[parse_ast(x) for x in parts]}

def point(node):
    value=node.get('atom','')
    if not ENTITY.fullmatch(value): raise ValueError('unresolved_or_invalid_point')
    return value

def call(node,name,arity):
    if node.get('op')!=name or len(node.get('args',[]))!=arity:
        raise ValueError('unsupported_'+name+'_shape')
    return node['args']

def line(node):
    result=tuple(sorted(map(point,call(node,'Line',2))))
    if result[0]==result[1]: raise ValueError('degenerate_line')
    return result

def angle(node):
    a,b,c=map(point,call(node,'Angle',3))
    if len({a,b,c})!=3: raise ValueError('degenerate_angle')
    ends=sorted((a,c))
    return ends[0],b,ends[1]

def fact(relation,entities,value='',unit=''):
    return dict(relation=relation,entities=entities,value=value,unit=unit)

def canonical_fact(ast):
    op=ast.get('op','')
    if op in {'Parallel','Perpendicular'}:
        args=call(ast,op,2)
        lines=sorted([line(x) for x in args])
        if lines[0]==lines[1]: raise ValueError('identical_line_pair')
        return fact(op,lines)
    if op=='Tangent':
        a,b=call(ast,op,2)
        if a.get('op')=='Circle':a,b=b,a
        segment=line(a)
        center=point(call(b,'Circle',1)[0])
        return fact(op,[segment,center])
    if op=='Equals':
        left,right=call(ast,'Equals',2)
        if right.get('op') in {'LengthOf','MeasureOf'}: left,right=right,left
        try:
            number=Fraction(right['atom'].replace(' ',''))
        except (KeyError,ValueError,ZeroDivisionError):
            raise ValueError('symbolic_or_nonrational_value')
        if left.get('op')=='LengthOf':
            entities=line(call(left,'LengthOf',1)[0])
            if number<=0: raise ValueError('nonpositive_length')
            return fact('Length',entities,str(number),'unspecified_source_unit')
        if left.get('op')=='MeasureOf':
            entities=angle(call(left,'MeasureOf',1)[0])
            if not 0<number<=360: raise ValueError('angle_out_of_range')
            return fact('Angle',entities,str(number),'deg')
        raise ValueError('unsupported_Equality_target')
    raise ValueError('unsupported_root_'+op)

def key(value,include_value=True):
    fields=['relation','entities']+(['value','unit'] if include_value else [])
    return json.dumps({field:value[field] for field in fields},sort_keys=True,separators=(',',':'))

def parse_record(raw):
    try:
        ast=parse_ast(raw)
    except ValueError as error:
        return dict(raw=raw,ast=None,fact=None,parse_status='syntax_error',reason=str(error))
    try:
        result=canonical_fact(ast)
    except ValueError as error:
        return dict(raw=raw,ast=ast,fact=None,parse_status='unsupported',reason=str(error))
    # Roundtrip JSON removes tuples for stable persisted comparison.
    return dict(raw=raw,ast=ast,fact=json.loads(json.dumps(result)),parse_status='supported',reason='finite_schema_v1')

def finite_entailments(text_records):
    derived={}
    for record in text_records:
        value=record['fact']
        if not value: continue
        inferred=None
        if value['relation']=='Perpendicular':
            first,second=value['entities'];shared=set(first)&set(second)
            if len(shared)==1:
                vertex=next(iter(shared));outer=sorted((next(x for x in first if x!=vertex),next(x for x in second if x!=vertex)))
                inferred=fact('Angle',[outer[0],vertex,outer[1]],'90','deg')
                rule='text_perpendicular_shared_endpoint_implies_90deg'
        elif value['relation']=='Angle' and value['value']=='90' and value['unit']=='deg':
            a,b,c=value['entities']
            inferred=fact('Perpendicular',sorted([sorted((a,b)),sorted((b,c))]))
            rule='text_90deg_implies_perpendicular_incident_lines'
        if inferred:
            derived[key(inferred)]={'fact':inferred,'rule':rule,'premise_raw':[record['raw']]}
    return derived

def conflict_keys(records):
    slots={};line_relations={};conflicts=set()
    for record in records:
        value=record['fact']
        if not value: continue
        slot=key(value,False)
        slots.setdefault(slot,set()).add(key(value))
        if value['relation'] in {'Parallel','Perpendicular'}:
            line_relations.setdefault(json.dumps(value['entities']),[]).append(value)
    conflicts.update(slot for slot,values in slots.items() if len(values)>1)
    for values in line_relations.values():
        if len({x['relation'] for x in values})>1:
            conflicts.update(key(x,False) for x in values)
    return conflicts

def classify(diagram,text):
    explicit={key(x['fact']):x for x in text if x['fact']}
    derived=finite_entailments(text)
    conflicts=conflict_keys(diagram+text+[
        dict(fact=x['fact']) for x in derived.values()])
    results=[]
    for record in diagram:
        value=record['fact'];result=dict(record)
        result.update(human_review='pending',visual_trust_signed=False,training_approved=False)
        if not value:
            result.update(category='uncertain',classification_reason='outside_finite_schema_or_invalid_source')
        elif key(value,False) in conflicts:
            result.update(category='uncertain',classification_reason='conflicting_formal_source_or_finite_consequence')
        elif key(value) in explicit:
            result.update(category='text_explicit',classification_reason='same_normalized_fact_in_official_text_annotation',text_evidence=[explicit[key(value)]['raw']])
        elif key(value) in derived:
            result.update(category='text_entailed',classification_reason=derived[key(value)]['rule'],text_evidence=derived[key(value)]['premise_raw'])
        else:
            result.update(category='visual_candidate',classification_reason='not_found_by_limited_formal_text_checks; requires_prose_entailment_and_image_review')
        results.append(result)
    return results
