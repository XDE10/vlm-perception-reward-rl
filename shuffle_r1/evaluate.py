"""Generate eight fresh samples per question from the pinned Shuffle-R1 evaluation inputs."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
from types import SimpleNamespace
import zipfile

from run import restore_source


def sha(data):
    return hashlib.sha256(data).hexdigest()


def payload_key(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


EXPECTED_SH="c68d48dffdf1085428be137565b0207c21035a59304987e30b498b208afe9918"
EXPECTED_LOADER="6d1169541bd7dee80924b9a09566c3b73e9aec04415fc7d887a3d197e0706662"
COUNTS=dict(mathverse=3940,mathvision=3040,mathvista=1000,wemath=1740,hallubench=951,chartqa=2500)
PINNED_DATA="476ee7d0d3919299eeeca135548a13440bc0751c"


ARCHIVE_SHA="0d6ba711f1ba15ba9ed4c4862458d151dcf4726fdc8a326a34cfa1e333268ac8"
ARCHIVE_BYTES=2430433618
SUITE_FOLDER={key:("ChartQA_test" if key=="chartqa" else key) for key in COUNTS}


def file_digest(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()

def verify_dataset_archive(path,data,suites):
    """Bind exact pinned ZIP and selected extracted trees, refuse stale/additional files."""
    if not path.is_file() or path.stat().st_size!=ARCHIVE_BYTES or file_digest(path)!=ARCHIVE_SHA:
        raise ValueError("incorrect/missing pinned MM_Eval archive")
    data=data.resolve()
    suite_roots={SUITE_FOLDER[s]:s for s in suites}
    indices={s:{} for s in suites}
    prefixes=set()
    with zipfile.ZipFile(path) as z:
        for item in z.infolist():
            name=PurePosixPath(item.filename)
            if item.is_dir() or "__MACOSX" in name.parts:
                continue
            selected=[i for i,piece in enumerate(name.parts) if piece in suite_roots]
            if not selected:
                continue
            start=selected[0]
            if name.is_absolute() or ".." in name.parts or "\\" in item.filename:
                raise ValueError(f"invalid archive entry {name}")
            archive_root=name.parts[start]
            key=suite_roots[archive_root]
            relative=PurePosixPath(*name.parts[start:]).as_posix()
            prefixes.add(tuple(name.parts[:start]))
            if relative in indices[key]:
                raise ValueError(f"duplicate file in pinned suite: {relative}")
            indices[key][relative]=item
        if len(prefixes)!=1 or any(not rows for rows in indices.values()):
            raise ValueError("could not resolve one verified archive data root")
        receipts={}
        for folder,suite in sorted(suite_roots.items()):
            files=indices[suite]
            top=data/folder
            if not top.is_dir() or top.is_symlink():
                raise ValueError(f"missing or symlinked extracted suite directory {folder}")
            actual=set()
            for p in top.rglob("*"):
                if p.is_symlink():
                    raise ValueError(f"symlinked data entry {p}")
                if p.is_file():
                    actual.add(p.relative_to(data).as_posix())
            if set(files)!=actual:
                raise ValueError(f"staged {suite} file list differs from frozen ZIP: missing {len(set(files)-actual)}, extra {len(actual-set(files))}")
            manifest=[]
            for rel,item in sorted(files.items()):
                local=data/rel
                if local.stat().st_size!=item.file_size:
                    raise ValueError(f"staged data length mismatch {rel}")
                with z.open(item) as entry:
                    wanted=hashlib.file_digest(entry,"sha256").hexdigest()
                if file_digest(local)!=wanted:
                    raise ValueError(f"staged data differs bytewise from frozen ZIP: {rel}")
                manifest.append({"path":rel,"bytes":item.file_size,"sha256":wanted})
            receipts[suite]={"member_count":len(manifest),"tree_sha256":payload_key(manifest)}
    return {"archive_sha256":ARCHIVE_SHA,"archive_bytes":ARCHIVE_BYTES,"suite_trees":receipts}

def decoded_fingerprint(image):
    rgb=image.convert("RGB")
    return sha((f"RGB:{rgb.width}x{rgb.height}\n").encode()+rgb.tobytes())


def system_prompt(script):
    text=script.decode()
    expect=r'^SYSTEM_PROMPT="""(.*?)"""$'
    matches=re.findall(expect,text,re.M|re.S)
    if len(matches)!=1:
        raise ValueError("failed to bind actual paper eval.sh system prompt")
    return matches[0]

def check_official(source):
    exact={source/"utils"/"data_loaders.py":EXPECTED_LOADER, source/"eval.sh":EXPECTED_SH}
    for p,expected in exact.items():
        if sha(p.read_bytes())!=expected:
            raise ValueError(f"upstream source digest mismatch: {p}")
    return system_prompt((source/"eval.sh").read_bytes())


def load_parquet(path, split):
    import datasets
    paths=sorted(path.rglob("*.parquet"))
    explicit=[str(p) for p in paths if split in p.name or split in p.relative_to(path).parts[:-1]]
    if explicit:
        return datasets.load_dataset("parquet",data_files={split:explicit},split=split)
    if split=="test" and path.name=="ChartQA_test" and paths:
        return datasets.load_dataset("parquet",data_files={split:[str(x) for x in paths]},split=split)
    return datasets.load_dataset(str(path),split=split)


def bind_runtime(model):
    from importlib.metadata import version
    import inspect
    import vllm
    from vllm import LLM, SamplingParams
    from vllm.v1.engine.parallel_sampling import ParentRequest
    if vllm.__version__!="0.9.2" or not re.search(r"\.seed\s*=\s*seed\s*\+\s*index",inspect.getsource(ParentRequest._get_child_sampling_params)):
        raise RuntimeError("vLLM 0.9.2 / V1 matching seeds are required")
    import torch
    if torch.cuda.device_count()!=1:
        raise RuntimeError("need exactly one dedicated GPU per process")
    began=time.perf_counter()
    llm=LLM(model=str(model),skip_tokenizer_init=False,tensor_parallel_size=1,dtype=torch.bfloat16,
            gpu_memory_utilization=.88,enforce_eager=True,max_model_len=8192,max_num_batched_tokens=8192,
            disable_custom_all_reduce=True,enable_prefix_caching=True,
            max_num_seqs=128, limit_mm_per_prompt={"image":1})
    if ".v1." not in type(llm.llm_engine).__module__:
        raise RuntimeError("vLLM V1 not active")
    metadata={"engine_seconds":time.perf_counter()-began,"gpu":torch.cuda.get_device_name(0),
              "versions":{k:version(k) for k in ("vllm","torch","transformers","Pillow","pandas","datasets")}}
    return llm,SamplingParams,metadata

def load_inputs(source, data, suite):
    from evaluation_prompts import prepare_prompts

    prompt = check_official(source)
    opts = SimpleNamespace(system_prompt=prompt, min_pixels=262144, max_pixels=4194304)
    loader_spec = importlib.util.spec_from_file_location("pinned_shuffle_loader", source / "utils" / "data_loaders.py")
    loader = importlib.util.module_from_spec(loader_spec)
    loader_spec.loader.exec_module(loader)
    loader.load_dataset = lambda path, split: load_parquet(Path(path), split)

    if suite == "chartqa":
        dataset = load_parquet(data / SUITE_FOLDER[suite], "test")
        items = (dict(id=f"chartqa_{i}", image_path=item["image"], question=item["question"],
                      answer=item["answer"], problem_version=item["type"]) for i, item in enumerate(dataset))
    else:
        dataset = getattr(loader, "load_" + suite + "_dataset")(str(data))
        items = iter(dataset)
    if len(dataset) != COUNTS[suite]:
        raise ValueError(f"Expected {COUNTS[suite]} questions in {suite}, got {len(dataset)}")

    if suite == "hallubench":
        path = data / "hallubench" / "HallusionBench.json"
        official = (row for row in json.loads(path.read_text(encoding="utf-8")) if row["filename"])
        items = (dict(item, id=json.dumps(
            [str(row[key]) for key in ("category", "subcategory", "set_id", "figure_id", "question_id")],
            separators=(",", ":"),
        )) for item, row in zip(items, official, strict=True))

    def convert(item):
        prompts, _ = prepare_prompts(suite, [item], opts)
        if len(prompts) != 1:
            raise ValueError(f"Could not load image for {suite}/{item['id']}")
        return item, prompts[0]

    return items, convert


def generate(args, items, convert):
    from itertools import islice

    llm, sampling_type, runtime = bind_runtime(args.model)
    seen = set()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    pending = args.out.with_name(args.out.name + ".partial")
    with pending.open("x", encoding="utf-8", newline="\n") as stream:
        while batch := list(islice(items, args.batch_questions)):
            prepared = [convert(item) for item in batch]
            samples = [sampling_type(n=8, seed=0, max_tokens=2048, temperature=0.5) for _ in prepared]
            responses = llm.generate([prompt for _, prompt in prepared], samples, use_tqdm=False)
            for (item, prompt), response in zip(prepared, responses, strict=True):
                key = str(item["id"])
                if key in seen or sorted(result.index for result in response.outputs) != list(range(8)):
                    raise RuntimeError(f"Duplicate ID or incomplete seeds for {args.suite}/{key}")
                seen.add(key)
                image_hash = decoded_fingerprint(prompt["multi_modal_data"]["image"])
                prompt_hash = sha(prompt["prompt"].encode())
                for result in sorted(response.outputs, key=lambda result: result.index):
                    if not result.finished() or result.token_ids is None:
                        raise RuntimeError(f"Unfinished completion for {args.suite}/{key}/{result.index}")
                    record = {"dataset": args.suite, "id": key, "seed": result.index,
                              "question_for_eval": item.get("question_for_eval", item["question"]),
                              "reference_answer": str(item["answer"]), "problem_version": item.get("problem_version"),
                              "prompt_sha256": prompt_hash, "image_sha256": image_hash,
                              "response": result.text, "response_sha256": sha(result.text.encode()),
                              "finish": result.finish_reason, "generated_tokens": len(result.token_ids)}
                    stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            stream.flush()
    if len(seen) != args.stop - args.start:
        raise RuntimeError("Unexpected number of generated questions")
    os.link(pending, args.out)
    pending.unlink()
    print(json.dumps({"questions": len(seen), "answers": 8 * len(seen), "runtime": runtime}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True, help="directory containing the extracted suite folders")
    parser.add_argument("--dataset-archive", type=Path, required=True, help="the pinned MM_Eval.zip")
    parser.add_argument("--suite", choices=COUNTS, required=True)
    parser.add_argument("--model", type=Path, help="local Hugging Face model export")
    parser.add_argument("--out", type=Path, help="new output JSONL")
    parser.add_argument("--batch-questions", type=int, default=4, choices=(2, 4, 8, 12, 16))
    parser.add_argument("--start", type=int, default=0, help="zero-based question offset")
    parser.add_argument("--stop", type=int, help="exclusive question offset")
    parser.add_argument("--check-only", action="store_true", help="verify sources and read prompts without a GPU")
    args = parser.parse_args()
    stop = args.stop if args.stop is not None else COUNTS[args.suite]
    if not 0 <= args.start < stop <= COUNTS[args.suite]:
        parser.error("expected 0 <= start < stop <= suite size")
    if not args.check_only and (args.model is None or not args.model.is_dir() or args.out is None or args.out.exists()):
        parser.error("generation requires a local --model and a new --out file")

    args.stop = stop

    from itertools import islice

    os.environ.update(HF_HUB_OFFLINE="1", HF_DATASETS_OFFLINE="1", TRANSFORMERS_OFFLINE="1",
                      VLLM_USE_V1="1", VLLM_ENABLE_V1_MULTIPROCESSING="0",
                      VLLM_ATTENTION_BACKEND="FLASH_ATTN", VLLM_USE_FLASHINFER_SAMPLER="0",
                      FLASH_ATTENTION_DETERMINISTIC="1", CUBLAS_WORKSPACE_CONFIG=":4096:8")
    source = restore_source(args.work_dir.resolve()) / "evaluation"
    data = args.data.resolve()
    proof = verify_dataset_archive(args.dataset_archive, data, (args.suite,))
    items, convert = load_inputs(source, data, args.suite)
    items = islice(items, args.start, stop)
    if args.check_only:
        keys = Counter(str(convert(item)[0]["id"]) for item in items)
        if len(keys) != stop - args.start or any(count != 1 for count in keys.values()):
            raise ValueError("Suite contains missing or duplicate inputs")
        print(json.dumps({"questions": len(keys), "dataset_proof": proof}))
    else:
        generate(args, items, convert)


if __name__ == "__main__":
    main()
