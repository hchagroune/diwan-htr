"""Dīwān al-Wathāʾiq: web server for a Hugging Face Space.

Wraps the `htr` pipeline (Gemini + Google Drive) in a small REST API and serves the website.
Everything is configured with Space secrets / variables (see README.md); nothing to edit in code.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import io
import json
import logging
import os
import queue
import re
import threading
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from htr.config import load_settings
from htr.dataset import decode_text, split_of
from htr.metrics import cer
from htr.pipeline import Pipeline

log = logging.getLogger("diwan")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

ROOT = Path(__file__).resolve().parents[1]
STATE_NAME = ".diwan_state.json"
IMAGE_RE = re.compile(r"\.(jpe?g|png|webp|tiff?)$", re.I)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ------------------------------------------------------------------ configuration from the Space
def build_settings():
    data = Path(os.environ.get("HTR_DATA", ROOT / "data"))
    o = {"paths.cache": str(data / "cache"), "paths.db": str(data / "jobs.sqlite"), "paths.reports": str(data / "reports")}
    train = os.environ.get("HTR_TRAIN_FOLDER", "")
    folders = {"train_images": train, "train_texts": os.environ.get("HTR_TRAIN_TEXT_FOLDER", train),
               "inbox": os.environ.get("HTR_INBOX_FOLDER", ""), "output": os.environ.get("HTR_OUTPUT_FOLDER", "")}
    google = all(os.environ.get(k) for k in ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN"))
    drive = google and all(folders.values())
    if drive:
        o.update({"storage": "drive", "drive.auth": "refresh_token", "drive.folders": folders})
    else:
        o.update({"storage": "local", "local_root": str(data / "drive"),
                  "local_folders": {"train_images": "library", "train_texts": "library", "inbox": "inbox", "output": "output"}})
    for env, key in (("HTR_ENGINE", "engine.type"), ("HTR_MODEL", "engine.model"), ("HTR_CRITIC_MODEL", "verify.critic_model")):
        if os.environ.get(env):
            o[key] = os.environ[env]
    return load_settings(ROOT / "config.space.yaml", o), drive


SETTINGS, DRIVE = build_settings()
PIPE = Pipeline(SETTINGS, log=log.info)
PASSWORD = os.environ.get("APP_PASSWORD", "")
SECRET = os.environ.get("APP_SECRET") or hashlib.sha256(("diwan:" + PASSWORD).encode()).hexdigest()

# Settings the website may change (stored with the queue backup, so they survive restarts)
EDITABLE = {
    "model": ("engine", "model", str), "k": ("few_shot", "k", int), "samples": ("verify", "consistency_samples", int),
    "critic": ("verify", "critic", bool), "critic_model": ("verify", "critic_model", str),
    "retries": ("verify", "max_retries", int), "conventions": ("prompt", "conventions", str),
    "notes_language": ("verify", "notes_language", str),
}
LIMITS = {"k": (0, 6), "samples": (1, 3), "retries": (0, 2)}
OVERRIDES: dict = {}
LAST = {"eval": None, "sync": None, "error": None}


def apply_settings(values: dict) -> None:
    for key, value in values.items():
        if key not in EDITABLE or value is None:
            continue
        section, attr, typ = EDITABLE[key]
        value = typ(value)
        if key in LIMITS:
            lo, hi = LIMITS[key]
            value = max(lo, min(hi, value))
        if typ is str:
            value = value.strip()
            if not value:
                continue
        setattr(getattr(SETTINGS, section), attr, value)
        OVERRIDES[key] = value
    PIPE._engine = PIPE._critic = None  # rebuilt with the new settings on next use


def current_settings() -> dict:
    return {k: getattr(getattr(SETTINGS, s), a) for k, (s, a, _) in EDITABLE.items()}


# ------------------------------------------------------------------ queue backup in Drive
class StateSaver:
    """Free Spaces lose their disk on restart: back the job queue up to the output folder."""

    def __init__(self):
        self.dirty = threading.Event()
        threading.Thread(target=self._loop, daemon=True).start()

    def soon(self) -> None:
        self.dirty.set()

    def payload(self) -> dict:
        return {"version": 1, "saved_at": now(), "jobs": PIPE.store.export_rows(), "settings": OVERRIDES,
                "eval": LAST["eval"]}

    def save(self) -> None:
        text = json.dumps(self.payload(), ensure_ascii=False)
        (PIPE.s.cache_dir / STATE_NAME).write_text(text, encoding="utf-8")
        if DRIVE:
            PIPE.storage.upload_text("output", STATE_NAME, text)

    def _loop(self) -> None:
        while True:
            self.dirty.wait()
            time.sleep(5)  # collect a burst of changes into one write
            self.dirty.clear()
            try:
                self.save()
            except Exception as exc:  # noqa: BLE001
                log.warning("state backup failed: %s", exc)

    def restore(self) -> None:
        data = None
        try:
            if DRIVE:
                f = next((f for f in PIPE.storage.list("output") if f.name == STATE_NAME), None)
                if f:
                    data = json.loads(decode_text(PIPE.storage.download(f)))
            elif (PIPE.s.cache_dir / STATE_NAME).exists():
                data = json.loads((PIPE.s.cache_dir / STATE_NAME).read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            log.warning("state restore failed: %s", exc)
        if not data:
            return
        if not PIPE.store.export_rows():
            n = PIPE.store.import_rows(data.get("jobs", []))
            log.info("restored %s jobs from backup", n)
        apply_settings(data.get("settings") or {})
        LAST["eval"] = data.get("eval")


SAVER = StateSaver()


# ------------------------------------------------------------------ background worker (one Gemini job at a time)
class Worker:
    def __init__(self):
        self.q: queue.Queue = queue.Queue()
        self.lock = threading.Lock()
        self.pending: list[dict] = []
        self.current: dict | None = None
        threading.Thread(target=self._loop, daemon=True).start()

    def submit(self, kind: str, **kw) -> bool:
        task = {"kind": kind, **kw}
        with self.lock:
            same = [t for t in self.pending + ([self.current] if self.current else [])
                    if t["kind"] == kind and t.get("id") == kw.get("id")]
            if same:
                return False
            self.pending.append(task)
        self.q.put(task)
        return True

    def clear(self) -> int:
        with self.lock:
            n = len(self.pending)
            self.pending.clear()
        while not self.q.empty():
            try:
                self.q.get_nowait()
            except queue.Empty:
                break
        return n

    def snapshot(self) -> dict:
        with self.lock:
            return {"current": self.current, "queued": list(self.pending)}

    def ids(self) -> tuple[str | None, set]:
        with self.lock:
            cur = self.current.get("id") if self.current and self.current["kind"] == "transcribe" else None
            return cur, {t["id"] for t in self.pending if t["kind"] == "transcribe"}

    def _loop(self) -> None:
        while True:
            task = self.q.get()
            with self.lock:
                if task not in self.pending:  # cleared by "Stop"
                    continue
                self.pending.remove(task)
                self.current = task
            try:
                self._run(task)
                LAST["error"] = None
            except Exception as exc:  # noqa: BLE001
                log.exception("task failed: %s", task)
                LAST["error"] = f"{type(exc).__name__}: {exc}"
            finally:
                with self.lock:
                    self.current = None
                SAVER.soon()

    def _run(self, task: dict) -> None:
        kind = task["kind"]
        if kind == "transcribe":
            PIPE.process(task["id"], feedback=task.get("note") or None)
        elif kind == "sync":
            audit, report = PIPE.sync()
            LAST["sync"] = {"at": now(), "audit": audit.summary(), "report": report}
        elif kind == "discover":
            PIPE.discover()
        elif kind == "eval":
            LAST["eval"] = {"at": now(), **PIPE.evaluate(task.get("n") or 20)}


WORKER = Worker()


def startup() -> None:
    SAVER.restore()
    if DRIVE:
        WORKER.submit("sync")
        WORKER.submit("discover")


threading.Thread(target=startup, daemon=True).start()

# ------------------------------------------------------------------ helpers
STATUS = {"pending": "new", "needs_review": "review", "approved": "approved", "exported": "approved",
          "verified": "approved", "rejected": "rejected", "error": "error"}


def token() -> str:
    return hmac.new(SECRET.encode(), b"diwan-session", hashlib.sha256).hexdigest()


def auth(request: Request) -> None:
    if not PASSWORD:
        return
    given = request.headers.get("x-diwan-key") or request.query_params.get("k") or ""
    if not hmac.compare_digest(given, token()):
        raise HTTPException(401, "Password required")


def enc(job_id: str) -> str:
    """URL-safe public id (local storage ids are file paths)."""
    return base64.urlsafe_b64encode(job_id.encode()).decode().rstrip("=")


def dec(public_id: str) -> str:
    try:
        return base64.urlsafe_b64decode(public_id + "=" * (-len(public_id) % 4)).decode()
    except (binascii.Error, UnicodeDecodeError):
        raise HTTPException(404, "Page not found") from None


def stem_of(name: str) -> str:
    return Path(name).stem


def base_stem(name: str) -> str:
    """'X 1.txt' and 'X (1).txt' are other versions of 'X.txt'."""
    s = re.sub(r"\.[^.]+$", "", name)
    return re.sub(r"\s+\d+$", "", re.sub(r"\s*\(\d+\)$", "", s)).strip()


def first_lines(text: str, n: int = 2) -> str:
    return " · ".join([ln for ln in (text or "").split("\n") if ln.strip()][:n])


def line_count(text: str) -> int:
    return len([ln for ln in (text or "").split("\n") if ln.strip()])


def page_summary(job: dict, current: str | None, queued: set) -> dict:
    status = STATUS.get(job["status"], job["status"])
    if job["id"] == current:
        status = "transcribing"
    elif job["id"] in queued:
        status = "queued"
    text = job.get("final") or job.get("draft") or ""
    return {"id": enc(job["id"]), "stem": stem_of(job["name"]), "status": status, "confidence": job.get("confidence"),
            "preview": first_lines(text), "lines": line_count(text), "reviewCer": job.get("review_cer"),
            "updatedAt": job.get("updated_at"), "approvedAt": job.get("updated_at") if status == "approved" else None,
            "hasImage": bool(job.get("image_path") and Path(job["image_path"]).exists())}


def page_flags(job: dict) -> list[dict]:
    out = []
    for f in job.get("flags") or []:
        if f.get("code") == "critic":
            continue
        out.append({"code": f.get("code"), "line": f.get("line"), "msg": f.get("message", ""), "hard": f.get("severity") == "hard"})
    for i in (job.get("critic") or {}).get("issues") or []:
        out.append({"code": "critic", "line": i.get("line"), "msg": i.get("problem", ""), "fix": i.get("suggestion", "")})
    return out


_pair_memo: dict = {}


def pair_summary(stem: str, meta: dict) -> dict:
    path = PIPE.cache.dir / f"{stem}.txt"
    key = (stem, path.stat().st_mtime if path.exists() else 0)
    if key not in _pair_memo:
        text = PIPE.cache.text(stem) if path.exists() else ""
        _pair_memo[key] = (first_lines(text, 1), line_count(text))
    first, lines = _pair_memo[key]
    return {"stem": stem, "verified": bool(meta.get("verified")), "conflict": bool(meta.get("conflict") or (
        meta.get("duplicate_cer") is not None and meta["duplicate_cer"] > 0.02 and not meta.get("verified"))),
            "dupCer": meta.get("duplicate_cer"), "first": first, "lines": lines, "split": meta.get("split")}


def get_job(public_id: str) -> dict:
    job = PIPE.store.get(dec(public_id))
    if not job or job.get("status") == "deleted":
        raise HTTPException(404, "Page not found")
    return job


async def expand(files: list[UploadFile]) -> list[tuple[str, bytes]]:
    out = []
    for f in files:
        data = await f.read()
        name = Path(f.filename or "file").name
        if name.lower().endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                for info in z.infolist():
                    base = Path(info.filename).name
                    if info.is_dir() or not base or base.startswith(".") or "__MACOSX" in info.filename:
                        continue
                    out.append((base, z.read(info)))
        else:
            out.append((name, data))
    return out


def mime_of(name: str) -> str:
    ext = Path(name).suffix.lower()
    return {".png": "image/png", ".webp": "image/webp", ".tif": "image/tiff", ".tiff": "image/tiff"}.get(ext, "image/jpeg")


# ------------------------------------------------------------------ API
app = FastAPI(title="Diwan al-Wathaiq", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


class Login(BaseModel):
    password: str


class TextBody(BaseModel):
    text: str
    reviewer: str = ""
    addToLibrary: bool = True


class NoteBody(BaseModel):
    note: str = ""


class EvalBody(BaseModel):
    n: int = 20


@app.get("/", response_class=HTMLResponse)
def index() -> Response:
    return FileResponse(ROOT / "static" / "index.html", headers={"Cache-Control": "no-cache"})


@app.post("/api/login")
def login(body: Login) -> dict:
    if PASSWORD and not hmac.compare_digest(body.password, PASSWORD):
        raise HTTPException(401, "Wrong password")
    return {"token": token() if PASSWORD else ""}


@app.get("/api/state", dependencies=[Depends(auth)])
def state() -> dict:
    cur, queued = WORKER.ids()
    jobs = [j for j in PIPE.store.list(None, order="name") if (j.get("kind") or "inbox") == "inbox" and j["status"] != "deleted"]
    gemini = SETTINGS.engine.type == "mock" or bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    return {
        "pages": [page_summary(j, cur, queued) for j in jobs],
        "pairs": [pair_summary(s, m) for s, m in sorted(PIPE.cache.manifest.items())],
        "settings": current_settings(), "worker": WORKER.snapshot(), "drive": DRIVE, "gemini": gemini,
        "password": bool(PASSWORD), "eval": LAST["eval"], "sync": LAST["sync"], "error": LAST["error"],
    }


@app.get("/api/pages/{job_id}", dependencies=[Depends(auth)])
def page(job_id: str) -> dict:
    job = get_job(job_id)
    cur, queued = WORKER.ids()
    s = page_summary(job, cur, queued)
    return {**s, "draft": job.get("draft") or "", "final": job.get("final") or "", "flags": page_flags(job),
            "examples": job.get("examples") or [], "reviewer": job.get("reviewer") or "", "attempts": job.get("attempts") or 0,
            "note": job.get("note") or "", "error": job.get("error") or "", "model": job.get("model") or ""}


@app.get("/api/pages/{job_id}/image", dependencies=[Depends(auth)])
def page_image(job_id: str) -> Response:
    job = get_job(job_id)
    path = PIPE._local_image(job)
    if job.get("image_path") != str(path):
        PIPE.store.update(job["id"], image_path=str(path))
    return FileResponse(path, media_type="image/jpeg", headers={"Cache-Control": "private, max-age=86400"})


@app.post("/api/pages/upload", dependencies=[Depends(auth)])
async def upload_pages(files: list[UploadFile] = File(...)) -> dict:
    added = 0
    for name, data in await expand(files):
        if not IMAGE_RE.search(name):
            continue
        rf = PIPE.storage.put("inbox", name, data, mime_of(name))
        if not PIPE.store.create(rf.id, rf.name, rf.version):
            PIPE.store.update(rf.id, status="pending", draft=None, final=None, confidence=None, flags=[], error=None)
        path = PIPE.inbox_dir / f"{stem_of(name)}.jpg"
        path.write_bytes(PIPE.prepare(data))
        PIPE.store.update(rf.id, image_path=str(path))
        added += 1
    SAVER.soon()
    return {"added": added}


@app.post("/api/pages/{job_id}/transcribe", dependencies=[Depends(auth)])
def transcribe(job_id: str, body: NoteBody | None = None) -> dict:
    job = get_job(job_id)
    return {"queued": WORKER.submit("transcribe", id=job["id"], note=(body.note if body else "").strip())}


@app.post("/api/transcribe-all", dependencies=[Depends(auth)])
def transcribe_all() -> dict:
    n = sum(WORKER.submit("transcribe", id=j["id"]) for j in PIPE.store.list(["pending", "error"], order="name")
            if (j.get("kind") or "inbox") == "inbox")
    return {"queued": n}


@app.post("/api/stop", dependencies=[Depends(auth)])
def stop() -> dict:
    return {"cleared": WORKER.clear()}


@app.post("/api/pages/{job_id}/approve", dependencies=[Depends(auth)])
def approve(job_id: str, body: TextBody) -> dict:
    job = get_job(job_id)
    if not body.text.strip():
        raise HTTPException(400, "The transcription is empty")
    PIPE.approve(job["id"], body.text, body.reviewer or "reviewer", add_to_training=body.addToLibrary)
    SAVER.soon()
    return {"ok": True}


@app.post("/api/pages/{job_id}/draft", dependencies=[Depends(auth)])
def save_draft(job_id: str, body: TextBody) -> dict:
    job = get_job(job_id)
    PIPE.save_draft(job["id"], body.text, body.reviewer)
    SAVER.soon()
    return {"ok": True}


@app.post("/api/pages/{job_id}/reject", dependencies=[Depends(auth)])
def reject(job_id: str, body: TextBody | None = None) -> dict:
    job = get_job(job_id)
    PIPE.reject(job["id"], body.reviewer if body else "", "rejected in website")
    SAVER.soon()
    return {"ok": True}


@app.delete("/api/pages/{job_id}", dependencies=[Depends(auth)])
def remove(job_id: str) -> dict:
    """Hide the page from the list. The scan in Drive is left untouched."""
    job = get_job(job_id)
    PIPE.store.update(job["id"], status="deleted")
    SAVER.soon()
    return {"ok": True}


@app.get("/api/pages/{job_id}/txt", dependencies=[Depends(auth)])
def page_txt(job_id: str) -> Response:
    job = get_job(job_id)
    text = (job.get("final") or job.get("draft") or "").rstrip() + "\n"
    name = stem_of(job["name"]) + ".txt"
    return Response(text.encode("utf-8"), media_type="text/plain; charset=utf-8",
                    headers={"Content-Disposition": f"attachment; filename*=UTF-8''{name}"})


@app.get("/api/approved.zip", dependencies=[Depends(auth)])
def approved_zip() -> Response:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for j in PIPE.store.list(["exported", "approved"], order="name"):
            if (j.get("kind") or "inbox") == "inbox" and (j.get("final") or j.get("draft")):
                z.writestr(stem_of(j["name"]) + ".txt", (j.get("final") or j.get("draft")).rstrip() + "\n")
    return Response(buf.getvalue(), media_type="application/zip",
                    headers={"Content-Disposition": "attachment; filename=diwan-transcriptions.zip"})


# ---- library (training pairs)
@app.get("/api/pairs/{stem}", dependencies=[Depends(auth)])
def pair(stem: str) -> dict:
    meta = PIPE.cache.manifest.get(stem)
    if not meta:
        raise HTTPException(404, "Not in the library")
    return {**pair_summary(stem, meta), "text": PIPE.cache.text(stem), "alts": PIPE.cache.alternatives(stem),
            "verifiedBy": meta.get("verified_by", "")}


@app.get("/api/pairs/{stem}/image", dependencies=[Depends(auth)])
def pair_image(stem: str) -> Response:
    path = PIPE.cache.image_path(stem)
    if stem not in PIPE.cache.manifest or not path.exists():
        raise HTTPException(404, "No image")
    return FileResponse(path, media_type="image/jpeg", headers={"Cache-Control": "private, max-age=86400"})


@app.post("/api/pairs/{stem}/verify", dependencies=[Depends(auth)])
def verify_pair(stem: str, body: TextBody) -> dict:
    if stem not in PIPE.cache.manifest:
        raise HTTPException(404, "Not in the library")
    PIPE.verify_pair(stem, body.text, body.reviewer or "reviewer")
    return {"ok": True}


@app.post("/api/pairs/upload", dependencies=[Depends(auth)])
async def upload_pairs(files: list[UploadFile] = File(...), expert: bool = Form(True)) -> dict:
    groups: dict[str, dict] = {}
    for name, data in await expand(files):
        kind = "img" if IMAGE_RE.search(name) else "txt" if name.lower().endswith(".txt") else None
        if kind:
            groups.setdefault(base_stem(name), {"img": [], "txt": []})[kind].append((name, data))
    added = conflicts = 0
    ds = SETTINGS.dataset
    for stem, g in groups.items():
        if not g["img"] or not g["txt"]:
            continue
        g["txt"].sort(key=lambda t: (t[0] != f"{stem}.txt", t[0]))
        texts = []
        for _, raw in g["txt"]:
            t = decode_text(raw).strip()
            if t and t not in texts:
                texts.append(t)
        if not texts:
            continue
        main, alts = texts[0], texts[1:]
        dup = round(max(cer(main, a) for a in alts), 4) if alts else None
        conflict = dup is not None and dup > 0.02
        img_name, img = g["img"][0]
        rf_img = PIPE.storage.put("train_images", img_name, img, mime_of(img_name))
        rf_txt = PIPE.storage.put("train_texts", f"{stem}.txt", (main + "\n").encode("utf-8"), "text/plain")
        old = PIPE.cache.manifest.get(stem) or {}
        verified = bool(expert) and not conflict
        meta = {"image_id": rf_img.id, "image_name": img_name, "image_v": rf_img.version, "text_id": rf_txt.id,
                "text_v": rf_txt.version, "verified": verified, "conflict": conflict}
        if verified:
            meta["verified_by"] = "expert upload"
        if dup is not None:
            meta["duplicate_cer"] = dup
        PIPE.cache.add(stem, PIPE.prepare(img), main, old.get("split") or split_of(stem, ds.val_fraction, ds.test_fraction), meta)
        for p in PIPE.cache.dir.glob(f"{stem}.alt*.txt"):
            p.unlink()
        for n, alt in enumerate(alts, 1):
            (PIPE.cache.dir / f"{stem}.alt{n}.txt").write_text(alt, encoding="utf-8")
        added += 1
        conflicts += conflict
    PIPE.cache.save()
    PIPE._index = PIPE._length_range = None
    orphans_img = sum(1 for g in groups.values() if g["img"] and not g["txt"])
    orphans_txt = sum(1 for g in groups.values() if g["txt"] and not g["img"])
    return {"added": added, "conflicts": conflicts, "imagesWithoutText": orphans_img, "textsWithoutImage": orphans_txt}


# ---- Drive, settings, evaluation
@app.post("/api/sync", dependencies=[Depends(auth)])
def sync() -> dict:
    if not DRIVE:
        raise HTTPException(400, "Google Drive is not connected")
    return {"queued": WORKER.submit("sync")}


@app.post("/api/discover", dependencies=[Depends(auth)])
def discover() -> dict:
    if not DRIVE:
        raise HTTPException(400, "Google Drive is not connected")
    return {"queued": WORKER.submit("discover")}


@app.get("/api/settings", dependencies=[Depends(auth)])
def get_settings() -> dict:
    return current_settings()


@app.post("/api/settings", dependencies=[Depends(auth)])
def set_settings(values: dict) -> dict:
    apply_settings(values)
    SAVER.soon()
    return current_settings()


@app.post("/api/eval", dependencies=[Depends(auth)])
def run_eval(body: EvalBody) -> dict:
    if not PIPE.cache.stems("test"):
        raise HTTPException(400, "No test pages in the library yet")
    return {"queued": WORKER.submit("eval", n=max(1, min(100, body.n)))}


@app.get("/healthz")
def health() -> dict:
    return {"ok": True}
