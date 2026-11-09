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
_SECTION = re.compile(r"\s*<perception>(.*?)</perception>\s*<think>(.*?)</think>\s*<answer>(.*?)</answer>\s*", re.S)
_TAG = re.compile(r"</?(?:perception|think|answer)>")
_ANSWER = re.compile(r"<answer>(.*?)</answer>", re.S)


def clean_problem(problem):
    return str(problem).removeprefix("<image>").strip()


def training_prompt(problem):
    """Conversational prompt with string contents; TRL adds the image block (if any)."""
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": clean_problem(problem)}]


def eval_messages(problem, with_image=True):
    user = ([{"type": "image"}] if with_image else []) + [{"type": "text", "text": clean_problem(problem)}]
    return [{"role": "system", "content": [{"type": "text", "text": SYSTEM_PROMPT}]}, {"role": "user", "content": user}]


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


__all__ = ["MAX_CLAIMS", "PROTOCOL", "SYSTEM_PROMPT", "clean_problem", "eval_messages", "extract_answer",
           "format_reward", "parse_completion", "training_prompt"]
