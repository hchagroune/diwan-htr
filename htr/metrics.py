"""Character / word error rates."""
from __future__ import annotations

from rapidfuzz.distance import Levenshtein

from .textnorm import normalize


def cer(reference: str, hypothesis: str, mode: str = "strict") -> float:
    ref, hyp = normalize(reference, mode), normalize(hypothesis, mode)
    if not ref:
        return 0.0 if not hyp else 1.0
    return Levenshtein.distance(ref, hyp) / len(ref)


def wer(reference: str, hypothesis: str, mode: str = "strict") -> float:
    ref, hyp = normalize(reference, mode).split(), normalize(hypothesis, mode).split()
    if not ref:
        return 0.0 if not hyp else 1.0
    return Levenshtein.distance(ref, hyp) / len(ref)


def similarity(a: str, b: str) -> float:
    """1 - CER, symmetric-ish, clipped to [0, 1]."""
    if not a and not b:
        return 1.0
    longest = max(len(normalize(a)), len(normalize(b)), 1)
    return max(0.0, 1.0 - Levenshtein.distance(normalize(a), normalize(b)) / longest)
