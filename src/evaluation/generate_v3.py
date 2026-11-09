"""Batched protocol-v3 generation and scoring shared by probes and evaluation.

Decoding is defined by this module, not by the checkpoint's generation_config
(Qwen2.5-VL ships repetition_penalty=1.05 and do_sample=true): greedy by default,
repetition_penalty 1.0, image placeholder token suppressed, stop at
``<|im_end|>``/``<|endoftext|>``. Every model (V0 and trained adapters) is
evaluated with exactly these settings.
"""
import json
import time

from src.data.intergps_index import Geometry
from src.data.perception_v4 import scoped_score
from src.rewards.perception_v5 import V5Config, score_v5
from src.training.protocol_v3 import PROTOCOL, eval_messages, extract_answer, format_reward, parse_completion

VERSION = "generate-v3-20261110"


def decoding_config(processor, model, max_new_tokens, do_sample=False, temperature=1.0, top_p=1.0):
    from transformers import GenerationConfig

    tokenizer = processor.tokenizer
    eos = [tokenizer.convert_tokens_to_ids(t) for t in ("<|im_end|>", "<|endoftext|>")]
    eos = [e for e in eos if isinstance(e, int) and e >= 0]
    options = dict(max_new_tokens=int(max_new_tokens), do_sample=bool(do_sample), repetition_penalty=1.0,
                   eos_token_id=eos, pad_token_id=tokenizer.pad_token_id, disable_compile=True)
    image_token = getattr(model.config, "image_token_id", None)
    if image_token is not None:
        options["suppress_tokens"] = [int(image_token)]
    if do_sample:
        options.update(temperature=float(temperature), top_p=float(top_p), top_k=0)
    else:
        options.update(temperature=None, top_p=None, top_k=None)
    return GenerationConfig(**options), eos


def generate(model, processor, requests, max_new_tokens=1024, batch_size=16, do_sample=False, temperature=1.0,
             top_p=1.0, seed=0, progress=None):
    """Generate one completion per request.

    ``requests``: dicts with ``id``, ``problem`` and optional ``image`` (PIL image or None).
    Returns one dict per request with the raw text and token accounting.
    """
    import torch

    tokenizer = processor.tokenizer
    previous_side = tokenizer.padding_side
    tokenizer.padding_side = "left"
    config, eos = decoding_config(processor, model, max_new_tokens, do_sample, temperature, top_p)
    device = next(model.parameters()).device
    results = []
    try:
        for start in range(0, len(requests), batch_size):
            chunk = requests[start:start + batch_size]
            with_image = [r.get("image") is not None for r in chunk]
            if len(set(with_image)) != 1:
                raise ValueError("a generation batch must be all-image or all-text")
            texts = [processor.apply_chat_template(eval_messages(r["problem"], with_image=with_image[0]), tokenize=False,
                                                   add_generation_prompt=True) for r in chunk]
            images = [r["image"] for r in chunk] if with_image[0] else None
            inputs = processor(text=texts, images=images, padding=True, return_tensors="pt").to(device)
            if do_sample:
                torch.manual_seed(seed + start)
            began = time.time()
            with torch.no_grad():
                output = model.generate(**inputs, generation_config=config)
            elapsed = time.time() - began
            prompt_width = inputs["input_ids"].shape[1]
            for i, request in enumerate(chunk):
                generated = output[i, prompt_width:].tolist()
                ended = False
                for j, token in enumerate(generated):
                    if token in eos:
                        generated = generated[:j]
                        ended = True
                        break
                text = tokenizer.decode(generated, skip_special_tokens=True)
                results.append({
                    "id": request["id"],
                    "text": text,
                    "has_image": with_image[0],
                    "prompt_tokens": int(inputs["attention_mask"][i].sum()),
                    "completion_tokens": len(generated),
                    "ended_eos": ended,
                    "budget_exhausted": (not ended) and len(generated) >= int(max_new_tokens),
                    "batch_seconds": elapsed,
                })
            if progress:
                progress(len(results), len(requests))
    finally:
        tokenizer.padding_side = previous_side
    return results


def score(results, references, verifier, v5_config=None):
    """Attach protocol, answer, format, v4 and v5 scores.

    ``references`` maps id -> dict(answer, gold_tokens (list), negative_tokens (list), geometry (Geometry|json|None)).
    """
    v5_config = v5_config or V5Config()
    answers = [extract_answer(r["text"])[0] for r in results]
    verdicts = verifier.verify_many(answers, [references[r["id"]]["answer"] for r in results])
    scored = []
    for result, answer, verdict in zip(results, answers, verdicts):
        ref = references[result["id"]]
        geometry = ref.get("geometry")
        if isinstance(geometry, str):
            geometry = Geometry.from_json(geometry)
        gold, negative = list(ref.get("gold_tokens") or []), list(ref.get("negative_tokens") or [])
        parsed = parse_completion(result["text"])
        v5 = score_v5(result["text"], gold, geometry, negative, v5_config) if gold else None
        v4 = scoped_score(result["text"], gold, negative) if gold else None
        scored.append({
            **result,
            "protocol": PROTOCOL,
            "protocol_ok": parsed["protocol_ok"],
            "format": format_reward(result["text"], v5_config.max_claims),
            "answer": {"extracted": answer, "correct": bool(verdict.get("correct")), "status": verdict.get("status"),
                       "normalized": verdict.get("normalized_answer")},
            "v5": None if v5 is None else {k: v5.get(k) for k in ["reward", "status", "tp", "false", "unknown", "chunks",
                                                                 "unique", "recall", "verified_precision",
                                                                 "false_reasons"]},
            "v4": None if v4 is None else {k: v4.get(k) for k in ["reward", "precision", "recall", "f1",
                                                                 "masked_predictions"]},
        })
    return scored


def summarize(scored):
    n = len(scored)
    if not n:
        return {"n": 0}
    with_gold = [s for s in scored if s["v5"] is not None]
    lengths = sorted(s["completion_tokens"] for s in scored)
    return {
        "n": n,
        "protocol_ok_rate": sum(s["protocol_ok"] for s in scored) / n,
        "format_rate": sum(s["format"] for s in scored) / n,
        "answer_accuracy": sum(s["answer"]["correct"] for s in scored) / n,
        "answer_status": _count(s["answer"]["status"] for s in scored),
        "eos_rate": sum(s["ended_eos"] for s in scored) / n,
        "budget_exhausted_rate": sum(s["budget_exhausted"] for s in scored) / n,
        "completion_tokens_mean": sum(lengths) / n,
        "completion_tokens_p50": lengths[n // 2],
        "completion_tokens_p90": lengths[min(n - 1, int(0.9 * n))],
        "completion_tokens_max": lengths[-1],
        "v5_reward_mean": sum(s["v5"]["reward"] for s in with_gold) / len(with_gold) if with_gold else None,
        "v5_recall_mean": sum(s["v5"]["recall"] for s in with_gold) / len(with_gold) if with_gold else None,
        "v5_false_mean": sum(s["v5"]["false"] for s in with_gold) / len(with_gold) if with_gold else None,
        "claims_mean": sum(s["v5"]["unique"] for s in with_gold) / len(with_gold) if with_gold else None,
        "version": VERSION,
    }


def _count(values):
    counts = {}
    for value in values:
        counts[str(value)] = counts.get(str(value), 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


__all__ = ["VERSION", "decoding_config", "generate", "score", "summarize", "write_jsonl"]
