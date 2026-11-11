"""Few-shot example selection: show the model the training pages that look most like the new page."""
from __future__ import annotations

import io
import random

import numpy as np
from PIL import Image

from .dataset import TrainingCache
from .engines.base import Example


def image_feature(data: bytes) -> np.ndarray:
    """Cheap layout/ink descriptor: 32x48 thumbnail + ink histogram + aspect ratio + ink density."""
    im = Image.open(io.BytesIO(data)).convert("L")
    aspect = im.width / im.height
    thumb = np.asarray(im.resize((32, 48), Image.Resampling.BILINEAR), dtype=np.float32) / 255.0
    ink = 1.0 - thumb
    hist, _ = np.histogram(ink, bins=16, range=(0, 1), density=True)
    vec = np.concatenate([(ink - ink.mean()).ravel(), hist / 16.0, [aspect, ink.mean() * 4]])
    return vec / (np.linalg.norm(vec) + 1e-8)


class ExampleIndex:
    def __init__(self, cache: TrainingCache, split: str = "train"):
        self.cache = cache
        self.stems = cache.stems(split)
        self._matrix: np.ndarray | None = None

    def _features(self) -> np.ndarray:
        if self._matrix is None:
            path = self.cache.dir / "features.npz"
            stored = {}
            if path.exists():
                z = np.load(path, allow_pickle=False)
                stored = dict(zip(z["stems"].tolist(), z["feats"]))
            feats = []
            for s in self.stems:
                if s not in stored:
                    stored[s] = image_feature(self.cache.image_path(s).read_bytes())
                feats.append(stored[s])
            np.savez(path, stems=np.array(list(stored)), feats=np.stack(list(stored.values())))
            self._matrix = np.stack(feats)
        return self._matrix

    def select(self, image: bytes, k: int, strategy: str = "similar", fixed: list | None = None,
               exclude: set | None = None, prefer_verified: bool = True,
               verified_only: bool = False) -> list[Example]:
        exclude = set(exclude or ())
        verified = {s for s in self.stems if self.cache.manifest[s].get("verified")}
        if verified_only or (prefer_verified and len(verified - exclude) >= k):
            exclude |= set(self.stems) - verified
        candidates = [s for s in self.stems if s not in exclude]
        if k <= 0 or not candidates:
            return []
        if strategy == "fixed" and fixed:
            chosen = [s for s in fixed if s in self.cache.manifest][:k]
        elif strategy == "random":
            chosen = random.sample(candidates, min(k, len(candidates)))
        else:
            mat = self._features()
            idx = [i for i, s in enumerate(self.stems) if s not in exclude]
            scores = mat[idx] @ image_feature(image)
            chosen = [self.stems[idx[i]] for i in np.argsort(-scores)[:k]]
        return [Example(s, self.cache.image_path(s).read_bytes(), self.cache.text(s)) for s in chosen]
