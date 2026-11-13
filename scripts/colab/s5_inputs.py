"""Pinned S5 inputs and secondary diagnostics. No held-out generations here."""
import ast
import io
import json
import re
from pathlib import Path

from scripts.colab import eval_inputs
from src.evaluation.harness import cfgeo_items, val82_items, wrapper_items
from src.evaluation.public_sources import WRAPPER, image_pixel_sha256

ROOT = Path(__file__).resolve().parents[2]
MATHVISTA = "mathvista/data/testmini-00000-of-00001-725687bf7a18d64b.parquet"
SOURCES = [WRAPPER["validation"], WRAPPER["test"], MATHVISTA]
ERRATA = {"validation:165", "validation:179"}


def mathvista_items(sources):
    import pyarrow.parquet as pq
    from PIL import Image

    columns = ["pid", "question", "decoded_image", "choices", "unit", "answer", "answer_type", "metadata"]
    out, gps, no_geometry3k = [], set(), set()
    for batch in pq.ParquetFile(Path(sources) / MATHVISTA).iter_batches(columns=columns):
        for row in batch.to_pylist():
            image = Image.open(io.BytesIO(row["decoded_image"]["bytes"])).convert("RGB")
            item_id = "mathvista:" + row["pid"]
            problem, choices = row["question"], row["choices"]
            if choices:
                labels = "\n".join(f"{chr(65 + i)}. {choice}" for i, choice in enumerate(choices))
                problem += "\n\n" + labels + "\nGive the letter of the correct choice."
            elif row["unit"]:
                problem += f"\nExpress the answer in {row['unit']}."
            reference = json.dumps({"answer": row["answer"], "choices": choices, "type": row["answer_type"]})
            out.append({"id": item_id, "problem": problem, "answer": reference,
                        "image": image, "cluster": image_pixel_sha256(image)})
            if row["metadata"]["task"] == "geometry problem solving":
                gps.add(item_id)
            if "geometry3k" not in row["metadata"]["source"].casefold():
                no_geometry3k.add(item_id)
    if (len(out), len({item["id"] for item in out}), len(gps), len(no_geometry3k)) != (1000, 1000, 208, 938):
        raise ValueError("MathVista testmini and its registered subsets have unexpected counts")
    return out, gps, no_geometry3k


class MathVistaVerifier:
    """Project answer block extraction, exact options/lists, and the strict numeric verifier."""

    def __init__(self, numeric):
        self.numeric = numeric

    def verify_many(self, answers, references):
        result, pending = [None] * len(answers), []
        for i, (answer, reference) in enumerate(zip(answers, references, strict=True)):
            ref = json.loads(reference)
            if answer is None:
                result[i] = {"correct": False, "status": "no_answer"}
                continue
            answer = answer.strip()
            if ref["choices"]:
                options = ref["choices"]
                label = re.fullmatch(r"\(?([A-Z])\)?[.]?", answer)
                if label and ord(label[1]) - 65 < len(options):
                    answer = options[ord(label[1]) - 65]
                correct = answer.casefold() == ref["answer"].strip().casefold()
                result[i] = {"correct": correct, "status": "choice_exact", "normalized_answer": answer}
            elif ref["type"] == "list":
                try:
                    prediction, target = ast.literal_eval(answer), ast.literal_eval(ref["answer"])
                    correct = isinstance(prediction, (list, tuple)) and list(prediction) == list(target)
                except (ValueError, SyntaxError, TypeError):
                    correct = False
                result[i] = {"correct": correct, "status": "list_exact", "normalized_answer": answer}
            else:
                pending.append((i, answer, ref["answer"]))
        if pending:
            indices, predictions, targets = zip(*pending)
            for i, verdict in zip(indices, self.numeric.verify_many(predictions, targets), strict=True):
                result[i] = verdict
        return result


def intergps_false(text, geometry, config):
    """Oracle-refuted fraction of valid distinct claims on matched original diagrams."""
    from src.rewards.claims import extract_block, parse_block
    from src.rewards.geometry_oracle import refute

    if geometry is None:
        return None
    block, status = extract_block(text)
    if status != "ok":
        return {"valid_claims": 0, "refuted": 0, "status": status}
    claims, info = parse_block(block, config.max_claims)
    if info["over_cap"]:
        return {"valid_claims": 0, "refuted": 0, "status": "over_cap"}
    valid = [c for c in claims if c.valid]
    return {"valid_claims": len(valid), "refuted": sum(bool(refute(c, geometry, config.oracle)) for c in valid),
            "status": "ok"}


def build(sources, config, out):
    from src.data.intergps_index import load_index

    check = eval_inputs.eval_sets(sources, out / "eval_sets_check.json")
    if not check["ok"]:
        raise ValueError("pinned evaluation inputs differ from the S3 specification")
    spec = json.loads(eval_inputs.SPEC.read_text(encoding="utf-8"))
    val, test = val82_items(ROOT, config), wrapper_items(sources, "test")
    cf = cfgeo_items(eval_inputs.CFGEO[0], sources)
    mathvista, gps, no_geometry3k = mathvista_items(sources)
    if len(val) != 82 or not ERRATA <= {item["id"] for item in val}:
        raise ValueError("val82 does not contain the expected approved rows")
    if len(cf) != 158 or [r["id"] for r in spec["test601"]] != [item["id"] for item in test]:
        raise ValueError("CF-Geo or test601 differs from the registered evaluation inputs")
    originals = {r["id"]: r["original_id"] for r in spec["test601"] if r["join"] == "matched"}
    index = load_index(eval_inputs.ANNOTATIONS, originals.values())
    geometry = {item["id"]: index[originals[item["id"]]] for item in test if item["id"] in originals}
    test_by_id = {item["id"]: item for item in test}
    visual = [test_by_id[item_id] for item_id in spec["test_vn"]]
    cases = {"val82": (val, "original"), "test_vn": (visual, "original"), "test_original": (test, "original"),
             "test_blind": (test, "blind"),
             "test_swap": (test, "swap"), "cf_original": (cf, "original"), "cf_k1": (cf, "cf_k1"),
             "cf_k2": (cf, "cf_k2"), "mathvista": (mathvista, "original")}
    subsets = {
        "val82_without_errata": ("val82", {item["id"] for item in val} - ERRATA),
        "cf_k2_exact": ("cf_k2", {item["id"] for item in cf if item["cf"]["places"] is None}),
        "mathvista_gps": ("mathvista", gps),
        "mathvista_without_geometry3k": ("mathvista", no_geometry3k),
    }
    return cases, subsets, spec["swap"], geometry
