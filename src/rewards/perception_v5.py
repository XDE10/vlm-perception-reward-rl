"""Falsifiable perception reward v5 ("claims as bets").

Each unique claim in the single ``<perception>`` block gets one verdict:

* TRUE    - canonical key equals a certified positive fact;
* FALSE   - unparseable chunk, certified negative, conflict with a certified
            constant slot (frozen v4 rule), or refuted by the InterGPS geometry
            oracle (point existence, incidence, parallel/perpendicular, circle);
* UNKNOWN - everything else (outside the certified scope and not refuted).

    R_v5 = clip((TP - alpha * FALSE - beta * UNKNOWN) / |G+|, -1, 1)

More than ``max_claims`` raw chunks gives -1. With alpha = 1 an extra verifiable
claim raises the expected reward only if the policy believes it with p > 0.5,
and beta prices padding with unverifiable claims. Under partial labels this is
the property v4 lacked: v4 never charged for claims outside the certified slots.

Consistency gate (D35, v5.1): if the oracle refutes one of the diagram's own
certified facts, that family of checks ("coordinates" or "existence") is not
trusted for the diagram, and its refutations of other claims are dropped (the
claims stay UNKNOWN). It uses only certified facts and the annotation, so it is
identical for every arm, split and model.
"""
from collections import Counter
from dataclasses import asdict, dataclass, field

from src.data.perception_v4 import conflicts_with_certified_constant, token_key
from src.rewards.claims import SCHEMA_VERSION, extract_block, parse_block, parse_claim
from src.rewards.geometry_oracle import ORACLE_VERSION, OracleConfig, reason_family, refute

VERSION = "perception-v5.1-20261109"


@dataclass(frozen=True)
class V5Config:
    alpha: float = 1.0
    beta: float = 0.1
    max_claims: int = 24
    consistency_gate: bool = True
    oracle: OracleConfig = field(default_factory=OracleConfig)

    @classmethod
    def from_dict(cls, data):
        data = dict(data or {})
        oracle = OracleConfig(**data.pop("oracle", {}))
        return cls(oracle=oracle, **data)

    def to_dict(self):
        data = asdict(self)
        data["oracle"] = self.oracle.to_dict()
        return data


def _empty(status, mask=True, reward=0.0, chunks=0):
    return {"reward": reward, "mask": mask, "status": status, "tp": 0, "false": 0, "unknown": 0,
            "chunks": chunks, "unique": 0, "recall": 0.0, "verified_precision": 0.0,
            "false_reasons": {}, "verdicts": [], "gated": [], "version": VERSION}


def consistency_gate(gold_tokens, geometry, oracle_config=OracleConfig()):
    """{family: first certified fact it refutes} for this diagram; empty when the annotation agrees with them all."""
    gated = {}
    if geometry is None:
        return gated
    for token in gold_tokens:
        claim = parse_claim(token)
        if not claim.valid:
            continue
        reason = refute(claim, geometry, oracle_config)
        family = reason_family(reason)
        if family is not None and family not in gated:
            gated[family] = {"certified": token, "reason": reason}
    return gated


def score_v5(text, gold_tokens, geometry, negative_tokens=(), config=V5Config()):
    """Score one completion. ``geometry`` may be None (then only certified rules apply)."""
    gold = {token_key(t) for t in gold_tokens}
    if not gold:
        return _empty("no_trusted_gold", mask=False)
    block, status = extract_block(text)
    if status != "ok":
        return _empty("block_" + status)
    claims, info = parse_block(block, config.max_claims)
    if info["over_cap"]:
        result = _empty("over_cap", reward=-1.0, chunks=info["chunks"])
        result["unique"] = info["unique"]
        return result
    negatives = {token_key(t) for t in negative_tokens} - gold
    gate = consistency_gate(gold_tokens, geometry, config.oracle) if config.consistency_gate else {}
    tp = false = unknown = 0
    reasons = Counter()
    verdicts = []
    for claim in claims:
        if not claim.valid:
            verdict, reason = "FALSE", "invalid_chunk"
        elif claim.key in gold:
            verdict, reason = "TRUE", None
        elif claim.key in negatives:
            verdict, reason = "FALSE", "certified_negative"
        elif conflicts_with_certified_constant(claim.raw, list(gold_tokens)):
            verdict, reason = "FALSE", "certified_constant_conflict"
        else:
            reason = refute(claim, geometry, config.oracle) if geometry is not None else None
            if reason_family(reason) in gate:
                reason = None  # this diagram's annotation contradicts its own certified facts for this family
            verdict = "FALSE" if reason else "UNKNOWN"
        if verdict == "TRUE":
            tp += 1
        elif verdict == "FALSE":
            false += 1
            reasons[reason] += 1
        else:
            unknown += 1
        verdicts.append({"claim": claim.raw[:120], "verdict": verdict, "reason": reason})
    raw = (tp - config.alpha * false - config.beta * unknown) / len(gold)
    return {
        "reward": max(-1.0, min(1.0, raw)),
        "mask": True,
        "status": "ok" if claims else "empty",
        "tp": tp,
        "false": false,
        "unknown": unknown,
        "chunks": info["chunks"],
        "unique": info["unique"],
        "recall": tp / len(gold),
        "verified_precision": tp / (tp + false) if tp + false else 0.0,
        "false_reasons": dict(reasons),
        "verdicts": verdicts,
        "gated": sorted(gate),
        "version": VERSION,
        "schema": SCHEMA_VERSION,
        "oracle": ORACLE_VERSION,
    }


__all__ = ["V5Config", "VERSION", "consistency_gate", "score_v5"]
