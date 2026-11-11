"""Offline engine for tests and for trying the dashboard without an API key."""
from __future__ import annotations

from .base import EngineResult, Example, HTREngine

DEMO_TEXT = "نص تجريبي من المحرك الوهمي\nالسطر الثاني للتجربة\nالسطر الثالث للتجربة"


class MockEngine(HTREngine):
    name = "mock"

    def __init__(self, answers=None):
        # answers: callable(image, examples, feedback) -> str, or a list of strings returned in turn
        self.answers = answers
        self.calls = 0

    def transcribe(self, image: bytes, examples: list[Example], feedback: str | None = None) -> EngineResult:
        self.calls += 1
        if callable(self.answers):
            text = self.answers(image, examples, feedback)
        elif isinstance(self.answers, list) and self.answers:
            text = self.answers[(self.calls - 1) % len(self.answers)]
        else:
            text = DEMO_TEXT
        return EngineResult(text, "mock")
