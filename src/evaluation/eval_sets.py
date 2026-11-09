"""Pre-registered evaluation-set rules (docs/plan/S3设计_20261109.md sections 1-3).

The rules read only the question text, the reference answer and the InterGPS human annotations, never a model
output:

* vision-needed (``test_vn``): the question has no digit and the diagram annotation has a numeric value;
* CF-Geo candidates: vision-needed, every numeric diagram value is a plain length or angle, the goal is a length
  (degree 1) or an area (degree 2), the reference parses, and any rounding request is "nearest tenth / hundredth /
  thousandth" with a plain decimal reference;
* the swapped-image condition pairs every test row with a row whose image pixels differ (fixed seed).

Wrapper rows (``hiyouga/geometry3k``) are joined to InterGPS records by exact RGB pixels plus the normalised
question, the rule of ``src/data/project3_audit.py``. Row ids are wrapper locators, ``<split>:<row>``, the same
ids the release uses. ``build_eval_sets`` is deterministic: the VM rebuilds the specification from the pinned
public files and the packed annotations and must get the committed one byte for byte.
"""
import hashlib
import json
import re
from collections import Counter
from decimal import ROUND_HALF_UP, Decimal

from src.data.project3_audit import norm, question_forms

RULES_VERSION = "eval-sets-v1-20261109"
SCHEMA = "p3-eval-sets-v1"
SWAP_SEED = 20261109
DIGIT = re.compile(r"[0-9]")
PLAIN_NUMBER = re.compile(r"^\s*\d+(?:\.\d+)?\s*$")
SINGLE_LETTER = re.compile(r"^\s*[a-z]\s*$")
ROUNDING_WORD = re.compile(r"\b(round|nearest)\b", re.I)
ROUNDING_PLACES = re.compile(r"\bnearest\s+(tenth|hundredth|thousandth)\b", re.I)
PLACES = {"tenth": 1, "hundredth": 2, "thousandth": 3}
DECIMAL = re.compile(r"^\d+(?:\.\d+)?$")
LENGTH_GOALS = ("Find(LengthOf(", "Find(PerimeterOf(", "Find(RadiusOf(", "Find(DiameterOf(")
LETTER_GOAL = re.compile(r"^Find\(([a-z])\)$")


def split_equals(form):
    """``Equals(F(args), value)`` -> ("F", "value"); None for any other form. The value may be an expression."""
    form = str(form).strip()
    if not form.startswith("Equals(") or not form.endswith(")"):
        return None
    body = form[len("Equals("):-1]
    depth = 0
    for i, ch in enumerate(body):
        depth += ch == "("
        depth -= ch == ")"
        if ch == "," and depth == 0:
            return body[:i].strip().split("(", 1)[0], body[i + 1:].strip()
    return None


def diagram_values(diagram_forms):
    return [v for v in (split_equals(f) for f in diagram_forms or []) if v]


def question_text(problem):
    return str(problem).replace("<image>", "").strip()


def vision_needed(problem, diagram_forms):
    """Rule of section 2: no digit in the question, at least one numeric value in the diagram annotation."""
    numeric = [v for v in diagram_values(diagram_forms) if DIGIT.search(v[1])]
    return bool(numeric) and not DIGIT.search(question_text(problem))


def gold_parses(answer):
    """True when the training verifier can grade against this reference (strict worker's typed gate)."""
    from math_verify import LatexExtractionConfig, parse

    from scripts.training.math_verify_v3_strict_worker import relation_answer

    reference = str(answer)
    if not reference.strip() or relation_answer(reference):
        return False
    parsed = parse(r"\boxed{" + reference + "}", extraction_config=[LatexExtractionConfig()], extraction_mode="first_match",
                   parsing_timeout=0)
    return bool(parsed) and any(not isinstance(x, str) for x in parsed)


def rounding_places(problem):
    """None: no rounding requested; an int: decimal places requested; "unrecognised": some other rounding phrase."""
    text = question_text(problem)
    if not ROUNDING_WORD.search(text):
        return None
    match = ROUNDING_PLACES.search(text)
    return PLACES[match.group(1).lower()] if match else "unrecognised"


def cf_candidate(problem, answer, diagram_forms, text_forms, parse_check=gold_parses):
    """Section 3.1. Returns {"ok": bool, "reason": str|None, "degree", "places", "lengths", "angles"}."""
    out = {"ok": False, "reason": None, "degree": None, "places": None, "lengths": [], "angles": []}
    if not vision_needed(problem, diagram_forms):
        out["reason"] = "not vision-needed"
        return out
    values = diagram_values(diagram_forms)
    numeric = [v for v in values if DIGIT.search(v[1])]
    lengths = [v[1].strip() for v in values if v[0] == "LengthOf"]
    angles = [v[1].strip() for v in values if v[0] == "MeasureOf"]
    if any(v[0] not in ("LengthOf", "MeasureOf") for v in numeric):
        out["reason"] = "numeric value that is not a length or an angle"
    elif not all(PLAIN_NUMBER.match(v) or SINGLE_LETTER.match(v) for v in lengths):
        out["reason"] = "length label is an expression"
    elif not all(PLAIN_NUMBER.match(v) for v in angles):
        out["reason"] = "angle label is not a plain number"
    elif not any(PLAIN_NUMBER.match(v) for v in lengths):
        out["reason"] = "no numeric length label"
    if out["reason"]:
        return out
    goal = next((str(f).strip() for f in text_forms or [] if str(f).strip().startswith("Find(")), "")
    letter = LETTER_GOAL.match(goal)
    if letter:
        degree = 1 if any(letter.group(1) == v for v in lengths) else None
    elif goal.startswith(LENGTH_GOALS):
        degree = 1
    elif goal.startswith("Find(AreaOf("):
        degree = 2
    else:
        degree = None
    if degree is None:
        out["reason"] = "goal is not a length or an area"
        return out
    if not parse_check(answer):
        out["reason"] = "reference does not parse"
        return out
    places = rounding_places(problem)
    if places == "unrecognised":
        out["reason"] = "rounding phrase not recognised"
        return out
    if places is not None and not DECIMAL.match(str(answer).strip()):
        out["reason"] = "rounding requested but the reference is not a plain decimal"
        return out
    if places is not None and not on_grid(answer, places):
        out["reason"] = "reference has more decimals than the rounding request"
        return out
    out.update(ok=True, degree=degree, places=places, lengths=[v for v in lengths if PLAIN_NUMBER.match(v)],
               angles=angles)
    return out


def on_grid(value, places):
    number = Decimal(str(value).strip())
    return number == number.quantize(Decimal(1).scaleb(-int(places)))


def rounded_answer_set(gold, places, factor):
    """S_m = {round_half_up(m*v, p) : v in [g - h, g + h)}, h = 0.5 * 10^-p (section 3.1), as decimal strings."""
    if not on_grid(gold, places):
        raise ValueError("reference %r is not rounded to %s places" % (gold, places))
    g, m = Decimal(str(gold).strip()), Decimal(str(factor))
    unit = Decimal(1).scaleb(-int(places))
    half = unit / 2
    low, high = m * (g - half), m * (g + half)
    value = low.quantize(unit, rounding=ROUND_HALF_UP)
    out = []
    while value - half < high:
        if value + half > low:
            out.append(str(value))
        value += unit
    return out


def scale_number(text, factor):
    """k * v for a printed label: integers stay integers, decimals use the fewest digits of the exact value."""
    value = Decimal(str(text).strip()) * Decimal(str(factor))
    out = format(value.normalize(), "f")
    return out


def scaled_exact_gold(answer, factor):
    """LaTeX for factor * answer (exact references only), checked to be equivalent by sympy."""
    import sympy
    from math_verify import LatexExtractionConfig, parse

    reference = str(answer).strip()
    if DECIMAL.match(reference):
        return scale_number(reference, factor)
    parsed = parse(r"\boxed{" + reference + "}", extraction_config=[LatexExtractionConfig()], extraction_mode="first_match",
                   parsing_timeout=0)
    expr = next(x for x in parsed if not isinstance(x, str))
    text = sympy.latex(sympy.Integer(int(factor)) * expr)
    check = parse(r"\boxed{" + text + "}", extraction_config=[LatexExtractionConfig()], extraction_mode="first_match",
                  parsing_timeout=0)
    again = next(x for x in check if not isinstance(x, str))
    if sympy.simplify(again - sympy.Integer(int(factor)) * expr) != 0:
        raise ValueError("scaled reference %r is not %s x %r" % (text, factor, reference))
    return text


def join_rows(split, rows, records):
    """Join wrapper rows of one split to InterGPS records: pixels first, then the normalised question."""
    by_pixels = {}
    for record in records:
        by_pixels.setdefault(record["image_pixel_sha256"], []).append(record)
    joined = []
    for number, row in enumerate(rows):
        candidates = by_pixels.get(row["pixel"], [])
        agreeing = [r for r in candidates if norm(row["problem"]).rstrip(".") in question_forms(r).values()]
        status = ("matched" if len(agreeing) == 1 else "ambiguous" if agreeing else
                  "question_conflict" if candidates else "missing_image")
        joined.append({"id": "%s:%d" % (split, number), "pixel": row["pixel"], "problem": row["problem"],
                       "answer": row["answer"], "status": status,
                       "record": agreeing[0] if status == "matched" else None})
    return joined


def swap_pairing(items, seed=SWAP_SEED):
    from src.training.rl_data import placebo_mapping

    return placebo_mapping([{"sample_id": x["id"], "image_pixel_sha256": x["pixel"]} for x in items], seed)


def _forms(record):
    diagram = (record.get("diagram_annotation") or {}).get("diagram_logic_forms") or []
    text = (record.get("dissolved_annotation") or {}).get("text_logic_forms") or []
    return diagram, text


def build_eval_sets(wrapper, records, sources=None, parse_check=gold_parses):
    """wrapper: {"validation": [row], "test": [row]} with row = {"problem", "answer", "pixel"} in parquet order.
    records: InterGPS records in the format of data/project3_audit/intergps_annotations.jsonl."""
    joined = {split: join_rows(split, wrapper[split], [r for r in records if r.get("split") == split])
              for split in ("validation", "test")}
    test = joined["test"]
    vn, vn_excluded = [], Counter()
    for item in test:
        if item["status"] != "matched":
            vn_excluded["not joined (%s)" % item["status"]] += 1
            continue
        diagram, _ = _forms(item["record"])
        if vision_needed(item["problem"], diagram):
            vn.append(item["id"])
        else:
            vn_excluded["not vision-needed"] += 1
    cf, cf_excluded = [], Counter()
    for split in ("validation", "test"):
        for item in joined[split]:
            if item["status"] != "matched":
                cf_excluded["not joined (%s)" % item["status"]] += 1
                continue
            diagram, text = _forms(item["record"])
            verdict = cf_candidate(item["problem"], item["answer"], diagram, text, parse_check)
            if not verdict["ok"]:
                cf_excluded[verdict["reason"]] += 1
                continue
            cf.append({"id": item["id"], "pixel": item["pixel"], "original_id": str(item["record"]["original_id"]),
                       "answer": str(item["answer"]), "degree": verdict["degree"], "places": verdict["places"],
                       "lengths": verdict["lengths"], "angles": verdict["angles"]})
    spec = {
        "schema": SCHEMA, "rules_version": RULES_VERSION, "design": "docs/plan/S3设计_20261109.md sections 1-3",
        "sources": sources or {},
        "test601": [{"id": x["id"], "pixel": x["pixel"], "join": x["status"],
                     "original_id": str(x["record"]["original_id"]) if x["record"] else None} for x in test],
        "test_vn": vn,
        "swap_seed": SWAP_SEED,
        "swap": swap_pairing(test),
        "cf_candidates": cf,
        "excluded": {"test_vn": dict(sorted(vn_excluded.items())), "cf_candidates": dict(sorted(cf_excluded.items()))},
        "counts": {"test601": len(test), "test_vn": len(vn), "cf_candidates": len(cf),
                   "cf_candidates_by_split": dict(Counter(x["id"].split(":")[0] for x in cf)),
                   "cf_rounded": sum(x["places"] is not None for x in cf),
                   "cf_degree": dict(Counter(str(x["degree"]) for x in cf)),
                   "joined": {s: dict(Counter(x["status"] for x in joined[s])) for s in joined}},
    }
    return spec


def canonical_sha256(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


__all__ = ["RULES_VERSION", "SCHEMA", "SWAP_SEED", "build_eval_sets", "canonical_sha256", "cf_candidate",
           "diagram_values", "gold_parses", "join_rows", "on_grid", "rounded_answer_set", "rounding_places", "scale_number",
           "scaled_exact_gold", "split_equals", "swap_pairing", "vision_needed"]
