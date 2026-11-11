"""Typed settings loaded from config.yaml (+ secrets from .env)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import Any

import yaml

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None


def _build(cls, data: dict | None):
    """Create dataclass `cls` from a dict, ignoring unknown keys, recursing into nested dataclasses."""
    data = data or {}
    kwargs = {}
    for f in fields(cls):
        if f.name not in data:
            continue
        value = data[f.name]
        ftype = f.type if not isinstance(f.type, str) else _NESTED.get(f.name)
        if ftype is not None and is_dataclass(ftype) and isinstance(value, dict):
            value = _build(ftype, value)
        kwargs[f.name] = value
    return cls(**kwargs)


@dataclass
class DriveCfg:
    auth: str = "oauth"
    credentials_file: str = "secrets/client_secret.json"
    token_file: str = "secrets/token.json"
    folders: dict = field(default_factory=dict)


@dataclass
class DatasetCfg:
    duplicate_policy: str = "newest"
    assume_verified: bool = False
    val_fraction: float = 0.05
    test_fraction: float = 0.05


@dataclass
class PathsCfg:
    cache: str = "data/cache"
    db: str = "data/jobs.sqlite"
    reports: str = "data/reports"


@dataclass
class PreprocessCfg:
    max_side: int = 3072
    grayscale: bool = True
    autocontrast: bool = True


@dataclass
class EngineCfg:
    type: str = "gemini"
    model: str = "gemini-3.1-pro-preview"
    endpoint: str | None = None
    vertex_project: str | None = None
    vertex_location: str = "global"
    temperature: float | None = None
    thinking_level: str | None = None
    media_resolution: str | None = "high"
    max_output_tokens: int = 8192


@dataclass
class FewShotCfg:
    k: int = 3
    strategy: str = "similar"
    fixed: list = field(default_factory=list)
    prefer_verified: bool = True
    verified_only: bool = False


@dataclass
class VerifyCfg:
    consistency_samples: int = 1
    critic: bool = True
    critic_model: str = "gemini-3.5-flash"
    notes_language: str = "English"   # language of the critic's notes shown to reviewers
    max_retries: int = 1
    review_threshold: float = 0.85
    auto_approve: bool = False


@dataclass
class PromptCfg:
    system: str = "You are an expert palaeographer of Maghrebi Arabic manuscripts."
    conventions: str = "- Output ONLY the transcribed Arabic text."
    instruction: str = "Transcribe this page."

    @property
    def system_full(self) -> str:
        return f"{self.system.strip()}\n\nRules:\n{self.conventions.strip()}"


_NESTED = {
    "drive": DriveCfg, "dataset": DatasetCfg, "paths": PathsCfg, "preprocess": PreprocessCfg,
    "engine": EngineCfg, "few_shot": FewShotCfg, "verify": VerifyCfg, "prompt": PromptCfg,
}


@dataclass
class Settings:
    storage: str = "drive"
    local_root: str = "data/local_drive"
    local_folders: dict = field(default_factory=dict)
    drive: DriveCfg = field(default_factory=DriveCfg)
    dataset: DatasetCfg = field(default_factory=DatasetCfg)
    paths: PathsCfg = field(default_factory=PathsCfg)
    preprocess: PreprocessCfg = field(default_factory=PreprocessCfg)
    engine: EngineCfg = field(default_factory=EngineCfg)
    few_shot: FewShotCfg = field(default_factory=FewShotCfg)
    verify: VerifyCfg = field(default_factory=VerifyCfg)
    prompt: PromptCfg = field(default_factory=PromptCfg)
    base_dir: Path = field(default_factory=Path.cwd)

    def path(self, p: str | os.PathLike) -> Path:
        """Resolve a config path relative to the config file's folder."""
        p = Path(p)
        return p if p.is_absolute() else (self.base_dir / p)

    @property
    def cache_dir(self) -> Path:
        return self.path(self.paths.cache)


def load_settings(path: str | os.PathLike | None = None, overrides: dict[str, Any] | None = None) -> Settings:
    path = Path(path or os.environ.get("HTR_CONFIG", "config.yaml")).resolve()
    if load_dotenv:
        load_dotenv(path.parent / ".env")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
    data = data or {}
    for key, value in (overrides or {}).items():  # e.g. {"engine.type": "mock"}
        node = data
        *parents, leaf = key.split(".")
        for part in parents:
            node = node.setdefault(part, {})
        node[leaf] = value
    settings = _build(Settings, data)
    settings.base_dir = path.parent
    return settings
