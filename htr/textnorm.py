"""Arabic text cleaning (model output) and normalisation (for fair CER/WER)."""
from __future__ import annotations

import re
import unicodedata

ARABIC_CHAR = re.compile(r"[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿]")
LATIN_CHAR = re.compile(r"[A-Za-z]")
TATWEEL = "ـ"
DIACRITICS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭ]")
_FENCE = re.compile(r"^\s*```[\w-]*\s*$")

# "loose" mode: ignore spelling variants that scholars transcribe inconsistently,
# incl. Maghrebi fa/qaf forms (ڢ ڧ ڡ ٯ) and Arabic-Indic digits.
_LOOSE = str.maketrans({
    "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ی": "ي", "ة": "ه", "ک": "ك",
    "ڢ": "ف", "ڡ": "ف", "ڧ": "ق", "ٯ": "ق",
    **{chr(0x0660 + i): str(i) for i in range(10)},
    **{chr(0x06F0 + i): str(i) for i in range(10)},
})


def clean_model_output(text: str) -> str:
    """Remove what a chatty model may add around the transcription, never the transcription itself.

    Drops markdown fences and leading/trailing lines that contain Latin letters but no Arabic
    (e.g. "Here is the transcription:"). Lines with only digits (folio numbers) are kept.
    """
    text = unicodedata.normalize("NFC", text or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in text.split("\n") if not _FENCE.match(ln)]

    def is_chatter(line: str) -> bool:
        return bool(LATIN_CHAR.search(line)) and not ARABIC_CHAR.search(line)

    while lines and (not lines[0].strip() or is_chatter(lines[0])):
        lines.pop(0)
    while lines and (not lines[-1].strip() or is_chatter(lines[-1])):
        lines.pop()
    return "\n".join(ln.strip() for ln in lines)


def normalize(text: str, mode: str = "strict") -> str:
    """strict: NFC, no tatweel, single spaces. loose: also no diacritics and unified letter variants."""
    text = unicodedata.normalize("NFC", text or "").replace(TATWEEL, "")
    if mode == "loose":
        text = DIACRITICS.sub("", text).translate(_LOOSE)
    return re.sub(r"\s+", " ", text).strip()


def arabic_ratio(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if ARABIC_CHAR.match(c)) / len(letters)
