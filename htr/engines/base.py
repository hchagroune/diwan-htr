"""Engine interface. Anything that can turn an image into text plugs in here."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Example:
    stem: str
    image: bytes      # preprocessed JPEG
    text: str


@dataclass
class EngineResult:
    text: str
    model: str
    usage: dict = field(default_factory=dict)


class HTREngine(ABC):
    name = "base"

    @abstractmethod
    def transcribe(self, image: bytes, examples: list[Example], feedback: str | None = None) -> EngineResult:
        """image: preprocessed JPEG bytes. feedback: reviewer/critic notes for a second attempt."""


def feedback_block(feedback: str) -> str:
    return ("A reviewer checked a previous attempt and reported the problems below. "
            "Re-read those places in the image carefully, then output the full corrected "
            "transcription only.\n" + feedback.strip())
