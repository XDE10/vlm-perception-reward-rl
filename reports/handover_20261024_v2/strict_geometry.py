"""Independent strict schema v5. Frozen perception_v4 remains unchanged."""
import ast
import re
from src.data.perception_v4 import scoped_score
from src.data.project3_perception_v2 import expression, ORDER

VERSION = 'geometry-strict-v5-20261024'


def validate_fact(token):
    lhs, sep, rhs = token.strip().partition('=')
    tree = ast.parse(lhs.strip(), mode='eval')
    if len(list(ast.walk(tree))) > 100 or len(token) > 600:
        raise ValueError('fact_budget')
    n = tree.body
    if not isinstance(n, ast.Call) or not isinstance(n.func, ast.Name) or n.keywords or n.func.id not in ORDER:
        raise ValueError('relation')
    rel, args = n.func.id, n.args

    def point(x):
        if not isinstance(x, ast.Name) or not re.fullmatch('[A-Z][0-9]*', x.id):
            raise ValueError('point')
        return x.id

    def points(xs, count):
        if len(xs) != count or len(set(point(x) for x in xs)) != count:
            raise ValueError('arity_or_degenerate_points')

    def segment(x):
        if not isinstance(x, ast.Tuple):
            raise ValueError('segment_tuple')
        points(x.elts, 2)
        return tuple(sorted(point(y) for y in x.elts))

    def angle(x):
        if not isinstance(x, ast.Tuple):
            raise ValueError('angle_tuple')
        points(x.elts, 3)

    def circle(x):
        if isinstance(x, ast.Name) and re.fullmatch(r'Circle(?:[1-9][0-9]*)?', x.id):
            return
        if isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == 'Circle' and not x.keywords and len(x.args) == 1:
            point(x.args[0]); return
        raise ValueError('circle')

    if rel in {'Length', 'Angle'}:
        points(args, 2 if rel == 'Length' else 3)
    elif rel in {'Parallel', 'Perpendicular', 'CongruentLength'}:
        if len(args) != 2 or segment(args[0]) == segment(args[1]):
            raise ValueError('line_pair')
    elif rel == 'CongruentAngle':
        if len(args) != 2: raise ValueError('angle_pair')
        for x in args: angle(x)
    elif rel in {'PointLiesOnLine', 'PointLiesOnCircle'}:
        if len(args) != 2: raise ValueError('incidence_arity')
        point(args[0]); (segment if rel == 'PointLiesOnLine' else circle)(args[1])
    elif rel == 'Tangent':
        if len(args) != 2: raise ValueError('tangent_arity')
        segment(args[0]); circle(args[1])
    elif rel in {'ArcLength', 'ArcMeasure', 'Area'}:
        if len(args) != 1 or not isinstance(args[0], ast.Call) or args[0].keywords or not isinstance(args[0].func, ast.Name):
            raise ValueError('shape_arity')
        shape = args[0]
        if rel == 'Area':
            sizes = {'Triangle': 3, 'Quadrilateral': 4, 'Polygon': len(shape.args)}
            if shape.func.id not in sizes or len(shape.args) < 3: raise ValueError('polygon')
            points(shape.args, sizes[shape.func.id])
        else:
            if shape.func.id not in {'minorArc', 'majorArc', 'unspecifiedArc'} or len(shape.args) not in {2, 3}: raise ValueError('arc')
            points(shape.args, len(shape.args))
    quantitative = rel in {'Length', 'Angle', 'ArcLength', 'ArcMeasure', 'Area'}
    if quantitative != bool(sep): raise ValueError('value_presence')
    if quantitative:
        raw = rhs.strip(); degrees = raw.endswith(' deg')
        if degrees: raw = raw[:-4]
        if degrees != (rel in {'Angle', 'ArcMeasure'}): raise ValueError('unit')
        _, constant, value = expression(raw)
        if value.is_nonpositive is True: raise ValueError('nonpositive_measure')
        # Source schema admits reflex angles; do not silently redefine those labels.
        if constant and rel in {'Angle', 'ArcMeasure'} and value > 360:
            raise ValueError('angle_range')
    return rel


def validate_completion(text):
    matches = re.findall(r'<perception>(.*?)</perception>', text, re.S)
    if len(matches) != 1 or text.count('<perception>') != 1 or text.count('</perception>') != 1:
        return {'valid': False, 'errors': ['perception_sections'], 'fact_count': 0}
    chunks = [x.strip() for x in matches[0].split(';') if x.strip()]
    errors = []
    if len(chunks) > 128: errors.append('fact_count_budget')
    for i, chunk in enumerate(chunks):
        try: validate_fact(chunk)
        except (ValueError, SyntaxError, TypeError) as e: errors.append(f'{i}:{e}')
    return {'valid': not errors, 'errors': errors, 'fact_count': len(chunks)}


def parallel_scores(text, positive, negative):
    legacy = scoped_score(text, positive, negative)
    check = validate_completion(text)
    strict = dict(legacy, format_valid=check['valid'], mask=bool(positive), schema_version=VERSION)
    if not check['valid'] or not positive:
        strict.update(reward=0., precision=0., recall=0., f1=0.,true_positive=0,certified_false_positive=0,masked_predictions=0,
                      prediction_scoring_status='invalid_geometry_schema' if not check['valid'] else 'no_trusted_gold')
    return {'frozen_v4': dict(legacy, mask=bool(positive)), 'strict_v5': strict, 'strict_validation': check}
