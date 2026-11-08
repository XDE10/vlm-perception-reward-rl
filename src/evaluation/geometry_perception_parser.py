"""Finite geometry schema, deterministic serialization, coverage-aware scoring.

No image interpretation is performed. F1 measures agreement with supplied,
audited labels only. Uncovered relation categories are not declared hallucinated.
"""
import re
from dataclasses import dataclass
from fractions import Fraction

VERSION = 'geometry-canonical-v1'
ORDER = {'Angle':0,'Length':1,'Parallel':2,'Perpendicular':3,'Tangent':4,'DirectedAngle':5}
ENTITY = r'[A-Z][0-9]*'


class GeometryError(ValueError):
    pass


@dataclass(frozen=True)
class Fact:
    relation: str
    entities: tuple[str,...]
    value: str = ''
    unit: str = ''

    @property
    def key(self): return self.relation,self.entities

    def serialize(self):
        return self.relation+'('+','.join(self.entities)+')'+('='+self.value+self.unit if self.value else '')


def _entity(text):
    if not re.fullmatch(ENTITY,text): raise GeometryError('Invalid entity')
    return text


def _segment(text):
    # Segments are unoriented; A10/A2 use ordinary Unicode lexicographic order.
    match = re.fullmatch('('+ENTITY+')('+ENTITY+')',text)
    if not match or match[1]==match[2]: raise GeometryError('Invalid segment')
    return ''.join(sorted((match[1],match[2])))


def parse_fact(text):
    match = re.fullmatch(r'([A-Za-z]+)\(([^()]*)\)(?:\s*=\s*(.*))?',text.strip())
    if not match or match[1] not in ORDER: raise GeometryError('Unknown or malformed relation')
    relation = match[1]
    entities = tuple(x.strip() for x in match[2].split(','))
    rhs = match[3]
    if relation in {'Angle','DirectedAngle'}:
        if len(entities)!=3: raise GeometryError('Angle requires three points')
        a,b,c = map(_entity,entities)
        if len({a,b,c})<3: raise GeometryError('Degenerate angle')
        if relation=='Angle': a,c = sorted((a,c))
        entities = a,b,c
    elif relation=='Length':
        if len(entities)==1:
            segment = re.fullmatch('('+ENTITY+')('+ENTITY+')',entities[0])
            if not segment: raise GeometryError('Invalid length segment')
            entities = segment[1],segment[2]
        if len(entities)!=2: raise GeometryError('Length requires two points')
        entities = tuple(sorted(map(_entity,entities)))
        if entities[0]==entities[1]: raise GeometryError('Degenerate segment')
    elif relation in {'Parallel','Perpendicular'}:
        if len(entities)!=2: raise GeometryError('Expected two segments')
        entities = tuple(sorted(map(_segment,entities)))
        if entities[0]==entities[1]: raise GeometryError('Identical line pair')
    elif relation=='Tangent':
        # Tangent(AB,O): segment AB tangent to circle with center O.
        # Roles must not be permuted. Circle radius/location is not inferred.
        if len(entities)!=2: raise GeometryError('Tangent(segment,circle_center)')
        entities = _segment(entities[0]),_entity(entities[1])
    value,unit = '',''
    if relation in {'Angle','DirectedAngle','Length'}:
        if rhs is None: raise GeometryError('Missing numeric value')
        numeric = re.fullmatch(r'([-+]?(?:\d+(?:\.\d+)?|\.\d+)(?:\s*/\s*\d+)?)\s*(deg|°|rad|mm|cm|m|km)?',rhs.strip())
        if not numeric: raise GeometryError('Unsupported numeric value or unit')
        try: number = Fraction(numeric[1].replace(' ',''))
        except (ValueError,ZeroDivisionError) as e: raise GeometryError('Invalid number') from e
        unit = numeric[2] or ('deg' if relation in {'Angle','DirectedAngle'} else '')
        unit = 'deg' if unit=='°' else unit
        if relation=='Length' and (number<=0 or unit in {'deg','rad'}): raise GeometryError('Invalid length')
        if relation in {'Angle','DirectedAngle'} and unit not in {'deg','rad'}: raise GeometryError('Invalid angle unit')
        value = str(number)
    elif rhs is not None:
        raise GeometryError('Relation cannot have a numeric value')
    return Fact(relation,entities,value,unit)


def parse_facts(text):
    facts,properties = set(),{}
    if len(text)>20000: raise GeometryError('Perception length limit')
    for item in text.strip().split(';'):
        if not item.strip(): continue
        fact = parse_fact(item)
        if fact.key in properties and properties[fact.key]!=(fact.value,fact.unit):
            raise GeometryError('Conflicting property values')
        properties[fact.key] = fact.value,fact.unit
        facts.add(fact)
    # Mutually exclusive relations on the exact same nondegenerate line pair.
    parallels = {f.entities for f in facts if f.relation=='Parallel'}
    if any(f.relation=='Perpendicular' and f.entities in parallels for f in facts):
        raise GeometryError('Conflicting line relations')
    return facts


def canonicalize(text):
    facts = parse_facts(text)
    return '; '.join(f.serialize() for f in sorted(facts,key=lambda f:(ORDER[f.relation],f.entities,f.value,f.unit)))


def parse_response(text):
    match = re.fullmatch(r'\s*<perception>(.*?)</perception>\s*<reasoning>(.*?)</reasoning>\s*<answer>(.*?)</answer>\s*',text,re.S)
    if not match: raise GeometryError('Expected exactly perception, reasoning, answer in order')
    if any(re.search(r'</?(?:perception|reasoning|answer)>',part) for part in match.groups()):
        raise GeometryError('Duplicate/nested sections')
    if not match[3].strip(): raise GeometryError('Empty answer')
    return {'facts':parse_facts(match[1]),'canonical_perception':canonicalize(match[1]),
            'reasoning':match[2].strip(),'answer':match[3].strip(),'canonicalization_version':VERSION}


def perception_f1(prediction,reference,covered_relations):
    """Only score categories declared exhaustively labeled for this problem.

    Invalid/contradictory predictions receive zero. Duplicates never increase TP.
    Empty or missing trusted reference yields mask=False and reward=0, not 1.
    """
    coverage = set(covered_relations)
    if not coverage<=ORDER.keys(): raise GeometryError('Unknown coverage category')
    gold = parse_facts(reference)
    if any(f.relation not in coverage for f in gold): raise GeometryError('Reference outside declared coverage')
    if not gold:
        return {'precision':0.,'recall':0.,'f1':0.,'mask':False,'tp':0,'fp':0,'fn':0,'status':'no_trusted_labels'}
    try: predicted = parse_facts(prediction)
    except GeometryError as e:
        return {'precision':0.,'recall':0.,'f1':0.,'mask':True,'tp':0,'fp':0,'fn':len(gold),'status':str(e)}
    scored = {f for f in predicted if f.relation in coverage}
    tp,fp,fn = len(scored&gold),len(scored-gold),len(gold-scored)
    precision = tp/(tp+fp) if tp+fp else 0.
    recall = tp/(tp+fn)
    f1 = 2*precision*recall/(precision+recall) if precision+recall else 0.
    return {'precision':precision,'recall':recall,'f1':f1,'mask':True,'tp':tp,'fp':fp,'fn':fn,
            'unscored_count':len(predicted-scored),'status':'ok'}
