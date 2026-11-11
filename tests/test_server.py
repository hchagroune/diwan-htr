"""End-to-end API tests with local storage and an offline engine (no Google account needed)."""
import importlib
import io
import os
import sys
import time
import zipfile
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def page(seed: int) -> bytes:
    im = Image.new("L", (600, 900), 235)
    d = ImageDraw.Draw(im)
    for r in range(8 + seed % 5):
        d.line([(60, 120 + r * 50), (540 - seed % 40, 120 + r * 50)], fill=20, width=4)
    buf = io.BytesIO()
    im.save(buf, "JPEG")
    return buf.getvalue()


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("HTR_DATA", str(tmp_path / "data"))
    monkeypatch.setenv("HTR_ENGINE", "mock")
    monkeypatch.setenv("APP_PASSWORD", "casbah")
    for k in ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN", "HTR_TRAIN_FOLDER"):
        monkeypatch.delenv(k, raising=False)
    sys.modules.pop("server.main", None)
    main = importlib.import_module("server.main")
    from fastapi.testclient import TestClient

    c = TestClient(main.app)
    c.main = main
    return c


def wait_idle(main, timeout=10):
    end = time.time() + timeout
    while time.time() < end:
        snap = main.WORKER.snapshot()
        if not snap["current"] and not snap["queued"]:
            return
        time.sleep(0.05)
    raise AssertionError("worker did not finish")


def test_password_gate_and_full_flow(client):
    main = client.main
    assert client.get("/").status_code == 200 and "app.js" in client.get("/").text
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/api/state").status_code == 401
    assert client.post("/api/login", json={"password": "nope"}).status_code == 401
    tok = client.post("/api/login", json={"password": "casbah"}).json()["token"]
    h = {"X-Diwan-Key": tok}

    # library: a zip with pairs, a duplicate version that disagrees, and an orphan
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for i in range(24):
            z.writestr(f"FRANOM88_1MIOM31_{i:04d}.jpg", page(i))
            z.writestr(f"FRANOM88_1MIOM31_{i:04d}.txt", f"الحمد لله\nسطر رقم {i}\nوالسلام")
        z.writestr("FRANOM88_1MIOM31_0003 1.txt", "نص مختلف تماما عن الاصل في كل كلماته")
        z.writestr("FRANOM88_1MIOM31_0999.jpg", page(99))
    r = client.post("/api/pairs/upload", headers=h, files=[("files", ("lib.zip", buf.getvalue(), "application/zip"))],
                    data={"expert": "true"}).json()
    assert r == {"added": 24, "conflicts": 1, "imagesWithoutText": 1, "textsWithoutImage": 0}
    st = client.get("/api/state", headers=h).json()
    conflict = [p for p in st["pairs"] if p["conflict"]]
    assert len(st["pairs"]) == 24 and [p["stem"] for p in conflict] == ["FRANOM88_1MIOM31_0003"]
    detail = client.get("/api/pairs/FRANOM88_1MIOM31_0003", headers=h).json()
    assert detail["alts"] and not detail["verified"]
    assert client.get("/api/pairs/FRANOM88_1MIOM31_0003/image", headers=h).status_code == 200
    client.post("/api/pairs/FRANOM88_1MIOM31_0003/verify", headers=h, json={"text": "الحمد لله\nمصحح", "reviewer": "Expert"})
    p3 = [p for p in client.get("/api/state", headers=h).json()["pairs"] if p["stem"] == "FRANOM88_1MIOM31_0003"][0]
    assert p3["verified"] and not p3["conflict"]

    # pages: upload, transcribe (mock engine), review, approve, download
    r = client.post("/api/pages/upload", headers=h, files=[("files", ("NEW_0001.jpg", page(7), "image/jpeg")),
                                                           ("files", ("NEW_0002.jpg", page(8), "image/jpeg"))]).json()
    assert r["added"] == 2
    pages = client.get("/api/state", headers=h).json()["pages"]
    assert {p["status"] for p in pages} == {"new"}
    assert client.get(f"/api/pages/{pages[0]['id']}/image?k={tok}").status_code == 200
    assert client.post("/api/transcribe-all", headers=h).json()["queued"] == 2
    wait_idle(main)
    pages = client.get("/api/state", headers=h).json()["pages"]
    assert {p["status"] for p in pages} == {"review"}
    d = client.get(f"/api/pages/{pages[0]['id']}", headers=h).json()
    assert d["draft"] and len(d["examples"]) == 3
    client.post(f"/api/pages/{pages[0]['id']}/approve", headers=h,
                json={"text": "الحمد لله\nنص معتمد", "reviewer": "Expert", "addToLibrary": True})
    txt = client.get(f"/api/pages/{pages[0]['id']}/txt?k={tok}")
    assert txt.text == "الحمد لله\nنص معتمد\n" and "attachment" in txt.headers["content-disposition"]
    z = zipfile.ZipFile(io.BytesIO(client.get(f"/api/approved.zip?k={tok}").content))
    assert z.namelist() == ["NEW_0001.txt"]
    st = client.get("/api/state", headers=h).json()
    assert len(st["pairs"]) == 25 and any(p["status"] == "approved" for p in st["pages"])
    out = Path(os.environ["HTR_DATA"]) / "drive" / "output" / "NEW_0001.txt"
    assert out.read_text(encoding="utf-8") == "الحمد لله\nنص معتمد\n"

    # remove from list: hidden and not re-created
    client.delete(f"/api/pages/{pages[1]['id']}", headers=h)
    assert len(client.get("/api/state", headers=h).json()["pages"]) == 1

    # settings
    s = client.post("/api/settings", headers=h, json={"k": 9, "model": "gemini-x", "critic": False}).json()
    assert s["k"] == 6 and s["model"] == "gemini-x" and s["critic"] is False

    # evaluation runs in the background
    assert client.post("/api/eval", headers=h, json={"n": 5}).status_code in (200, 400)


def test_state_backup_restores_queue(client):
    main = client.main
    tok = client.post("/api/login", json={"password": "casbah"}).json()["token"]
    h = {"X-Diwan-Key": tok}
    client.post("/api/pages/upload", headers=h, files=[("files", ("A.jpg", page(1), "image/jpeg"))])
    client.post("/api/settings", headers=h, json={"k": 2})
    main.SAVER.save()
    rows = main.PIPE.store.export_rows()
    for r in rows:
        main.PIPE.store.delete(r["id"])
    assert not main.PIPE.store.export_rows()
    main.SAVER.restore()
    assert [r["name"] for r in main.PIPE.store.export_rows()] == ["A.jpg"]
