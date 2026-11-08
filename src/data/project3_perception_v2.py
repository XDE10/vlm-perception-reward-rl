"""Review-only InterGPS v2. Safe symbolic AST; source records never become gold."""
import ast
import json
import re
import sympy as sp
from src.data.project3_perception_prototype import parse_ast, point, line, angle, call, fact, key, finite_entailments

VERSION = 'intergps-perception-v2-20261024'
ORDER = ['Angle','ArcMeasure','ArcLength','Area','CongruentAngle','CongruentLength',
         'Length','Parallel','Perpendicular','PointLiesOnCircle','PointLiesOnLine','Tangent']


def expression(raw):
    if not isinstance(raw,str) or len(raw)>160: raise ValueError('expression_length')
    s=raw.strip().replace('^','**').replace(r'\pi','pi')
    for _ in range(4):
        s=re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}',r'((\1)/(\2))',s)
        s=re.sub(r'\\sqrt\{([^{}]+)\}',r'sqrt(\1)',s)
    s=re.sub(r'(?<=\d)(?=[A-Za-z(])|(?<=\))(?=[A-Za-z(])','*',s)
    if not re.fullmatch(r'[A-Za-z0-9_+*/(). \-]+',s):raise ValueError('expression_outside_whitelist')
    tree=ast.parse(s,mode='eval')
    if len(list(ast.walk(tree)))>70:raise ValueError('expression_complexity')
    def build(n):
        if isinstance(n,ast.Constant) and type(n.value) in (int,float):
            if abs(n.value)>10**12:raise ValueError('constant_bound')
            return sp.Rational(str(n.value))
        if isinstance(n,ast.Name) and re.fullmatch('[a-z][a-z0-9_]{0,15}',n.id):
            if n.id in {'nan','inf','infinity','oo','zoo'}:raise ValueError('reserved_nonfinite_name')
            return sp.pi if n.id=='pi' else sp.Symbol(n.id,real=True)
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.UAdd,ast.USub)):
            v=build(n.operand);return -v if isinstance(n.op,ast.USub) else v
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='sqrt' and len(n.args)==1 and not n.keywords:
            return sp.sqrt(build(n.args[0]))
        if isinstance(n,ast.BinOp):
            a,b=build(n.left),build(n.right)
            if isinstance(n.op,ast.Add):return a+b
            if isinstance(n.op,ast.Sub):return a-b
            if isinstance(n.op,ast.Mult):return a*b
            if isinstance(n.op,ast.Div) and b!=0:return a/b
            if isinstance(n.op,ast.Pow) and b.is_Integer and abs(b)<=8:return a**b
        raise ValueError('expression_ast_rejected')
    v=build(tree.body)
    if v.has(sp.zoo,sp.oo,-sp.oo,sp.nan) or v.is_real is False:raise ValueError('nonfinite_or_nonreal')
    return sp.sstr(v),not bool(v.free_symbols),v


def circle(n):
    args=n.get('args',[])
    if n.get('op')!='Circle' or len(args) not in (1,2):raise ValueError('unsupported_circle_identity')
    center=point(args[0]);radius=args[1].get('atom') if len(args)==2 else None
    if radius is not None and not re.fullmatch('[A-Za-z0-9_]+',radius):raise ValueError('unresolved_radius_identity')
    return {'center':center,'source_radius_id':radius}


def arc(n):
    qualifier='unspecified'
    if n.get('op') in ('Minor','Major'):
        qualifier=n['op'].lower();n=call(n,n['op'],1)[0]
    if n.get('op')!='Arc' or len(n.get('args',[])) not in (2,3):raise ValueError('unsupported_arc')
    # Keep source traversal/order. Two endpoints alone do not disambiguate major/minor.
    return {'points':[point(x) for x in n['args']], 'kind':qualifier}


def quantity(n):
    op=n.get('op')
    if op=='LengthOf':
        inner=call(n,op,1)[0]
        if inner.get('op')=='Line':return 'Length',list(line(inner)),'unspecified_source_unit'
        return 'ArcLength',arc(inner),'unspecified_source_unit'
    if op=='MeasureOf':
        inner=call(n,op,1)[0]
        if inner.get('op')=='Angle':return 'Angle',list(angle(inner)),'deg'
        if inner.get('atom'):raise ValueError('unresolved_measure_label_requires_source_alias_mapping')
        return 'ArcMeasure',arc(inner),'deg'
    if op=='AreaOf':
        shape=call(n,op,1)[0];name=shape.get('op');args=shape.get('args',[])
        sizes={'Triangle':3,'Quadrilateral':4,'Pentagon':5,'Hexagon':6,'Polygon':None}
        if name not in sizes or len(args)<3 or (sizes[name] and len(args)!=sizes[name]):raise ValueError('unsupported_area_shape')
        pts=[point(x) for x in args]
        if len(set(pts))!=len(pts):raise ValueError('degenerate_polygon')
        return 'Area',{'shape':name,'boundary':pts},'unspecified_source_unit_squared'
    raise ValueError('unsupported_quantity')


def canonical(n):
    op=n.get('op')
    if op in ('Parallel','Perpendicular'):
        a,b=map(line,call(n,op,2))
        if a==b:raise ValueError('identical_line_pair')
        return fact(op,sorted([a,b]))
    if op=='Tangent':
        a,b=call(n,op,2)
        if a.get('op')=='Circle':a,b=b,a
        return fact(op,[list(line(a)),circle(b)])
    if op=='PointLiesOnLine':
        p,l=call(n,op,2);return fact(op,[point(p),list(line(l))])
    if op=='PointLiesOnCircle':
        p,c=call(n,op,2);return fact(op,[point(p),circle(c)])
    if op=='Equals':
        left,right=call(n,op,2)
        if left.get('op') not in ('LengthOf','MeasureOf','AreaOf'):left,right=right,left
        rel,entities,unit=quantity(left)
        if right.get('op') in ('LengthOf','MeasureOf','AreaOf'):
            rel2,entities2,unit2=quantity(right)
            if rel!=rel2 or rel not in ('Length','Angle'):raise ValueError('unsupported_equality_pair')
            pair=sorted([entities,entities2],key=lambda x:json.dumps(x))
            return fact('Congruent'+rel,pair)
        value,constant,v=expression(right.get('atom',''))
        if constant and v.is_nonpositive:raise ValueError('nonpositive_measure')
        if constant and rel in ('Angle','ArcMeasure') and v>360:raise ValueError('angle_out_of_range')
        f=fact(rel,entities,value,unit);f['value_kind']='constant' if constant else 'symbolic_expression'
        return f
    raise ValueError('unsupported_root_'+str(op))


def parse_record(raw):
    try:
        tree=parse_ast(raw);value=canonical(tree)
        return dict(raw=raw,ast=tree,fact=json.loads(json.dumps(value)),parse_status='supported',reason=VERSION)
    except (ValueError,SyntaxError,TypeError,KeyError,ZeroDivisionError) as e:
        return dict(raw=raw,ast=locals().get('tree'),fact=None,parse_status='unsupported',reason=str(e))


def classify(diagram,text):
    explicit={key(x['fact']) for x in text if x['fact']}
    derived=finite_entailments(text)
    # Different symbolic annotations are equations to solve, not contradictions.
    slots={}
    inferred=[{'fact':r['fact']} for r in derived.values()]
    pair_relations={}
    for r in diagram+text+inferred:
        f=r['fact']
        if f and f.get('value_kind')=='constant':slots.setdefault(key(f,False),set()).add(f['value'])
        elif f and f['relation']=='Angle' and f['value']=='90':slots.setdefault(key(f,False),set()).add('90')
        if f and f['relation'] in {'Parallel','Perpendicular'}:pair_relations.setdefault(json.dumps(f['entities']),set()).add(f['relation'])
    conflict={k for k,v in slots.items() if len(v)>1}
    result=[]
    for r in diagram:
        f=r['fact'];cat='uncertain';reason='unsupported_or_unresolved'
        if f:
            if key(f,False) in conflict or (f['relation'] in {'Parallel','Perpendicular'} and len(pair_relations.get(json.dumps(f['entities']),set()))>1):reason='incompatible_constant_or_line_source_annotations'
            elif key(f) in explicit:cat='text_explicit';reason='formal_text_exact_match'
            elif key(f) in derived:cat='text_entailed';reason=derived[key(f)]['rule']
            elif f['relation']=='PointLiesOnLine' and f['entities'][0] in f['entities'][1]:cat='text_entailed';reason='line_endpoint_incidence_is_definitional'
            else:cat='visual_candidate';reason='limited_text_comparison_only; prose_and_image_review_pending'
        result.append({**r,'category':cat,'classification_reason':reason,'human_review':'pending','training_approved':False})
    return result


def ordered_facts(records):
    values={key(r['fact']):r['fact'] for r in records if r['category']=='visual_candidate'}
    return sorted(values.values(),key=lambda f:(ORDER.index(f['relation']),json.dumps(f['entities'],sort_keys=True),f['value'],f['unit']))
