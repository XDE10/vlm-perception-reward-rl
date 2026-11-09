"""Answer extraction, presentation-only normalisation and a persistent verifier.

The verifier keeps the project's strict typed gate
(``scripts/training/math_verify_v3_strict_worker.check``) but runs it in a
persistent ``spawn`` process pool, so a hung or crashing Math-Verify call is
isolated and timed out without paying a Python start-up per completion (the
legacy entry spawned one subprocess per call). Normalisation only removes
presentation (``x = 4`` -> ``4``, trailing units, ``$`` wrappers); it never
changes a value, and no numeric tolerance is added for training (D4).
"""
import concurrent.futures as cf
import multiprocessing as mp
import re

VERSION = "answer-verifier-v1-20261109"
_ASSIGN = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*([^=]+)$")
_UNITS = re.compile(
    r"(?:\s*(?:\\,|\\ |~)?\s*(?:\\text\{\s*)?(?:cm|mm|km|m|in\.?|inch(?:es)?|ft|feet|yd|yards?|units?|"
    r"square\s+(?:units?|cm|m|in(?:ches)?|ft|feet)|sq\.?\s*(?:units?|cm|m|in|ft)|degrees?|deg)\s*\}?"
    r"(?:\s*\^\s*\{?\s*[23]\s*\}?|[²³])?)$",
    re.I,
)
_DEGREE = re.compile(r"(?:\s*\^\s*\{?\s*\\circ\s*\}?|\s*°|\s*\\degree)$")


def normalize_answer(text):
    s = (text or "").strip()
    for _ in range(3):
        s = s.strip().rstrip(".").strip()
        if s.startswith("$") and s.endswith("$") and len(s) > 1:
            s = s.strip("$").strip()
        if s.startswith(r"\(") and s.endswith(r"\)"):
            s = s[2:-2].strip()
        if s.startswith(r"\approx") or s.startswith("≈"):
            s = s.removeprefix(r"\approx").removeprefix("≈").strip()
        match = _ASSIGN.match(s)
        if match:
            s = match.group(2).strip()
        s = _DEGREE.sub("", s).strip()
        s = _UNITS.sub("", s).strip()
    return s


def _wrap(answer):
    return answer if r"\boxed" in answer else r"\boxed{" + answer + "}"


def _check(payload):
    try:
        from scripts.training.math_verify_v3_strict_worker import check

        return check(payload)
    except Exception as exc:  # parse errors are reported, never raised into the trainer
        return {"correct": False, "status": str(exc)[:120] or type(exc).__name__, "error_type": type(exc).__name__}


def _warm():
    import math_verify  # noqa: F401


class AnswerVerifier:
    """Process-isolated Math-Verify with per-call timeout and automatic pool restart."""

    def __init__(self, workers=4, timeout=10.0):
        self.workers, self.timeout = workers, timeout
        self._pool = None
        self.restarts = 0

    def _ensure(self):
        if self._pool is None:
            self._pool = cf.ProcessPoolExecutor(max_workers=self.workers, mp_context=mp.get_context("spawn"),
                                                initializer=_warm)
        return self._pool

    def _restart(self):
        if self._pool is not None:
            self._pool.shutdown(wait=False, cancel_futures=True)
        self._pool = None
        self.restarts += 1

    def verify_many(self, answers, references):
        if len(answers) != len(references):
            raise ValueError("answers/references length mismatch")
        results = [None] * len(answers)
        pending = []
        pool = self._ensure()
        for i, (answer, reference) in enumerate(zip(answers, references)):
            if answer is None or not str(answer).strip():
                results[i] = {"correct": False, "status": "no_answer"}
                continue
            normalized = normalize_answer(str(answer))
            payload = {"output": _wrap(normalized), "reference": str(reference)}
            pending.append((i, normalized, pool.submit(_check, payload)))
        broken = False
        for i, normalized, future in pending:
            try:
                result = future.result(timeout=self.timeout)
            except cf.TimeoutError:
                result, broken = {"correct": False, "status": "verifier_timeout"}, True
            except cf.process.BrokenProcessPool:
                result, broken = {"correct": False, "status": "verifier_crashed"}, True
            result = dict(result)
            result["normalized_answer"] = normalized
            result["verifier"] = VERSION
            results[i] = result
        if broken:
            self._restart()
        return results

    def close(self):
        if self._pool is not None:
            self._pool.shutdown(wait=True, cancel_futures=True)
            self._pool = None


__all__ = ["AnswerVerifier", "VERSION", "normalize_answer"]
