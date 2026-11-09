"""Shared prompt and output protocol v3: perception -> think -> answer.

Every arm (and every evaluation of every model, including V0) uses exactly
these messages. Training rows keep string contents so TRL can insert the image
placeholder; evaluation builds the structured form directly. A test asserts both
render to the same chat-template text.
"""
import re

from src.rewards.claims import extract_block, parse_block

PROTOCOL = "perception-think-answer-v3-20261109"
MAX_CLAIMS = 24
SYSTEM_PROMPT = (
    "You solve geometry problems from a diagram. Respond in exactly three parts and nothing else:\n"
    "<perception>facts you can read directly in the diagram, separated by semicolons</perception>\n"
    "<think>step-by-step reasoning</think>\n"
    "<answer>final answer only</answer>\n\n"
    "Write perception facts with the printed point labels in this syntax: "
    "Length(A,B)=5; Angle(A,B,C)=60 deg; Parallel((A,B),(C,D)); Perpendicular((A,B),(C,D)); "
    "PointLiesOnLine(C,(A,B)); PointLiesOnCircle(A,Circle(O)); CongruentLength((A,B),(C,D)).\n"
    "Put the vertex in the middle of Angle(...), write angle values with \" deg\", copy printed values "
    "exactly (for example x+3), and list at most 24 facts. Include only facts shown in the diagram, "
    "not facts stated in the question or obtained by calculation.\n"
    "The answer must be a single number or expression, without units and without \"x =\"."
)
# Prompt variants pre-registered in docs/plan/S3设计_20261109.md section 6. "p0" is the protocol every run so far used.
# "p1" adds one fixed sentence at the end of the user turn; S3 adopts it only if the train-only rule says so, and then
# for every arm and every evaluation. "answer_only" is a diagnostic (how much the three-part protocol costs V0); it is
# never used for training or for an endpoint.
P1_SUFFIX = "Respond in the format <perception>...</perception><think>...</think><answer>...</answer>."
ANSWER_ONLY_SYSTEM_PROMPT = (
    "You solve geometry problems from a diagram. Think step by step, then give the final answer inside "
    "<answer></answer>. The answer must be a single number or expression, without units and without \"x =\"."
)
PROMPT_VARIANTS = ("p0", "p1", "answer_only")
PROTOCOL_IDS = {"p0": PROTOCOL, "p1": "perception-think-answer-v3-p1-20261109",
                "answer_only": "answer-only-diagnostic-20261109"}
_SECTION = re.compile(r"\s*<perception>(.*?)</perception>\s*<think>(.*?)</think>\s*<answer>(.*?)</answer>\s*", re.S)
_TAG = re.compile(r"</?(?:perception|think|answer)>")
_ANSWER = re.compile(r"<answer>(.*?)</answer>", re.S)


def clean_problem(problem):
    return str(problem).removeprefix("<image>").strip()


def _check_variant(variant):
    if variant not in PROMPT_VARIANTS:
        raise ValueError("unknown prompt variant %r; known: %s" % (variant, ", ".join(PROMPT_VARIANTS)))


def system_prompt(variant="p0"):
    _check_variant(variant)
    return ANSWER_ONLY_SYSTEM_PROMPT if variant == "answer_only" else SYSTEM_PROMPT


def user_text(problem, variant="p0"):
    _check_variant(variant)
    text = clean_problem(problem)
    return text + "\n\n" + P1_SUFFIX if variant == "p1" else text


def protocol_id(variant="p0"):
    _check_variant(variant)
    return PROTOCOL_IDS[variant]


def training_prompt(problem, variant="p0"):
    """Conversational prompt with string contents; TRL adds the image block (if any)."""
    if variant == "answer_only":
        raise ValueError("the answer-only prompt is a diagnostic and is never used for training")
    return [{"role": "system", "content": system_prompt(variant)}, {"role": "user", "content": user_text(problem, variant)}]


def eval_messages(problem, with_image=True, variant="p0"):
    user = ([{"type": "image"}] if with_image else []) + [{"type": "text", "text": user_text(problem, variant)}]
    return [{"role": "system", "content": [{"type": "text", "text": system_prompt(variant)}]},
            {"role": "user", "content": user}]


def extract_answer(text):
    matches = _ANSWER.findall(text)
    if len(matches) != 1 or text.count("<answer>") != 1 or text.count("</answer>") != 1:
        return None, ("no_answer_block" if not matches else "multiple_answer_blocks")
    answer = matches[0].strip()
    return (answer, "ok") if answer else (None, "empty_answer")


def parse_completion(text):
    match = _SECTION.fullmatch(text)
    nested = bool(match) and any(_TAG.search(part) for part in match.groups())
    answer, answer_status = extract_answer(text)
    return {
        "protocol_ok": bool(match) and not nested,
        "perception": match.group(1) if match else None,
        "think": match.group(2) if match else None,
        "answer": answer,
        "answer_status": answer_status,
    }


def format_reward(text, max_claims=MAX_CLAIMS):
    parsed = parse_completion(text)
    if not parsed["protocol_ok"] or parsed["answer"] is None:
        return 0.0
    block, status = extract_block(text)
    if status != "ok":
        return 0.0
    claims, info = parse_block(block, max_claims)
    if info["over_cap"] or not any(c.valid for c in claims):
        return 0.0
    return 1.0


__all__ = ["ANSWER_ONLY_SYSTEM_PROMPT", "MAX_CLAIMS", "P1_SUFFIX", "PROMPT_VARIANTS", "PROTOCOL", "PROTOCOL_IDS",
           "SYSTEM_PROMPT", "clean_problem", "eval_messages", "extract_answer", "format_reward", "parse_completion",
           "protocol_id", "system_prompt", "training_prompt", "user_text"]
