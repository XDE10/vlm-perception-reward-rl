import json

import pytest

from src.training.rl_data import build_items, load_training_rows
from src.training.rl_rewards import RewardBank, completion_text
from tests._mini_release import make_release, mini_config

pytest.importorskip("PIL")


class FakeVerifier:
    def __init__(self):
        self.calls = 0

    def verify_many(self, answers, references):
        self.calls += 1
        return [{"correct": a is not None and a == r, "status": "equivalent" if a == r else "mismatch",
                 "normalized_answer": a} for a, r in zip(answers, references)]

    def close(self):
        pass


def batch(tmp_path, arm):
    make_release(tmp_path)
    config = mini_config(tmp_path, arm)
    rows, index = load_training_rows(config, tmp_path)
    items, _ = build_items(config, rows, index, tmp_path, load_images=False)
    keys = ["reference_answer", "sample_id", "original_id", "meta_source", "gold_reward", "neg_reward", "geom_reward",
            "gold_own", "neg_own", "geom_own"]
    kw = {k: [item[k] for item in items[:2]] for k in keys}
    return config, kw


GOOD = "<perception>Length(A,B)=3; PointLiesOnLine(C,(A,B))</perception><think>t</think><answer>{}</answer>"
SPRAY = "<perception>PointLiesOnLine(D,(A,B)); Perpendicular((A,B),(A,C))</perception><think>t</think><answer>0</answer>"


def make_bank(tmp_path, config, weights, verifier=None):
    return RewardBank(config["arm"], weights, log_path=tmp_path / "rollouts.jsonl", verifier=verifier or FakeVerifier(),
                      run_meta={"arm": config["arm"]["name"], "seed": config["seed"]})


def test_components_logging_and_single_computation_per_batch(tmp_path):
    config, kw = batch(tmp_path, "rl_v5")
    verifier = FakeVerifier()
    bank = make_bank(tmp_path, config, {"answer": 1.0, "format": 0.05, "perception": 0.1}, verifier)
    completions = [[{"role": "assistant", "content": GOOD.format(kw["reference_answer"][0])}],
                   [{"role": "assistant", "content": SPRAY}]]
    metrics = {}
    kw = dict(kw, log_metric=lambda name, value: metrics.__setitem__(name, value))
    answer = bank.answer_reward(completions, **kw)
    fmt = bank.format_reward(completions, **kw)
    perception = bank.perception_reward(completions, **kw)
    assert verifier.calls == 1  # three reward heads, one computation
    assert answer == [1.0, 0.0] and fmt == [1.0, 1.0]
    assert perception[0] == pytest.approx(1.0) and perception[1] < 0  # sprayed claims are refuted by geometry
    records = [json.loads(x) for x in (tmp_path / "rollouts.jsonl").read_text().splitlines()]
    assert len(records) == 2 and records[0]["arm"] == "rl_v5"
    assert records[0]["weighted_total"] == pytest.approx(1.0 + 0.05 + 0.1)
    assert records[1]["v5"]["false_reasons"] and records[1]["v5"]["verdicts"]
    assert records[0]["v5_own"]["reward"] == records[0]["v5"]["reward"]
    assert metrics["p3/answer_acc"] == 0.5


def test_mode_none_and_v4(tmp_path):
    config, kw = batch(tmp_path, "rl_ans")
    completions = [GOOD.format(kw["reference_answer"][0]), SPRAY]
    bank = make_bank(tmp_path, config, {"answer": 1.0, "format": 0.05, "perception": 0.0})
    assert bank.perception_reward(completions, **kw) == [0.0, 0.0]
    config["arm"]["perception_reward"] = "v4"
    bank = make_bank(tmp_path, config, {"answer": 1.0, "format": 0.05, "perception": 0.2})
    v4 = bank.perception_reward(completions, **kw)
    assert v4[0] == pytest.approx(1.0) and v4[1] >= 0.0  # v4 never goes negative


def test_placebo_reward_uses_other_metadata_but_logs_own_score(tmp_path):
    config, kw = batch(tmp_path, "rl_v5_placebo")
    assert kw["meta_source"] != kw["sample_id"]
    bank = make_bank(tmp_path, config, {"answer": 1.0, "format": 0.05, "perception": 0.1})
    bank.perception_reward([GOOD.format("2")] * 2, **kw)
    records = [json.loads(x) for x in (tmp_path / "rollouts.jsonl").read_text().splitlines()]
    assert all(r["meta_source"] != r["sample_id"] for r in records)
    assert all("reward" in r["v5_own"] for r in records)


def test_rollout_records_carry_the_run_protocol(tmp_path):
    from src.training.protocol_v3 import PROTOCOL, protocol_id

    config, kw = batch(tmp_path, "rl_v5")
    bank = make_bank(tmp_path, config, {"answer": 1.0, "format": 0.05, "perception": 0.1})
    bank.answer_reward([GOOD.format("2")] * 2, **kw)
    p1 = RewardBank(config["arm"], {"answer": 1.0, "format": 0.05, "perception": 0.1}, log_path=tmp_path / "p1.jsonl",
                    verifier=FakeVerifier(), protocol=protocol_id("p1"))
    p1.answer_reward([GOOD.format("3")] * 2, **kw)
    read = lambda name: [json.loads(x) for x in (tmp_path / name).read_text().splitlines()]  # noqa: E731
    assert {r["protocol"] for r in read("rollouts.jsonl")} == {PROTOCOL}  # default: the protocol of rl_v3.json
    assert {r["protocol"] for r in read("p1.jsonl")} == {protocol_id("p1")}


def test_misaligned_metadata_fails_closed(tmp_path):
    config, kw = batch(tmp_path, "rl_v5")
    kw["gold_reward"] = kw["gold_reward"][:1]
    bank = make_bank(tmp_path, config, {"answer": 1.0, "format": 0.05, "perception": 0.1})
    with pytest.raises(ValueError, match="misaligned"):
        bank.answer_reward([GOOD.format("2"), SPRAY], **kw)


def test_completion_text_handles_trl_shapes():
    assert completion_text("x") == "x"
    assert completion_text([{"role": "assistant", "content": "y"}]) == "y"
    assert completion_text([{"role": "assistant", "content": [{"type": "text", "text": "z"}]}]) == "z"
