"""Per-claim parsing of a ``<perception>`` block.

Every ``;``-separated chunk becomes one Claim. A chunk that fails the strict
geometry schema or the frozen v4 canonicaliser is kept as an *invalid* claim,
so one malformed fact costs one claim instead of zeroing the whole block (the
v4 behaviour). Canonical keys come from the frozen ``perception_v4.token_key``
so certified tokens and predictions are matched with unchanged semantics.

The strict schema check is ported from
``reports/handover_20261024_v2/strict_geometry.py`` (schema v5, frozen evidence
directory) with the same rules: arity, distinct points, segment/angle/circle
roles, unit presence, positive values and the reflex-angle upper bound of 360.
"""
import ast
import re
from dataclasses import dataclass

from src.data.perception_v4 import token_key
from src.data.project3_perception_v2 import ORDER, expression

SCHEMA_VERSION = "claims-v6-20261109"
_BLOCK_RE = re.compile(r"<perception>(.*?)</perception>", re.S)
QUANTITATIVE = {"Length", "Angle", "ArcLength", "ArcMeasure", "Area"}


@dataclass(frozen=True)
class Claim:
    raw: str
    key: str = None
    relation: str = None
    args: tuple = None
    value: str = ""
    unit: str = ""
    error: str = None

    @property
    def valid(self):
        return self.error is None


def _point(node):
    if not isinstance(node, ast.Name) or not re.fullmatch(r"[A-Z][0-9]*", node.id):
        raise ValueError("point")
    return node.id


def _points(nodes, count):
    if len(nodes) != count or len({_point(x) for x in nodes}) != count:
        raise ValueError("arity_or_degenerate_points")


def _segment(node):
    if not isinstance(node, ast.Tuple):
        raise ValueError("segment_tuple")
    _points(node.elts, 2)
    return tuple(sorted(_point(x) for x in node.elts))


def _angle(node):
    if not isinstance(node, ast.Tuple):
        raise ValueError("angle_tuple")
    _points(node.elts, 3)


def _circle(node):
    if isinstance(node, ast.Name) and re.fullmatch(r"Circle(?:[1-9][0-9]*)?", node.id):
        return
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Circle"
            and not node.keywords and len(node.args) == 1):
        _point(node.args[0])
        return
    raise ValueError("circle")


def validate_schema(token):
    """Raise ValueError unless the fact is well formed; return the relation name."""
    if len(token) > 600:
        raise ValueError("fact_budget")
    lhs, sep, rhs = token.strip().partition("=")
    tree = ast.parse(lhs.strip(), mode="eval")
    if len(list(ast.walk(tree))) > 100:
        raise ValueError("fact_budget")
    node = tree.body
    if (not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.keywords
            or node.func.id not in ORDER):
        raise ValueError("relation")
    relation, args = node.func.id, node.args
    if relation in {"Length", "Angle"}:
        _points(args, 2 if relation == "Length" else 3)
    elif relation in {"Parallel", "Perpendicular", "CongruentLength"}:
        if len(args) != 2 or _segment(args[0]) == _segment(args[1]):
            raise ValueError("line_pair")
    elif relation == "CongruentAngle":
        if len(args) != 2:
            raise ValueError("angle_pair")
        for arg in args:
            _angle(arg)
    elif relation in {"PointLiesOnLine", "PointLiesOnCircle"}:
        if len(args) != 2:
            raise ValueError("incidence_arity")
        _point(args[0])
        (_segment if relation == "PointLiesOnLine" else _circle)(args[1])
    elif relation == "Tangent":
        if len(args) != 2:
            raise ValueError("tangent_arity")
        _segment(args[0])
        _circle(args[1])
    elif relation in {"ArcLength", "ArcMeasure", "Area"}:
        if (len(args) != 1 or not isinstance(args[0], ast.Call) or args[0].keywords
                or not isinstance(args[0].func, ast.Name)):
            raise ValueError("shape_arity")
        shape = args[0]
        if relation == "Area":
            sizes = {"Triangle": 3, "Quadrilateral": 4, "Polygon": len(shape.args)}
            if shape.func.id not in sizes or len(shape.args) < 3:
                raise ValueError("polygon")
            _points(shape.args, sizes[shape.func.id])
        else:
            if shape.func.id not in {"minorArc", "majorArc", "unspecifiedArc"} or len(shape.args) not in {2, 3}:
                raise ValueError("arc")
            _points(shape.args, len(shape.args))
    quantitative = relation in QUANTITATIVE
    if quantitative != bool(sep):
        raise ValueError("value_presence")
    if quantitative:
        raw = rhs.strip()
        degrees = raw.endswith(" deg")
        if degrees:
            raw = raw[:-4]
        if degrees != (relation in {"Angle", "ArcMeasure"}):
            raise ValueError("unit")
        _, constant, value = expression(raw)
        if value.is_nonpositive is True:
            raise ValueError("nonpositive_measure")
        if constant and relation in {"Angle", "ArcMeasure"} and value > 360:
            raise ValueError("angle_range")
    return relation


def parse_claim(raw):
    raw = raw.strip()
    try:
        validate_schema(raw)
        key = token_key(raw)
        relation, args, value, unit = ast.literal_eval(key)
    except (ValueError, SyntaxError, TypeError, RecursionError, MemoryError) as exc:
        return Claim(raw=raw, error=type(exc).__name__ + ":" + str(exc)[:80])
    return Claim(raw=raw, key=key, relation=relation, args=_freeze(args), value=value, unit=unit)


def _freeze(value):
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(x) for x in value)
    return value


def extract_block(text):
    """Return (block_text, status). status is 'ok', 'missing' or 'multiple'."""
    matches = _BLOCK_RE.findall(text)
    if not matches:
        return None, "missing"
    if len(matches) > 1 or text.count("<perception>") != 1 or text.count("</perception>") != 1:
        return None, "multiple"
    return matches[0], "ok"


def parse_block(block, max_claims=24):
    """Split a perception block into de-duplicated claims.

    Returns (claims, info). ``info['chunks']`` counts raw chunks before
    de-duplication; ``info['over_cap']`` is True when chunks exceed max_claims.
    """
    chunks = [x.strip() for x in block.split(";") if x.strip()]
    info = {"chunks": len(chunks), "over_cap": len(chunks) > max_claims}
    seen = set()
    claims = []
    for chunk in chunks:
        claim = parse_claim(chunk)
        marker = claim.key if claim.valid else ("invalid", re.sub(r"\s+", "", chunk))
        if marker in seen:
            continue
        seen.add(marker)
        claims.append(claim)
    info["unique"] = len(claims)
    info["invalid"] = sum(not c.valid for c in claims)
    return claims, info


def entity_points(args):
    """All point names referenced by canonical args (circle aliases excluded)."""
    found = []

    def walk(node):
        if isinstance(node, tuple) and len(node) == 2 and node[0] == "name" and isinstance(node[1], str):
            if re.fullmatch(r"[A-Z][0-9]*", node[1]):
                found.append(node[1])
            return
        if isinstance(node, tuple):
            for item in node:
                if isinstance(item, tuple):
                    walk(item)

    walk(args)
    return found


__all__ = ["Claim", "SCHEMA_VERSION", "entity_points", "extract_block", "parse_block", "parse_claim", "validate_schema"]
