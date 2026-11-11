"""Orchestrator: intake -> preprocess -> retrieve examples -> transcribe -> verify -> route -> export.

Every component is injected (storage, engine, critic, job store), so each can be replaced
without touching the others. The dashboard only calls the review methods at the bottom.
"""
from __future__ import annotations

import csv
import time
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from statistics import mean

from .agents.verifier import (GeminiCritic, combine, consensus, critic_feedback, line_agreement)
from .config import Settings
from .dataset import Audit, TrainingCache, match_pairs
from .engines import HTREngine, make_engine
from .jobs import JobStore
from .metrics import cer, wer
from .preprocess import prepare_from_settings
from .retriever import ExampleIndex
from .storage import RemoteFile, Storage, make_storage


class Pipeline:
    def __init__(self, settings: Settings, storage: Storage | None = None, engine: HTREngine | None = None,
                 critic=None, store: JobStore | None = None, log=print):
        self.s = settings
        self._storage, self._engine, self._critic = storage, engine, critic
        self.store = store or JobStore(settings.path(settings.paths.db))
        self.cache = TrainingCache(settings.cache_dir)
        self.inbox_dir = settings.cache_dir / "inbox"
        self.output_dir = settings.cache_dir / "output"
        for d in (self.inbox_dir, self.output_dir):
            d.mkdir(parents=True, exist_ok=True)
        self._index: ExampleIndex | None = None
        self._length_range: tuple[int, int] | None = None
        self.log = log

    # ------------------------------------------------------------ lazy components
    @property
    def storage(self) -> Storage:
        if self._storage is None:
            self._storage = make_storage(self.s)
        return self._storage

    @property
    def engine(self) -> HTREngine:
        if self._engine is None:
            self._engine = make_engine(self.s)
        return self._engine

    @property
    def critic(self):
        if self._critic is None and self.s.verify.critic and self.s.engine.type != "mock":
            cfg = self.s.engine if self.s.engine.type == "vertex" else replace(self.s.engine, type="gemini")
            self._critic = GeminiCritic(self.s.verify.critic_model, engine_cfg=cfg, language=self.s.verify.notes_language)
        return self._critic or None

    @property
    def index(self) -> ExampleIndex:
        if self._index is None:
            self._index = ExampleIndex(self.cache, "train")
        return self._index

    @property
    def length_range(self) -> tuple[int, int] | None:
        if self._length_range is None:
            lengths = sorted(len(self.cache.text(s)) for s in self.cache.stems("train"))
            if len(lengths) >= 20:
                self._length_range = (lengths[len(lengths) // 100], lengths[-1 - len(lengths) // 100])
        return self._length_range

    def prepare(self, data: bytes) -> bytes:
        return prepare_from_settings(data, self.s)

    def examples_for(self, image: bytes, stem: str):
        fs = self.s.few_shot
        return self.index.select(image, fs.k, fs.strategy, fs.fixed, exclude={stem},
                                 prefer_verified=fs.prefer_verified, verified_only=fs.verified_only)

    # ------------------------------------------------------------ 1. training data
    def audit(self) -> Audit:
        images = self.storage.list("train_images")
        texts = self.storage.list("train_texts")
        return match_pairs(images, texts, self.s.dataset.duplicate_policy)

    def sync(self) -> tuple[Audit, dict]:
        audit = self.audit()
        report = self.cache.sync(self.storage, audit, self.prepare, self.s.dataset.val_fraction,
                                 self.s.dataset.test_fraction, progress=self.log,
                                 assume_verified=self.s.dataset.assume_verified)
        self._index, self._length_range = None, None
        return audit, report

    # ------------------------------------------------------------ 2. intake
    def discover(self) -> int:
        """Create a job for every inbox image not seen before and not already transcribed in the output folder."""
        try:
            done = {f.stem for f in self.storage.list("output") if f.is_text}
        except Exception:
            done = set()
        new = 0
        for f in self.storage.list("inbox"):
            if f.is_image and f.stem not in done and self.store.create(f.id, f.name, f.version):
                new += 1
        return new

    def queue_training_review(self, n: int = 20, split: str | None = None, include_verified: bool = False) -> int:
        """Put unverified training pairs in the review queue so an expert can correct the ground truth.

        Pages whose duplicate versions disagree most come first. No model call is made: the
        existing transcription is the draft and the other versions are shown next to it.
        """
        stems = self.cache.stems(split, verified=None if include_verified else False)
        stems.sort(key=lambda s: -self.cache.manifest[s].get("duplicate_cer", -1))
        queued = 0
        for stem in stems:
            if queued >= n:
                break
            job_id = f"train:{stem}"
            meta = self.cache.manifest[stem]
            if not self.store.create(job_id, meta.get("image_name", f"{stem}.jpg"), meta.get("text_v", ""),
                                     kind="training", status="needs_review"):
                continue
            dup = meta.get("duplicate_cer")
            flags = [] if dup is None else [{
                "code": "conflicting_versions", "severity": "soft", "line": None,
                "message": f"{len(self.cache.alternatives(stem)) + 1} versions of this transcription exist; "
                           f"they differ by {dup:.0%} of characters."}]
            self.store.update(job_id, draft=self.cache.text(stem), image_path=str(self.cache.image_path(stem)),
                              confidence=None if dup is None else round(max(0.0, 1 - dup), 3), flags=flags,
                              model="existing transcription")
            queued += 1
        return queued

    def _local_image(self, job: dict) -> Path:
        if job.get("image_path") and Path(job["image_path"]).exists():
            return Path(job["image_path"])
        path = self.inbox_dir / f"{Path(job['name']).stem}.jpg"
        if not path.exists():
            raw = self.storage.download(RemoteFile(id=job["id"], name=job["name"]))
            path.write_bytes(self.prepare(raw))
        return path

    # ------------------------------------------------------------ 3. agentic processing
    def process(self, job_id: str, feedback: str | None = None) -> dict:
        job = self.store.get(job_id)
        v = self.s.verify
        try:
            path = self._local_image(job)
            image = path.read_bytes()
            stem = Path(job["name"]).stem
            examples = self.examples_for(image, stem)

            # Transcriber agent (N independent samples -> consensus + line-level uncertainty)
            results = [self.engine.transcribe(image, examples, feedback) for _ in range(max(1, v.consistency_samples))]
            samples = [r.text for r in results]
            draft, agreement, line_scores = consensus(samples)

            # Verifier agent
            critic = self.critic.review(image, draft) if self.critic else None
            verdict = combine(draft, agreement, line_scores, critic, self.length_range)

            # Self-correction loop: re-transcribe with the critic's notes, keep the better version
            attempts = 0
            while attempts < v.max_retries and (verdict.hard or (critic and critic.get("issues"))):
                attempts += 1
                notes = critic_feedback(critic) if critic and critic.get("issues") else \
                    "\n".join(f"- {f.message}" for f in verdict.flags if f.severity == "hard")
                retry = self.engine.transcribe(image, examples, "\n".join(x for x in (feedback, notes) if x)).text
                r_critic = self.critic.review(image, retry) if self.critic else None
                r_scores = line_agreement(retry, samples) if len(samples) > 1 else [1.0] * len(retry.split("\n"))
                r_verdict = combine(retry, agreement, r_scores, r_critic, self.length_range)
                better = (verdict.hard and not r_verdict.hard) or (
                    not r_verdict.hard and r_critic and critic and r_critic["confidence"] > critic["confidence"])
                if better:
                    draft, critic, verdict = retry, r_critic, r_verdict
                else:
                    break

            # Router
            auto = v.auto_approve and not verdict.hard and verdict.confidence >= v.review_threshold
            usage = {k: sum(r.usage.get(k, 0) for r in results) for k in ("input_tokens", "output_tokens")}
            self.store.update(
                job_id, status="approved" if auto else "needs_review", draft=draft,
                confidence=verdict.confidence, flags=verdict.to_json()["flags"], line_scores=verdict.line_scores,
                critic=verdict.critic, examples=[e.stem for e in examples], usage=usage,
                model=results[0].model, attempts=(job.get("attempts") or 0) + 1 + attempts,
                image_path=str(path), error=None, note=feedback,
            )
            if auto:
                self._export(self.store.get(job_id), draft, reviewer="auto", add_to_training=False)
        except Exception as exc:  # keep the queue moving; the error is visible in the dashboard
            self.store.update(job_id, status="error", error=f"{type(exc).__name__}: {exc}")
            self.log(f"  ! {job['name']}: {exc}")
        return self.store.get(job_id)

    def run(self, limit: int | None = None) -> dict:
        new = self.discover()
        pending = self.store.list(["pending"], order="name")[: limit or None]
        self.log(f"{new} new page(s) found, processing {len(pending)}")
        for i, job in enumerate(pending, 1):
            done = self.process(job["id"])
            self.log(f"  [{i}/{len(pending)}] {job['name']} -> {done['status']} (confidence {done['confidence']})")
        return self.store.stats()

    def watch(self, interval: int = 300) -> None:
        while True:
            self.run()
            time.sleep(interval)

    # ------------------------------------------------------------ 4. human review (dashboard)
    def _export(self, job: dict, final: str, reviewer: str, add_to_training: bool) -> None:
        stem = Path(job["name"]).stem
        text = final.strip().replace("\r\n", "\n") + "\n"
        if job.get("kind") == "training":  # corrected ground truth goes back to the training folder
            self.storage.upload_text("train_texts", f"{stem}.txt", text)
            self.cache.mark_verified(stem, text.strip(), reviewer)
            self._index = None
            self.store.update(job["id"], status="verified", final=text.strip(), reviewer=reviewer,
                              review_cer=round(cer(job.get("draft") or "", text), 4), in_training=1)
            return
        output_id = self.storage.upload_text("output", f"{stem}.txt", text)
        (self.output_dir / f"{stem}.txt").write_text(text, encoding="utf-8")
        if add_to_training:  # feedback loop: validated pages become new examples / fine-tuning data
            self.storage.copy_into(RemoteFile(id=job["id"], name=job["name"]), "train_images", job["name"])
            self.storage.upload_text("train_texts", f"{stem}.txt", text)
            self.cache.add(stem, Path(job["image_path"]).read_bytes(), text.strip(), "train",
                           {"source": "review", "image_name": job["name"], "verified": True, "verified_by": reviewer})
            self.cache.save()
            self._index, self._length_range = None, None
        self.store.update(job["id"], status="exported", final=text.strip(), reviewer=reviewer,
                          review_cer=round(cer(job.get("draft") or "", text), 4),
                          output_id=output_id, in_training=int(add_to_training))

    def approve(self, job_id: str, final_text: str, reviewer: str, add_to_training: bool = True) -> dict:
        self._export(self.store.get(job_id), final_text, reviewer, add_to_training)
        return self.store.get(job_id)

    def verify_pair(self, stem: str, text: str, reviewer: str) -> None:
        """An expert corrected a training transcription: write it back and trust it from now on."""
        text = text.strip().replace("\r\n", "\n")
        self.storage.upload_text("train_texts", f"{stem}.txt", text + "\n")
        self.cache.manifest[stem]["conflict"] = False
        self.cache.mark_verified(stem, text, reviewer)
        self._index = None

    def save_draft(self, job_id: str, text: str, reviewer: str) -> None:
        self.store.update(job_id, final=text, reviewer=reviewer)

    def reject(self, job_id: str, reviewer: str, note: str = "") -> None:
        self.store.update(job_id, status="rejected", reviewer=reviewer, note=note)

    def retranscribe(self, job_id: str, note: str | None = None) -> dict:
        return self.process(job_id, feedback=note or None)

    def export_approved(self) -> int:
        jobs = self.store.list(["approved"])
        for job in jobs:
            self._export(job, job.get("final") or job["draft"], job.get("reviewer") or "auto", False)
        return len(jobs)

    # ------------------------------------------------------------ 5. evaluation
    def evaluate(self, n: int | None = None, split: str = "test") -> dict:
        stems = self.cache.stems(split)[: n or None]
        if not stems:
            raise RuntimeError(f"No '{split}' pages in the cache. Run `python -m htr sync` first.")
        fs = self.s.few_shot
        out_dir = self.s.path(self.s.paths.reports) / datetime.now().strftime("eval_%Y%m%d_%H%M")
        out_dir.mkdir(parents=True, exist_ok=True)
        rows = []
        for i, stem in enumerate(stems, 1):
            image, ref = self.cache.image_path(stem).read_bytes(), self.cache.text(stem)
            hyp = self.engine.transcribe(image, self.examples_for(image, stem)).text
            (out_dir / f"{stem}.txt").write_text(hyp, encoding="utf-8")
            row = {"page": stem, "cer": round(cer(ref, hyp), 4), "cer_loose": round(cer(ref, hyp, "loose"), 4),
                   "wer": round(wer(ref, hyp), 4), "ref_lines": ref.count("\n") + 1, "hyp_lines": hyp.count("\n") + 1}
            rows.append(row)
            self.log(f"  [{i}/{len(stems)}] {stem}: CER {row['cer']:.1%}")
        with open(out_dir / "report.csv", "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        return {"pages": len(rows), "cer": round(mean(r["cer"] for r in rows), 4),
                "cer_loose": round(mean(r["cer_loose"] for r in rows), 4),
                "wer": round(mean(r["wer"] for r in rows), 4), "model": self.s.engine.model,
                "verified_references": sum(1 for s in stems if self.cache.manifest[s].get("verified")),
                "k": fs.k, "report": str(out_dir / "report.csv")}

    @classmethod
    def from_settings(cls, settings: Settings, **kw) -> "Pipeline":
        return cls(settings, **kw)
