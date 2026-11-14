"""Real-model GPU probe: LoRA scope, prompt budget, peak memory, generation throughput, ViT cache.

    python -m scripts.colab.gpu_probe --model-path <snapshot> --out <out>/gpu_probe.json

Measurements mirror the registered training shape: the longest training prompts
(by real processor token count, image included) with a full-length completion,
LoRA r=16 on language modules, gradient checkpointing, bf16. Nothing here
changes the experiment; the numbers feed ``decide_runtime``.
"""
import argparse
import json
import math
import statistics
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _sync(device):
    import torch

    if device.type == "cuda":
        torch.cuda.synchronize()


def _reset(device):
    import torch

    if device.type == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()


def _peak_gb(device):
    import torch

    return round(torch.cuda.max_memory_allocated() / 1e9, 2) if device.type == "cuda" else None


def _stats(values):
    values = sorted(values)
    n = len(values)
    return {"n": n, "max": values[-1], "p95": values[min(n - 1, int(math.ceil(0.95 * n)) - 1)],
            "mean": round(statistics.fmean(values), 1), "min": values[0]}


def prompt_lengths(processor, rows, root):
    from PIL import Image
    from trl.data_utils import prepare_multimodal_messages

    from src.training.protocol_v3 import training_prompt

    lengths = {}
    for row in rows:
        image = Image.open(Path(root) / row["image_path"]).convert("RGB")
        messages = prepare_multimodal_messages(training_prompt(row["problem"]), images=[image])
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        lengths[row["sample_id"]] = int(processor(text=[text], images=[image], return_tensors="pt")["input_ids"].shape[1])
    return lengths


def build_batch(processor, rows, root, completion_len, device, seed=0):
    import torch
    from PIL import Image

    from src.training.protocol_v3 import eval_messages

    tokenizer = processor.tokenizer
    side = tokenizer.padding_side
    tokenizer.padding_side = "left"
    try:
        images = [Image.open(Path(root) / r["image_path"]).convert("RGB") for r in rows]
        texts = [processor.apply_chat_template(eval_messages(r["problem"]), tokenize=False, add_generation_prompt=True)
                 for r in rows]
        inputs = processor(text=texts, images=images, padding=True, return_tensors="pt")
    finally:
        tokenizer.padding_side = side
    generator = torch.Generator().manual_seed(seed)
    completion = torch.randint(1000, 100000, (len(rows), completion_len), generator=generator)
    batch = {"input_ids": torch.cat([inputs["input_ids"], completion], dim=1),
             "attention_mask": torch.cat([inputs["attention_mask"], torch.ones_like(completion)], dim=1),
             "pixel_values": inputs["pixel_values"], "image_grid_thw": inputs["image_grid_thw"]}
    if "mm_token_type_ids" in inputs:
        batch["mm_token_type_ids"] = torch.cat([inputs["mm_token_type_ids"], torch.zeros_like(completion)], dim=1)
    return {k: v.to(device) for k, v in batch.items()}, completion.to(device), images


def completion_logps(model, batch, completion, completion_len):
    from trl.trainer.utils import selective_log_softmax

    logits = model(**batch, logits_to_keep=completion_len + 1).logits[:, :-1, :]
    return selective_log_softmax(logits, completion)


def fwd_bwd(model, processor, rows, root, completion_len, device):
    import torch

    batch, completion, _ = build_batch(processor, rows, root, completion_len, device)
    _reset(device)
    model.train()
    started = time.time()
    logps = completion_logps(model, batch, completion, completion_len)
    loss = -logps.float().mean()
    loss.backward()
    _sync(device)
    seconds = time.time() - started
    grads = [p.grad for n, p in model.named_parameters() if p.requires_grad]
    finite = all(g is not None and torch.isfinite(g).all().item() for g in grads)
    nonzero = sum(1 for g in grads if g is not None and g.abs().sum().item() > 0)
    model.zero_grad(set_to_none=True)
    return {"peak_gb": _peak_gb(device), "seconds": round(seconds, 2), "loss": float(loss.item()),
            "grads_finite": finite, "nonzero_grad_tensors": nonzero, "trainable_tensors": len(grads)}


def generation_probe(model, processor, rows, root, repeats, new_tokens, device):
    import torch
    from PIL import Image
    from transformers import GenerationConfig

    from src.training.protocol_v3 import eval_messages

    tokenizer = processor.tokenizer
    side = tokenizer.padding_side
    tokenizer.padding_side = "left"
    try:
        selected = [r for r in rows for _ in range(repeats)]
        images = [Image.open(Path(root) / r["image_path"]).convert("RGB") for r in selected]
        texts = [processor.apply_chat_template(eval_messages(r["problem"]), tokenize=False, add_generation_prompt=True)
                 for r in selected]
        inputs = processor(text=texts, images=images, padding=True, return_tensors="pt").to(device)
    finally:
        tokenizer.padding_side = side
    config = GenerationConfig(max_new_tokens=new_tokens, min_new_tokens=new_tokens, do_sample=True, temperature=1.0,
                              top_p=1.0, top_k=0, repetition_penalty=1.0, pad_token_id=tokenizer.pad_token_id,
                              suppress_tokens=[int(model.config.image_token_id)], disable_compile=True)
    was_checkpointing = getattr(model, "is_gradient_checkpointing", False)
    if was_checkpointing:
        model.gradient_checkpointing_disable()
    model.eval()
    _reset(device)
    started = time.time()
    with torch.no_grad():
        output = model.generate(**inputs, generation_config=config)
    _sync(device)
    seconds = time.time() - started
    if was_checkpointing:
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    generated = int(output.shape[1] - inputs["input_ids"].shape[1])
    return {"sequences": len(selected), "new_tokens": generated, "seconds": round(seconds, 2),
            "tokens_per_second": round(len(selected) * generated / seconds, 1), "peak_gb": _peak_gb(device),
            "prompt_width": int(inputs["input_ids"].shape[1])}


def vit_probe(model, processor, rows, root, completion_len, device, repeats=3):
    import torch

    from src.training.vision_cache import FrozenVisionCache, _inner_vl_model

    inner = _inner_vl_model(model)
    batch, completion, _ = build_batch(processor, rows, root, completion_len, device)
    model.eval()
    with torch.no_grad():
        times = []
        for _ in range(repeats):
            _sync(device)
            t = time.time()
            batched = inner.get_image_features(batch["pixel_values"], batch["image_grid_thw"]).pooler_output
            _sync(device)
            times.append(time.time() - t)
        vit = statistics.median(times)
        times = []
        for _ in range(repeats):
            _sync(device)
            t = time.time()
            reference = completion_logps(model, batch, completion, completion_len).float()
            _sync(device)
            times.append(time.time() - t)
        forward = statistics.median(times)
        sizes = batch["image_grid_thw"].prod(-1).tolist()
        chunks = torch.split(batch["pixel_values"], sizes)
        singles = [inner.get_image_features(chunk, batch["image_grid_thw"][i:i + 1]).pooler_output[0]
                   for i, chunk in enumerate(chunks)]
        image_diff = max(float((a.float() - b.float()).abs().max()) for a, b in zip(batched, singles))
        # a max-abs gap alone cannot tell bf16 rounding on large activations from a real batching difference
        image_rel = max(float((a.float() - b.float()).norm() / b.float().norm().clamp_min(1e-12))
                        for a, b in zip(batched, singles))
        image_scale = max(float(b.float().abs().max()) for b in singles)
        cache = FrozenVisionCache(model)
        try:
            for i, chunk in enumerate(chunks):  # fill the cache image by image, as reuse across batches would
                cache.get_image_features(chunk, batch["image_grid_thw"][i:i + 1])
            cached = completion_logps(model, batch, completion, completion_len).float()
        finally:
            cache.remove()
        logp_diff = float((cached - reference).abs().max())
        logp_mean = float((cached - reference).abs().mean())
    return {"vit_seconds": round(vit, 4), "forward_seconds": round(forward, 4), "vit_fraction_of_forward": round(vit / forward, 4),
            "batched_vs_single_image_max_abs_diff": image_diff, "batched_vs_single_image_max_rel_diff": round(image_rel, 6),
            "image_feature_max_abs": round(image_scale, 2), "cache_logprob_max_abs_diff": logp_diff,
            "cache_logprob_mean_abs_diff": round(logp_mean, 6),
            "equivalent": logp_diff <= 0.02, "cache_hits": cache.hits, "cache_misses": cache.misses}


def probe(model, processor, train_rows, val_rows, root, completion_len=1024, micro_sizes=(8, 4, 2), gen_rows=8,
          gen_repeats=8, prompt_budget=1600, lora=(16, 32)):
    import torch

    from src.training.lora_language import attach_language_lora

    device = next(model.parameters()).device
    report = {"completion_len": completion_len}
    lengths = prompt_lengths(processor, train_rows, root)
    val_lengths = prompt_lengths(processor, val_rows, root) if val_rows else {}
    report["prompt_tokens"] = {"budget": prompt_budget, "train": _stats(list(lengths.values())),
                               "train_over_budget": sorted(k for k, v in lengths.items() if v > prompt_budget),
                               "validation": _stats(list(val_lengths.values())) if val_lengths else None,
                               "validation_over_budget": sorted(k for k, v in val_lengths.items() if v > prompt_budget)}
    longest = sorted(train_rows, key=lambda r: -lengths[r["sample_id"]])
    peft_model, targets, identity = attach_language_lora(model, *lora)
    report["parameters"] = {k: v for k, v in identity.items() if k != "trainable_names"}
    report["parameters"]["lora_target_modules"] = len(targets)
    peft_model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    peft_model.enable_input_require_grads()
    report["micro_batch"] = {}
    for size in micro_sizes:
        try:
            report["micro_batch"][str(size)] = fwd_bwd(peft_model, processor, longest[:size], root, completion_len, device)
        except torch.OutOfMemoryError as exc:
            report["micro_batch"][str(size)] = {"oom": True, "error": str(exc)[:300]}
            peft_model.zero_grad(set_to_none=True)
            _reset(device)
    try:
        report["generation"] = generation_probe(peft_model, processor, longest[:gen_rows], root, gen_repeats,
                                                completion_len, device)
    except torch.OutOfMemoryError as exc:
        report["generation"] = {"oom": True, "error": str(exc)[:300]}
        _reset(device)
    report["vit"] = vit_probe(peft_model, processor, longest[:min(gen_rows, len(longest))], root, completion_len, device)
    if device.type == "cuda":
        props = torch.cuda.get_device_properties(0)
        report["gpu"] = {"name": props.name, "total_gb": round(props.total_memory / 1e9, 2)}
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--experiment", default=str(ROOT / "configs/experiments/rl_v3.json"))
    args = parser.parse_args(argv)
    import torch
    from transformers import AutoProcessor

    from src.data.approved_training_inputs import load_approved
    from src.training.hf_compat import vision_model_class

    config = json.loads(Path(args.experiment).read_text(encoding="utf-8"))
    m, t = config["model"], config["train"]
    manifest = ROOT / config["data"]["manifest"]
    release = json.loads(manifest.read_text(encoding="utf-8"))
    train_rows = load_approved(manifest, config["data"]["train_file"])
    val_rows = []
    for name in release.get("approved_evaluation_files", []):
        val_rows += [json.loads(x) for x in (manifest.parent / name).read_text(encoding="utf-8").splitlines() if x.strip()]
    started = time.time()
    processor = AutoProcessor.from_pretrained(args.model_path, max_pixels=m["max_pixels"], min_pixels=m["min_pixels"])
    model = vision_model_class().from_pretrained(args.model_path, dtype=torch.bfloat16,
                                                 attn_implementation=m["attn_implementation"]).to("cuda")
    load_seconds = time.time() - started
    report = probe(model, processor, train_rows, val_rows, ROOT, completion_len=t["max_completion_length"],
                   prompt_budget=t["max_prompt_tokens"], lora=(config["lora"]["r"], config["lora"]["alpha"]))
    report["load_seconds"] = round(load_seconds, 1)
    report["total_seconds"] = round(time.time() - started, 1)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["prompt_tokens", "micro_batch", "generation", "vit"] if k in report},
                     default=str)[:3000])


if __name__ == "__main__":
    main()
