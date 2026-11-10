"""Reward bank for protocol v3 GRPO: one computation per batch, three reward heads.

TRL calls ``answer_reward``, ``format_reward`` and ``perception_reward`` in turn
with the same completions list. The bank computes every component once, caches
it for the batch and appends one JSONL record per rollout, so logs never depend
on TRL's own logging. Every record carries the reward actually used by the arm
*and* the v5 score against the row's own metadata (``v5_own``), which is the
quantity that tells whether a placebo-trained policy perceives its own image.
"""
import hashlib
import json
import threading
import time
from pathlib import Path

from src.data.intergps_index import Geometry
from src.data.perception_v4 import scoped_score
from src.rewards.answer import AnswerVerifier
from src.rewards.perception_v5 import V5Config, score_v5
from src.training.protocol_v3 import PROTOCOL, extract_answer, format_reward, parse_completion

RECORD_SCHEMA = "rl-rollout-v1"
V5_FIELDS = ["reward", "status", "tp", "false", "unknown", "chunks", "unique", "recall", "verified_precision",
             "false_reasons"]


def completion_text(completion):
    if isinstance(completion, str):
        return completion
    message = completion[-1] if isinstance(completion, list) else completion
    content = message.get("content", "") if isinstance(message, dict) else str(message)
    if isinstance(content, list):
        return "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return str(content)


class RewardBank:
    def __init__(self, arm, weights, v5_config=None, log_path=None, verifier=None, run_meta=None, protocol=PROTOCOL):
        self.protocol = protocol  # the run's protocol id, written into every rollout record
        self.mode = arm["perception_reward"]
        if self.mode not in {"none", "v4", "v5"}:
            raise ValueError("unknown perception reward mode")
        self.weights = {"answer": float(weights["answer"]), "format": float(weights["format"]),
                        "perception": float(weights["perception"])}
        self.v5_config = v5_config or V5Config()
        self.verifier = verifier or AnswerVerifier()
        self.log_path = Path(log_path) if log_path else None
        if self.log_path:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.run_meta = dict(run_meta or {})
        self._lock = threading.Lock()
        self._geometry = {}
        self._cache_key, self._cache = None, None
        self.calls = 0

    def reward_funcs(self):
        return [self.answer_reward, self.format_reward, self.perception_reward]

    def reward_weights(self):
        return [self.weights["answer"], self.weights["format"], self.weights["perception"]]

    def _geom(self, text):
        key = hashlib.sha1(text.encode()).hexdigest()
        if key not in self._geometry:
            self._geometry[key] = Geometry.from_json(text)
        return self._geometry[key]

    def compute(self, completions, kw):
        texts = [completion_text(c) for c in completions]
        key = (id(completions), hashlib.sha1("\x00".join(texts).encode()).hexdigest())
        if key == self._cache_key:
            return self._cache
        n = len(texts)
        columns = ["reference_answer", "sample_id", "original_id", "meta_source", "gold_reward", "neg_reward",
                   "geom_reward", "gold_own", "neg_own", "geom_own"]
        for column in columns:
            if len(kw.get(column, [])) != n:
                raise ValueError(f"reward metadata misaligned for column {column}")
        answers = [extract_answer(t)[0] for t in texts]
        verdicts = self.verifier.verify_many(answers, kw["reference_answer"])
        state = kw.get("trainer_state")
        step = getattr(state, "global_step", None)
        ids = kw.get("completion_ids")
        records = []
        for i, text in enumerate(texts):
            gold_reward = json.loads(kw["gold_reward"][i])
            neg_reward = json.loads(kw["neg_reward"][i])
            v5 = score_v5(text, gold_reward, self._geom(kw["geom_reward"][i]), neg_reward, self.v5_config)
            own_is_reward = kw["meta_source"][i] == kw["sample_id"][i]
            v5_own = v5 if own_is_reward else score_v5(text, json.loads(kw["gold_own"][i]), self._geom(kw["geom_own"][i]),
                                                        json.loads(kw["neg_own"][i]), self.v5_config)
            v4 = scoped_score(text, gold_reward, neg_reward)
            answer = float(bool(verdicts[i].get("correct")))
            fmt = format_reward(text, self.v5_config.max_claims)
            perception = {"none": 0.0, "v4": float(v4["reward"]), "v5": float(v5["reward"])}[self.mode]
            total = self.weights["answer"] * answer + self.weights["format"] * fmt + self.weights["perception"] * perception
            parsed = parse_completion(text)
            records.append({
                "schema": RECORD_SCHEMA,
                "protocol": self.protocol,
                **self.run_meta,
                "global_step": step,
                "call": self.calls,
                "index": i,
                "sample_id": kw["sample_id"][i],
                "original_id": kw["original_id"][i],
                "meta_source": kw["meta_source"][i],
                "completion": text,
                "completion_tokens": len(ids[i]) if ids is not None else None,
                "protocol_ok": parsed["protocol_ok"],
                "answer": {"extracted": answers[i], "correct": bool(answer), "status": verdicts[i].get("status"),
                           "normalized": verdicts[i].get("normalized_answer")},
                "format": fmt,
                "v4": {k: v4.get(k) for k in ["reward", "precision", "recall", "f1", "masked_predictions", "format_valid"]},
                "v5": {k: v5.get(k) for k in V5_FIELDS + ["verdicts"]},
                "v5_own": {k: v5_own.get(k) for k in V5_FIELDS},
                "rewards": {"answer": answer, "format": fmt, "perception": perception},
                "weights": dict(self.weights),
                "weighted_total": total,
                "time": time.time(),
            })
        self._write(records)
        self._log_metrics(records, kw.get("log_metric"))
        self.calls += 1
        self._cache_key, self._cache = key, records
        return records

    def _write(self, records):
        if not self.log_path:
            return
        with self._lock, self.log_path.open("a", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    @staticmethod
    def _log_metrics(records, log_metric):
        if not callable(log_metric) or not records:
            return
        n = len(records)
        claims = sum(r["v5_own"]["unique"] or 0 for r in records)
        unknown = sum(r["v5_own"]["unknown"] or 0 for r in records)
        metrics = {
            "p3/answer_acc": sum(r["rewards"]["answer"] for r in records) / n,
            "p3/format_rate": sum(r["rewards"]["format"] for r in records) / n,
            "p3/protocol_ok": sum(bool(r["protocol_ok"]) for r in records) / n,
            "p3/perception_reward": sum(r["rewards"]["perception"] for r in records) / n,
            "p3/v5_own_reward": sum(r["v5_own"]["reward"] for r in records) / n,
            "p3/v5_own_false_per_completion": sum(r["v5_own"]["false"] or 0 for r in records) / n,
            "p3/v5_own_recall": sum(r["v5_own"]["recall"] or 0 for r in records) / n,
            "p3/claims_per_completion": claims / n,
            "p3/unknown_fraction": unknown / claims if claims else 0.0,
            "p3/v4_f1": sum(r["v4"]["f1"] or 0 for r in records) / n,
            "p3/verifier_errors": sum(r["answer"]["status"] in {"verifier_timeout", "verifier_crashed"} for r in records) / n,
        }
        for name, value in metrics.items():
            log_metric(name, float(value))

    def answer_reward(self, completions, **kw):
        return [r["rewards"]["answer"] for r in self.compute(completions, kw)]

    def format_reward(self, completions, **kw):
        return [r["rewards"]["format"] for r in self.compute(completions, kw)]

    def perception_reward(self, completions, **kw):
        return [r["rewards"]["perception"] for r in self.compute(completions, kw)]

    def close(self):
        self.verifier.close()


__all__ = ["RECORD_SCHEMA", "RewardBank", "completion_text"]
