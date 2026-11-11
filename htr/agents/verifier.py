"""Verification agent: rule checks + self-consistency + model critic -> confidence and flags."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field

from rapidfuzz import fuzz

from ..metrics import similarity
from ..textnorm import LATIN_CHAR, arabic_ratio


@dataclass
class Flag:
    code: str
    message: str
    severity: str = "soft"          # soft | hard
    line: int | None = None         # 1-based


@dataclass
class Verdict:
    confidence: float
    flags: list[Flag] = field(default_factory=list)
    line_scores: list[float] = field(default_factory=list)   # agreement per line (1 = all samples agree)
    critic: dict = field(default_factory=dict)

    @property
    def hard(self) -> bool:
        return any(f.severity == "hard" for f in self.flags)

    def to_json(self) -> dict:
        return {"confidence": self.confidence, "flags": [asdict(f) for f in self.flags],
                "line_scores": self.line_scores, "critic": self.critic}


# ---------------------------------------------------------------- rules
def rule_checks(text: str, length_range: tuple[int, int] | None = None) -> list[Flag]:
    flags: list[Flag] = []
    if not text.strip():
        return [Flag("empty", "The model returned no text.", "hard")]
    lines = [ln for ln in text.split("\n") if ln.strip()]
    if arabic_ratio(text) < 0.8:
        flags.append(Flag("not_arabic", "Less than 80% of letters are Arabic.", "hard"))
    for i, ln in enumerate(text.split("\n"), 1):
        if LATIN_CHAR.search(ln):
            flags.append(Flag("latin", "Latin letters: possible commentary or translation.", "soft", i))
        if any(tok in ln for tok in ("```", "**", "##")):
            flags.append(Flag("markdown", "Markdown formatting in the output.", "soft", i))
    # Generation loops: same line repeated many times is a classic VLM failure.
    for i in range(2, len(lines)):
        if lines[i] == lines[i - 1] == lines[i - 2]:
            flags.append(Flag("loop", "Same line repeated 3+ times (generation loop).", "hard"))
            break
    if len(lines) >= 8 and len(set(lines)) / len(lines) < 0.5:
        flags.append(Flag("repetitive", "More than half of the lines are duplicates.", "hard"))
    if length_range:
        lo, hi = length_range
        n = len(text)
        if n < lo * 0.5:
            flags.append(Flag("short", f"Much shorter than training pages ({n} chars).", "soft"))
        elif n > hi * 1.5:
            flags.append(Flag("long", f"Much longer than training pages ({n} chars).", "soft"))
    return flags


# ---------------------------------------------------- self-consistency
def consensus(samples: list[str]) -> tuple[str, float, list[float]]:
    """Pick the medoid sample; return it, overall agreement, and per-line agreement scores."""
    samples = [s for s in samples if s.strip()] or samples
    if len(samples) == 1:
        return samples[0], 1.0, [1.0] * len(samples[0].split("\n"))
    sims = [[similarity(a, b) if i != j else 1.0 for j, b in enumerate(samples)] for i, a in enumerate(samples)]
    best = max(range(len(samples)), key=lambda i: sum(sims[i]))
    draft = samples[best]
    others = [s for i, s in enumerate(samples) if i != best]
    agreement = sum(sims[best][j] for j in range(len(samples)) if j != best) / len(others)
    return draft, round(agreement, 3), line_agreement(draft, others)


def line_agreement(draft: str, others: list[str]) -> list[float]:
    """For each draft line, how closely the other samples reproduce it (0-1)."""
    scores = []
    for idx, line in enumerate(draft.split("\n")):
        if not line.strip() or not others:
            scores.append(1.0)
            continue
        per_other = []
        for other in others:
            olines = other.split("\n")
            window = olines[max(0, idx - 2): idx + 3] or olines  # tolerate a shifted line
            per_other.append(max((fuzz.ratio(line, o) for o in window), default=0) / 100)
        scores.append(round(sum(per_other) / len(per_other), 3))
    return scores


# ------------------------------------------------------------- critic
CRITIC_PROMPT = """You are verifying a diplomatic transcription of the attached Arabic manuscript page
(Maghrebi script, Algeria, 18th-19th c.). The transcription is given with line numbers.
Compare it with the image and report ONLY concrete problems:
 - misread words (give the line number, what is written, what you read instead),
 - omitted words or lines,
 - added text that is not on the page (commentary, translation, headings).
Do not report style, punctuation or spelling variants that match the manuscript.
Write "problem" and "suggestion" in {language}; quote Arabic words exactly.
confidence = your probability (0-1) that the transcription has no substantive error.

Transcription:
{numbered}"""

CRITIC_SCHEMA = {
    "type": "object",
    "properties": {
        "confidence": {"type": "number"},
        "issues": {"type": "array", "items": {"type": "object", "properties": {
            "line": {"type": "integer"},
            "problem": {"type": "string"},
            "suggestion": {"type": "string"},
        }, "required": ["line", "problem"]}},
    },
    "required": ["confidence", "issues"],
}


class GeminiCritic:
    def __init__(self, model: str, client=None, engine_cfg=None, language: str = "English"):
        if client is None:
            from ..engines.gemini import make_client

            client = make_client(engine_cfg)
        self.model, self.client, self.language = model, client, language

    def review(self, image: bytes, draft: str) -> dict:
        from google.genai import types

        from ..engines.gemini import call_with_retry

        numbered = "\n".join(f"{i}: {ln}" for i, ln in enumerate(draft.split("\n"), 1))
        config = types.GenerateContentConfig(response_mime_type="application/json",
                                             response_json_schema=CRITIC_SCHEMA,
                                             media_resolution="MEDIA_RESOLUTION_HIGH")
        resp = call_with_retry(lambda: self.client.models.generate_content(
            model=self.model, config=config,
            contents=[types.Part.from_bytes(data=image, mime_type="image/jpeg"),
                      CRITIC_PROMPT.format(numbered=numbered, language=self.language)]))
        try:
            data = json.loads(resp.text)
        except (TypeError, json.JSONDecodeError):
            return {"confidence": 0.5, "issues": [], "error": "critic returned invalid JSON"}
        data["confidence"] = float(min(1.0, max(0.0, data.get("confidence", 0.5))))
        return data


def critic_feedback(critic: dict) -> str:
    issues = critic.get("issues") or []
    return "\n".join(f"- line {i.get('line')}: {i.get('problem')}"
                     + (f" (suggestion: {i['suggestion']})" if i.get("suggestion") else "") for i in issues)


# ---------------------------------------------------------- combine
def combine(text: str, agreement: float, line_scores: list[float], critic: dict | None,
            length_range: tuple[int, int] | None = None, uncertain_below: float = 0.8) -> Verdict:
    flags = rule_checks(text, length_range)
    for i, score in enumerate(line_scores, 1):
        if score < uncertain_below:
            flags.append(Flag("uncertain_line", f"Samples disagree on this line ({score:.0%}).", "soft", i))
    for issue in (critic or {}).get("issues", []):
        flags.append(Flag("critic", issue.get("problem", ""), "soft", issue.get("line")))
    confidence = agreement
    if critic and "confidence" in critic:
        confidence = min(confidence, critic["confidence"])
    if any(f.severity == "hard" for f in flags):
        confidence = min(confidence, 0.3)
    return Verdict(round(confidence, 3), flags, line_scores, critic or {})
