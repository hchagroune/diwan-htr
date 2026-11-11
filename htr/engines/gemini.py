"""Gemini engine (Gemini API key or Vertex AI, incl. a fine-tuned Vertex endpoint)."""
from __future__ import annotations

import os
import time

from ..config import EngineCfg, PromptCfg
from ..textnorm import clean_model_output
from .base import EngineResult, Example, HTREngine, feedback_block

RETRY_CODES = {429, 500, 502, 503, 504}


def make_client(cfg: EngineCfg):
    from google import genai

    if cfg.type == "vertex":
        project = cfg.vertex_project or os.environ.get("GOOGLE_CLOUD_PROJECT")
        return genai.Client(vertexai=True, project=project, location=cfg.vertex_location)
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set (put it in .env)")
    return genai.Client(api_key=key)


def call_with_retry(fn, attempts: int = 5, base_delay: float = 5.0):
    from google.genai import errors

    for i in range(attempts):
        try:
            return fn()
        except errors.APIError as exc:
            if getattr(exc, "code", None) not in RETRY_CODES or i == attempts - 1:
                raise
            time.sleep(base_delay * (3 ** i))


class GeminiEngine(HTREngine):
    name = "gemini"

    def __init__(self, cfg: EngineCfg, prompt: PromptCfg, client=None):
        self.cfg, self.prompt = cfg, prompt
        self.client = client or make_client(cfg)
        # A tuned Vertex model is addressed by its endpoint resource name.
        self.model = cfg.endpoint if (cfg.type == "vertex" and cfg.endpoint) else cfg.model

    def generation_config(self):
        from google.genai import types

        kw = {"system_instruction": self.prompt.system_full, "max_output_tokens": self.cfg.max_output_tokens}
        if self.cfg.temperature is not None:
            kw["temperature"] = self.cfg.temperature
        if self.cfg.thinking_level:
            kw["thinking_config"] = types.ThinkingConfig(thinking_level=self.cfg.thinking_level.upper())
        if self.cfg.media_resolution:
            kw["media_resolution"] = f"MEDIA_RESOLUTION_{self.cfg.media_resolution.upper()}"
        return types.GenerateContentConfig(**kw)

    def build_contents(self, image: bytes, examples: list[Example], feedback: str | None = None):
        """Few-shot as a conversation: (page -> transcription) x k, then the new page."""
        from google.genai import types

        img = lambda b: types.Part.from_bytes(data=b, mime_type="image/jpeg")
        contents = []
        for ex in examples:
            contents.append(types.Content(role="user", parts=[img(ex.image), types.Part.from_text(text=self.prompt.instruction)]))
            contents.append(types.Content(role="model", parts=[types.Part.from_text(text=ex.text)]))
        final = self.prompt.instruction + (f"\n\n{feedback_block(feedback)}" if feedback else "")
        contents.append(types.Content(role="user", parts=[img(image), types.Part.from_text(text=final)]))
        return contents

    def transcribe(self, image: bytes, examples: list[Example], feedback: str | None = None) -> EngineResult:
        contents = self.build_contents(image, examples, feedback)
        resp = call_with_retry(lambda: self.client.models.generate_content(
            model=self.model, contents=contents, config=self.generation_config()))
        usage = {}
        if getattr(resp, "usage_metadata", None):
            u = resp.usage_metadata
            usage = {"input_tokens": u.prompt_token_count, "output_tokens": u.candidates_token_count}
        return EngineResult(clean_model_output(resp.text or ""), self.model, usage)
