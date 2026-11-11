from .base import EngineResult, Example, HTREngine


def make_engine(settings) -> HTREngine:
    cfg = settings.engine
    if cfg.type in ("gemini", "vertex"):
        from .gemini import GeminiEngine

        return GeminiEngine(cfg, settings.prompt)
    if cfg.type == "openai_compat":
        from .openai_compat import OpenAICompatEngine

        return OpenAICompatEngine(cfg, settings.prompt)
    if cfg.type == "mock":
        from .mock import MockEngine

        return MockEngine()
    raise ValueError(f"Unknown engine type: {cfg.type}")


__all__ = ["EngineResult", "Example", "HTREngine", "make_engine"]
