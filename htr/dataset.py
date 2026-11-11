"""Training pairs: matching image <-> transcription, auditing, deterministic split, local cache."""
from __future__ import annotations

import codecs
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .storage import RemoteFile, Storage


def decode_text(data: bytes) -> str:
    """Transcriptions may be UTF-8 (with/without BOM), UTF-16 or Windows-1256 (old Arabic Windows)."""
    if data[:2] in (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE):
        return data.decode("utf-16")
    for enc in ("utf-8-sig", "cp1256"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def split_of(stem: str, val_fraction: float, test_fraction: float) -> str:
    """Stable split from a hash of the name: a page never moves between train and test."""
    bucket = int(hashlib.sha1(stem.encode("utf-8")).hexdigest()[:8], 16) / 0xFFFFFFFF
    if bucket < test_fraction:
        return "test"
    if bucket < test_fraction + val_fraction:
        return "val"
    return "train"


@dataclass
class Pair:
    stem: str
    image: RemoteFile
    text: RemoteFile


@dataclass
class Audit:
    pairs: list[Pair] = field(default_factory=list)
    images_without_text: list[str] = field(default_factory=list)
    texts_without_image: list[str] = field(default_factory=list)
    duplicate_texts: dict[str, list[RemoteFile]] = field(default_factory=dict)   # stem -> all versions
    duplicate_images: dict[str, list[RemoteFile]] = field(default_factory=dict)

    def summary(self) -> dict:
        return {
            "pairs": len(self.pairs),
            "images_without_text": len(self.images_without_text),
            "texts_without_image": len(self.texts_without_image),
            "stems_with_duplicate_texts": len(self.duplicate_texts),
            "stems_with_duplicate_images": len(self.duplicate_images),
        }


def _pick(files: list[RemoteFile], policy: str) -> RemoteFile | None:
    if len(files) == 1:
        return files[0]
    if policy == "skip":
        return None
    if policy == "largest":
        return max(files, key=lambda f: f.size or 0)
    return max(files, key=lambda f: f.modified or "")  # newest


def match_pairs(images: list[RemoteFile], texts: list[RemoteFile], duplicate_policy: str = "newest") -> Audit:
    by_img, by_txt = defaultdict(list), defaultdict(list)
    for f in images:
        if f.is_image:
            by_img[f.stem].append(f)
    for f in texts:
        if f.is_text:
            by_txt[f.stem].append(f)
    audit = Audit()
    audit.duplicate_texts = {s: fs for s, fs in by_txt.items() if len(fs) > 1}
    audit.duplicate_images = {s: fs for s, fs in by_img.items() if len(fs) > 1}
    audit.images_without_text = sorted(set(by_img) - set(by_txt))
    audit.texts_without_image = sorted(set(by_txt) - set(by_img))
    for stem in sorted(set(by_img) & set(by_txt)):
        img, txt = _pick(by_img[stem], duplicate_policy), _pick(by_txt[stem], duplicate_policy)
        if img and txt:
            audit.pairs.append(Pair(stem, img, txt))
    return audit


class TrainingCache:
    """Local mirror of the training pairs: <cache>/train/<stem>.jpg|.txt + manifest.json"""

    def __init__(self, cache_dir: Path):
        self.dir = Path(cache_dir) / "train"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.dir / "manifest.json"
        self.manifest: dict[str, dict] = (
            json.loads(self.manifest_path.read_text(encoding="utf-8")) if self.manifest_path.exists() else {}
        )

    def save(self) -> None:
        self.manifest_path.write_text(json.dumps(self.manifest, ensure_ascii=False, indent=1), encoding="utf-8")

    def image_path(self, stem: str) -> Path:
        return self.dir / f"{stem}.jpg"

    def text(self, stem: str) -> str:
        return (self.dir / f"{stem}.txt").read_text(encoding="utf-8")

    def alternatives(self, stem: str) -> list[str]:
        """Other versions of the transcription found in Drive (same file name)."""
        return [p.read_text(encoding="utf-8") for p in sorted(self.dir.glob(f"{stem}.alt*.txt"))]

    def stems(self, split: str | None = None, verified: bool | None = None) -> list[str]:
        return sorted(s for s, m in self.manifest.items()
                      if (split is None or m["split"] == split)
                      and (verified is None or bool(m.get("verified")) == verified))

    def add(self, stem: str, image_bytes: bytes | None, text: str, split: str, meta: dict | None = None) -> None:
        """image_bytes must already be preprocessed (see preprocess.py); None keeps the cached image."""
        if image_bytes is not None:
            self.image_path(stem).write_bytes(image_bytes)
        (self.dir / f"{stem}.txt").write_text(text, encoding="utf-8")
        self.manifest[stem] = {"split": split, **(meta or {})}

    def mark_verified(self, stem: str, text: str, reviewer: str) -> None:
        (self.dir / f"{stem}.txt").write_text(text, encoding="utf-8")
        self.manifest[stem].update(verified=True, verified_by=reviewer)
        self.save()

    def sync(self, storage: Storage, audit: Audit, prepare, val_fraction: float, test_fraction: float,
             progress=print, assume_verified: bool = False) -> dict:
        from .metrics import cer

        added = updated = 0
        for i, pair in enumerate(audit.pairs, 1):
            old = self.manifest.get(pair.stem)
            if old and old.get("image_v") == pair.image.version and old.get("text_v") == pair.text.version:
                continue
            same_image = old and old.get("image_v") == pair.image.version and self.image_path(pair.stem).exists()
            image = None if same_image else prepare(storage.download(pair.image))
            text = decode_text(storage.download(pair.text)).strip()
            split = old["split"] if old else split_of(pair.stem, val_fraction, test_fraction)
            # A text we verified and pushed back to Drive comes back unchanged: keep it verified.
            old_verified_same = bool(old and old.get("verified") and old.get("verified_by")
                                     and (self.dir / f"{pair.stem}.txt").exists() and self.text(pair.stem) == text)
            verified = assume_verified or old_verified_same
            meta = {"image_id": pair.image.id, "image_name": pair.image.name, "image_v": pair.image.version,
                    "text_id": pair.text.id, "text_v": pair.text.version, "verified": verified}
            if old and old.get("verified_by") and verified:
                meta["verified_by"] = old["verified_by"]
            # Several transcriptions with the same name: keep the others and measure how much they disagree.
            for p in self.dir.glob(f"{pair.stem}.alt*.txt"):
                p.unlink()
            others = [f for f in audit.duplicate_texts.get(pair.stem, []) if f.id != pair.text.id]
            if others:
                alts = [decode_text(storage.download(f)).strip() for f in others]
                for n, alt in enumerate(alts, 1):
                    (self.dir / f"{pair.stem}.alt{n}.txt").write_text(alt, encoding="utf-8")
                meta["duplicate_cer"] = round(max(cer(text, a) for a in alts), 4)
                # Two "expert" versions that disagree cannot both be ground truth: an expert must choose.
                if meta["duplicate_cer"] > 0.02 and not old_verified_same:
                    meta["verified"] = False
            self.add(pair.stem, image, text, split, meta)
            added += old is None
            updated += old is not None
            if i % 25 == 0:
                progress(f"  synced {i}/{len(audit.pairs)}")
                self.save()
        self.save()
        disagree = [m["duplicate_cer"] for m in self.manifest.values() if "duplicate_cer" in m]
        return {"added": added, "updated": updated, "total": len(self.manifest),
                "splits": dict(Counter(m["split"] for m in self.manifest.values())),
                "verified": sum(1 for m in self.manifest.values() if m.get("verified")),
                "pages_with_conflicting_versions": len(disagree),
                "mean_disagreement_between_versions": round(sum(disagree) / len(disagree), 3) if disagree else None}

    def stats(self) -> dict:
        lengths = sorted(len(self.text(s)) for s in self.stems())
        if not lengths:
            return {"pages": 0}
        chars = Counter()
        for s in self.stems():
            chars.update(c for c in self.text(s) if not c.isspace())
        pct = lambda q: lengths[min(len(lengths) - 1, int(q * len(lengths)))]
        return {
            "pages": len(lengths), "chars_p01": pct(0.01), "chars_median": pct(0.5), "chars_p99": pct(0.99),
            "lines_median": sorted(self.text(s).count("\n") + 1 for s in self.stems())[len(lengths) // 2],
            "character_inventory": "".join(c for c, _ in chars.most_common()),
            "rare_characters": {c: n for c, n in chars.items() if n <= 3},
        }


def audit_to_json(audit: Audit) -> dict:
    return {**audit.summary(), "details": {
        "images_without_text": audit.images_without_text, "texts_without_image": audit.texts_without_image,
        "duplicate_texts": {k: [f.name for f in v] for k, v in audit.duplicate_texts.items()},
        "duplicate_images": {k: [f.name for f in v] for k, v in audit.duplicate_images.items()},
        "pairs_sample": [asdict(p) for p in audit.pairs[:3]],
    }}
