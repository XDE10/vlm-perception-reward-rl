"""Refute perception claims with InterGPS human geometry (never certify them).

``refute(claim, geometry, config)`` returns a short reason string when the claim
is contradicted by the annotated diagram, otherwise ``None`` (the claim stays
UNKNOWN unless it is a certified positive). Checks use only translation- and
scale-invariant quantities: normalised point-to-line distance, the angle between
two directions and the relative deviation from a circle radius. Textbook figures
are not always drawn to scale, so value-based checks (angle size, equal lengths,
equal angles) are off by default and must pass calibration before use (D5/D6
in docs/plan/决策记录.md).
"""
import math
from dataclasses import asdict, dataclass

from src.rewards.claims import entity_points

ORACLE_VERSION = "geometry-oracle-v1-20261109"


@dataclass(frozen=True)
class OracleConfig:
    line_distance: float = 0.06
    parallel_deg: float = 15.0
    perpendicular_deg: float = 15.0
    circle_relative: float = 0.15
    check_point_existence: bool = True
    check_circle_existence: bool = True
    check_angle_value: bool = False
    angle_value_deg: float = 35.0
    check_congruent_length: bool = False
    congruent_length_ratio: float = 1.5
    check_congruent_angle: bool = False
    congruent_angle_deg: float = 25.0

    def to_dict(self):
        return asdict(self)


def _name(entity):
    if isinstance(entity, tuple) and len(entity) == 2 and entity[0] == "name":
        return entity[1]
    return None


def _pair(entity):
    if isinstance(entity, tuple) and len(entity) == 2 and entity[0] == "tuple" and len(entity[1]) == 2:
        a, b = (_name(x) for x in entity[1])
        if a and b:
            return a, b
    return None


def _triple(entity):
    if isinstance(entity, tuple) and len(entity) == 2 and entity[0] == "tuple" and len(entity[1]) == 3:
        names = tuple(_name(x) for x in entity[1])
        if all(names):
            return names
    return None


def _circle_centre(entity, geometry):
    """Centre name for Circle(O); a bare alias resolves only when the diagram has one circle."""
    if isinstance(entity, tuple) and len(entity) == 2 and entity[0] == "Circle" and len(entity[1]) == 1:
        return _name(entity[1][0]), "explicit"
    alias = _name(entity)
    if alias and alias.startswith("Circle"):
        known = _known_circles(geometry)
        return (next(iter(known)) if len(known) == 1 else None), "alias"
    return None, "unknown"


def _known_circles(geometry):
    return set(geometry.circles) | set(geometry.circle_points)


def _xy(geometry, *names):
    if not all(n in geometry.points for n in names):
        return None
    return [geometry.points[n] for n in names]


def _direction_deg(p, q):
    return math.degrees(math.atan2(q[1] - p[1], q[0] - p[0])) % 180.0


def _line_gap(a, b):
    diff = abs(a - b) % 180.0
    return min(diff, 180.0 - diff)


def _line_distance(p, a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]
    norm2 = vx * vx + vy * vy
    if norm2 == 0:
        return None, None
    cross = abs(vx * (p[1] - a[1]) - vy * (p[0] - a[0]))
    t = ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / norm2
    return cross / norm2, t


def _angle_at(vertex, a, c):
    v1 = (a[0] - vertex[0], a[1] - vertex[1])
    v2 = (c[0] - vertex[0], c[1] - vertex[1])
    n1, n2 = math.hypot(*v1), math.hypot(*v2)
    if n1 == 0 or n2 == 0:
        return None
    cos = max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))
    return math.degrees(math.acos(cos))


def _constant(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def refute(claim, geometry, config=OracleConfig()):
    if not claim.valid:
        return "invalid_chunk"
    relation, args = claim.relation, claim.args
    if config.check_point_existence and geometry.point_names:
        unknown = [p for p in entity_points(args) if p not in geometry.point_names]
        if unknown:
            return "unknown_point"
    if relation in {"PointLiesOnCircle", "Tangent"} and config.check_circle_existence:
        centre, kind = _circle_centre(args[1], geometry)
        known = _known_circles(geometry)
        if not known:
            return "no_circle_in_diagram"
        if kind == "explicit" and centre not in known:
            return "unknown_circle"
    if relation == "PointLiesOnLine":
        point, pair = _name(args[0]), _pair(args[1])
        if not point or not pair:
            return None
        if point in pair:
            return "degenerate_incidence"
        coords = _xy(geometry, point, *pair)
        if coords is None:
            return None
        distance, _ = _line_distance(*coords)
        if distance is not None and distance > config.line_distance:
            return "not_collinear"
        return None
    if relation in {"Parallel", "Perpendicular"}:
        first, second = _pair(args[0]), _pair(args[1])
        if not first or not second:
            return None
        coords = _xy(geometry, *first, *second)
        if coords is None:
            return None
        a, b, c, d = coords
        gap = _line_gap(_direction_deg(a, b), _direction_deg(c, d))
        if relation == "Parallel":
            dc, _ = _line_distance(c, a, b)
            dd, _ = _line_distance(d, a, b)
            if dc is not None and dd is not None and max(dc, dd) <= config.line_distance:
                return "collinear_pair"
            return "not_parallel" if gap > config.parallel_deg else None
        return "not_perpendicular" if abs(90.0 - gap) > config.perpendicular_deg else None
    if relation == "PointLiesOnCircle":
        point = _name(args[0])
        centre, _ = _circle_centre(args[1], geometry)
        if not point or not centre:
            return None
        coords = _xy(geometry, point, centre)
        if coords is None:
            return None
        others = [q for q in geometry.circle_points.get(centre, ()) if q != point and q in geometry.points]
        if not others:
            return None
        radii = sorted(math.dist(geometry.points[centre], geometry.points[q]) for q in others)
        radius = radii[len(radii) // 2]
        if radius <= 0:
            return None
        deviation = abs(math.dist(coords[0], coords[1]) - radius) / radius
        return "off_circle" if deviation > config.circle_relative else None
    if relation == "Angle" and config.check_angle_value:
        names = tuple(_name(x) for x in args)
        value = _constant(claim.value) if claim.unit == "deg" else None
        if len(names) != 3 or not all(names) or value is None or value > 180:
            return None
        coords = _xy(geometry, names[1], names[0], names[2])
        if coords is None:
            return None
        measured = _angle_at(*coords)
        if measured is not None and abs(measured - value) > config.angle_value_deg:
            return "angle_value_mismatch"
        return None
    if relation == "CongruentLength" and config.check_congruent_length:
        first, second = _pair(args[0]), _pair(args[1])
        coords = _xy(geometry, *first, *second) if first and second else None
        if coords is None:
            return None
        l1, l2 = math.dist(coords[0], coords[1]), math.dist(coords[2], coords[3])
        if min(l1, l2) > 0 and max(l1, l2) / min(l1, l2) > config.congruent_length_ratio:
            return "lengths_not_equal"
        return None
    if relation == "CongruentAngle" and config.check_congruent_angle:
        first, second = _triple(args[0]), _triple(args[1])
        if not first or not second:
            return None
        c1 = _xy(geometry, first[1], first[0], first[2])
        c2 = _xy(geometry, second[1], second[0], second[2])
        if c1 is None or c2 is None:
            return None
        m1, m2 = _angle_at(*c1), _angle_at(*c2)
        if m1 is not None and m2 is not None and abs(m1 - m2) > config.congruent_angle_deg:
            return "angles_not_equal"
        return None
    return None


__all__ = ["ORACLE_VERSION", "OracleConfig", "refute"]
