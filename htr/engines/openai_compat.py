"""Any OpenAI-compatible vision server, e.g. vLLM serving your own fine-tuned Qwen-VL model."""
from __future__ import annotations

import base64
import os

from ..config import EngineCfg, PromptCfg
from ..textnorm import clean_model_output
from .base import EngineResult, Example, HTREngine, feedback_block


class OpenAICompatEngine(HTREngine):
    name = "openai_compat"

    def __init__(self, cfg: EngineCfg, prompt: PromptCfg, client=None):
        if client is None:
            from openai import OpenAI

            client = OpenAI(base_url=cfg.endpoint, api_key=os.environ.get("OPENAI_COMPAT_API_KEY", "EMPTY"))
        self.cfg, self.prompt, self.client = cfg, prompt, client

    @staticmethod
    def _image(b: bytes) -> dict:
        return {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(b).decode()}}

    def transcribe(self, image: bytes, examples: list[Example], feedback: str | None = None) -> EngineResult:
        msgs = [{"role": "system", "content": self.prompt.system_full}]
        for ex in examples:
            msgs.append({"role": "user", "content": [self._image(ex.image), {"type": "text", "text": self.prompt.instruction}]})
            msgs.append({"role": "assistant", "content": ex.text})
        final = self.prompt.instruction + (f"\n\n{feedback_block(feedback)}" if feedback else "")
        msgs.append({"role": "user", "content": [self._image(image), {"type": "text", "text": final}]})
        resp = self.client.chat.completions.create(
            model=self.cfg.model, messages=msgs, max_tokens=self.cfg.max_output_tokens,
            temperature=0.0 if self.cfg.temperature is None else self.cfg.temperature,
        )
        return EngineResult(clean_model_output(resp.choices[0].message.content or ""), self.cfg.model)
