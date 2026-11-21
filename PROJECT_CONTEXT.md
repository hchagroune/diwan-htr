# PROJECT CONTEXT: Dīwān al-Wathāʾiq (ديوان الوثائق)

> **For the next Claude session.** Read this whole file before doing anything. It is the full state of the
> project as of **21 November 2026** (America/New_York evening of 20 Nov). Then check the repository for
> anything newer than this file: `git log` on `main` and `website`, open pull requests, and the n8n instance.
> The owner (Houssam) works through Claude and expects every change as a reviewable commit and pull request.

---

## 1. The project in one paragraph

Dīwān al-Wathāʾiq turns handwritten Arabic sharia-court deeds in **Maghrebi script** (Algiers and Annaba,
18th–19th c., ANOM microfilm fonds *1 MiOM 31*, series "Archives arabes et turques de l'Ancienne Régence
d'Alger") into verified text. An **AI reader** transcribes a page, an **AI checker** compares the text with the
image line by line and gives a confidence score, and a **human expert** approves, corrects or sends the page back
with a note. Every approved page (image + text) becomes a worked example for the next pages and a training pair.
It is the **final project for the Limitless Learning Agentic AI course** ("Final Project for Limitless Learning
Agentic AI Training"), built by **Limitless imagination**, and it is pitched to **KSAA** (the pitch document was
`pitch_ksaa.pdf`). The live demo only needs to work during the pitch, so free hosting is fine.

## 2. People

| Who | Role |
|---|---|
| **Chagroune Houssam Eddine** (حسام الدين شقرون) | Founder, Limitless imagination. Owner of the GitHub repo and the n8n instance. Talks to Claude. |
| **Daddi Addoun Yacine** (ياسين دادي عدون) | Co-founder, Limitless imagination. The expert reviewer in the pilot: approved pages 0038 and 0188. |
| **Dr Mourad Bouache** (د. مراد بوعاش) and the students of the Agentic AI learning group at Limitless Learning | Pitch audience. |

The Arabic spellings of all three names were written by Claude and are **not yet confirmed** by the owner.
Public contact used on the site (it was already on the old site): `chagroune.amc@gmail.com`.

## 3. Hard rules (from the owner; apply to everything)

1. **Never name any AI model, vendor or product** (no model names, no AI-provider company names) anywhere on the
   site, the pitch or the demo: pages, code comments, alt text, slides, metadata. Use **"AI reader / القارئ الآلي"**
   and **"AI checker / المدقق الآلي"**. Remove any mention found. Before handing over site work, grep `docs/` and
   `tools/` for vendor and model names: the count must be **zero**. (The app on `main` still names the vendor:
   see §11, deferred by the owner.) This file follows the same rule.
2. **Bilingual Arabic + English on every page**, with a language switch. Arabic is right-to-left and set properly
   (`lang`, `dir`, fonts), not mirrored English.
3. **Static site only**: no server, no API keys, no secrets in code. Must work **offline** on presentation day.
4. **Respectful use of Islamic visual heritage**: geometry, tiles, seals, script. **Never Qur'anic verses as
   decoration.** No generic "AI" visuals (gradients, robots, glowing brains).
5. **Accessible**: WCAG AA contrast, keyboard navigation, reduced-motion support, works on a phone.
6. **Ask before inventing any fact, name, number or quote.** Estimates must be labelled "تقدير / Estimate".
7. Every change goes through a commit + pull request that the owner reviews and merges. Never commit secrets.

## 4. Systems map

| System | Where | State |
|---|---|---|
| GitHub repo | https://github.com/hchagroune/diwan-htr (public) | Default branch `main`. Site source on branch `website`, merged into `main` regularly (PRs #5, #9). |
| **Presentation site** (static) | **https://diwan-alwathaiq.onrender.com** | **Live.** Render static site `diwan-alwathaiq`, serves `docs/` from branch **`website`**, redeploys on every commit to `docs/**`, never sleeps. Created by hand in the Render dashboard (also described in `render.yaml`). |
| Transcription app (Docker) | https://diwan-htr.onrender.com | Live. Render web service `diwan-htr`, free plan, built from `Dockerfile` on `main`, deploys when GitHub checks pass (`autoDeployTrigger: checksPass`). Password-protected. Sleeps after 15 min idle (~1 min to wake), disk wiped on sleep. |
| n8n Cloud | https://hsm38.app.n8n.cloud | **Free trial** (no public API, no Environments). Connected to Claude through the official n8n MCP connector. Two workflows, both currently **not published/active** (see §6). |
| Google Drive | folders: Inbox, In review, Results, Library | Folder IDs live in n8n *Settings* (not repeated here because the repo is public). |
| MongoDB | `mongo.ibadica.org:443` (TLS via Traefik SNI) on the owner's home Ubuntu server | Set up with Docker (see §10). **Not yet wired into the n8n workflow.** |
| GitHub Pages | would be https://hchagroune.github.io/diwan-htr/ | **Unknown / probably off.** Claude could not check (API blocked). The pitch QR no longer depends on it. |
| Claude Project | "Final Project. n8n MCP" | Holds `claude/mongodb-setup.md`. |

### Render environment variables of `diwan-htr` (names only; values only in Render)
Required: the AI vendor API key (variable named in `render.yaml`), `APP_PASSWORD`, `APP_SECRET` (generated).
Google Drive: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`, `HTR_TRAIN_FOLDER`,
`HTR_INBOX_FOLDER`, `HTR_OUTPUT_FOLDER`. Fixed: `HTR_DATA=/home/user/data`. Optional: `HTR_MODEL`,
`HTR_TRAIN_TEXT_FOLDER`. The owner filled them in the Render form when creating the Blueprint.

## 5. Repository layout

### Branch `main` (the app + a copy of the site)
```
server/main.py        FastAPI app: REST API (/api/...), background worker, password login, /healthz
static/               the app's own UI (index.html, app.js, style.css), Arabic with an English switch
htr/                  pipeline: engines/ (the vendor engine, a generic compatible-API engine, a mock engine), agents/verifier.py (rule checks +
                      self-consistency + model critic → confidence and flags), retriever.py (few-shot examples),
                      storage/ (gdrive, local), dataset.py, metrics.py, preprocess.py, textnorm.py, jobs.py
tests/test_server.py  API tests (run by GitHub Actions on push/PR to main)
config.space.yaml     default settings (storage, dataset split, examples, checker, rules)
Dockerfile            python:3.12-slim, user 1000, uvicorn server.main:app on $PORT (default 7860)
render.yaml           Render Blueprint: service diwan-htr (docker, free, virginia, main, checksPass) +
                      static site diwan-alwathaiq (branch website, publish ./docs, headers, buildFilter docs/**)
.github/workflows/deploy.yml   "Test and deploy": pytest on push/PR to main; optional Hugging Face Space
                      deploy only if the HF_TOKEN secret exists (otherwise skipped with a notice)
README.md             app docs: Render setup, presentation site section, HF alternative, Drive, usage, costs
docs/, tools/         copy of the presentation site (source of truth is branch `website`)
PROJECT_CONTEXT.md    this file
```
App tabs: Pages (upload scans/zip or fetch from Drive, transcribe), Review (scan + editable text, doubtful lines
in red, Approve saves .txt and adds to Library), Library (verified pairs used as examples), Register (correction
rate, accuracy test, settings, download approved). Run locally: `HTR_ENGINE=mock uvicorn server.main:app --port 7860`.

### Branch `website` (the presentation site; Render static site serves `docs/`)
```
docs/index.html            Welcome (motto hero in a horseshoe arch)
docs/how/index.html        How it works (5 steps, send-back loop, 3 rules, why agentic, real n8n workflow diagrams)
docs/demo/index.html       Try it (recorded pilot data, no network); live mode optional
docs/pitch/index.html      Full-screen pitch + workflow presentation (15 slides)
docs/archive/index.html    The archive (facts + sources)
docs/creators/index.html   The creators (deed of two witnesses, seals with photos, ijāza chain)
docs/board.html            Team board (older page, English only, reads the n8n door with an access code)
docs/404.html              Works under / (Render) and /diwan-htr/ (GitHub Pages) via a <base> chosen at load
docs/sw.js                 Service worker: caches every page/asset after one visit (https only); generated
docs/assets/diwan.css      Design tokens + all page styles;  diwan.js: language switch, embed mode, SW register
docs/assets/pitch.css/.js  Pitch styles and controls;  demo.js: demo logic;  demo-data.js: generated pilot data
docs/assets/qr-demo.svg    QR → https://diwan-alwathaiq.onrender.com/demo/?page=0188 (generated)
docs/assets/fonts/         self-hosted WOFF: Amiri 400/700/400i (Latin + Arabic subset), IBM Plex Sans Arabic
                           400/500/600, IBM Plex Sans (variable) + OFL licences
docs/assets/img/           uploaded pictures (see §8.6) + README.md with the exact names and the upload link
docs/assets/board.js/.css, site.css   the board (site.css kept only for the board)
tools/build_site.py        GENERATES all pages, 404, QR and sw.js:  cd tools && python build_site.py
tools/pitch_page.py        the pitch slides;  tools/workflow_diagrams.py: SVG diagrams of the real workflow
tools/build_demo_data.py   builds docs/assets/demo-data.js from tools/pilot_source.py + tools/pilot_0188.json
tools/qr.py                QR encoder (byte mode, level M, v1–6), verified with OpenCV
tools/service_worker.py    writes docs/sw.js with the file list and a content hash
```
**Never edit the generated HTML by hand**: change `tools/*.py` and run `python tools/build_site.py` (from `tools/`).
Pages use relative paths everywhere, so they work on Render (root), GitHub Pages (`/diwan-htr/`) and `file://`.

### Other branches (all merged, safe to delete): `deploy/render-free`, `deploy/render-static-site`,
`site/direction-b`, `site/pitch-v2`, `site/workflow-presentation`, `site/photos`.
**Open PR #1** `docs/limitless-learning-final-project` → `main`: adds to README "This website was created as the
final project for our **Limitless Learning Agentic AI** course." Mergeable; never merged.

### Pull request history
#1 open (README line) · #2 Render free deploy (merged) · #3 Direction B site (merged into website before its QR fix
landed) · #4 static site in render.yaml · #5 website→main · #6 pitch redesign + Amiri + QR fix · #7 workflow
presentation · #8 photo slots + removed "our ask" · #9 website→main (includes the owner's image uploads).

## 6. The n8n workflows (hsm38.app.n8n.cloud)

### 6.1 Main workflow: "Diwan al-Wathaiq - Arabic HTR with expert review" (id `Yi2GEyaDfdaYeLg9`)
87 nodes = **40 working steps** + sticky notes (every step has a "What it does / Why it is here" note, in English).
The canvas note "Note 1" carries the title **"Final Project for Limitless Learning Agentic AI Training"**.
**Not published**, so the 10-minute schedule does not fire on its own; runs are started with *Test now*.

**Settings** node holds 13 values: inboxFolderId, reviewFolderId, resultsFolderId, libraryFolderId,
exampleStems (`FRANOM88_1MIOM31_0188.JPG, …_0100.JPG, …_0038.JPG`), expertEmail, transcribeModel, checkerModel,
maxRetries (**1**), notesLanguage (**Arabic**), the vendor API base URL, systemPrompt (expert palaeographer of
Maghrebi-script Arabic manuscripts, diplomatic transcription only) and rules (output only Arabic text, one line
per manuscript line, keep original spelling, no added vowels/hamzas, Maghrebi fa = dot below → ف and qaf = one dot
above → ق, folio number alone on the first line, spaces where the seal interrupts line 1, …).
⚠ **reviewFolderId and resultsFolderId currently hold the same folder ID**, so "Move scan to Results" changes
nothing. Probably unintended; ask the owner.

Stages (node names as in n8n; vendor-named nodes are shown by role on the site):
1. **Pick up a new scan** (9): Every 10 minutes / Test now → Settings → Find next scan in Inbox → Move scan to
   In review → Board: being read → Download scan → Shrink scan (≤2400 px working copy) → Scan to base64.
2. **Load the example pages** (9): List example files → Find example files (Library) → Pick example files →
   Download example files → Image or text? → Shrink example images → Put examples back together →
   Examples to base64 → Collect examples (image + expert text pairs).
3. **Read and check** (7): Build reader request → AI reader transcribes (HTTP, waits up to 5 min, retries) →
   Read transcription (serious flags: empty answer, same line 3× in a row, cut text) → Build checker request →
   AI checker checks → Read check (confidence capped at 20% after a serious flag, 50% if the answer is unreadable;
   keeps the best version) → Problems found? Try again (loops back once with the checker's notes, maxRetries=1).
4. **Expert reviews by email** (5): Prepare review email → Board: with the expert → Email the expert and wait
   (Gmail, button to a form: Decision, Corrected transcription pre-filled, Note for the reader, Reviewer name;
   waits up to **7 days**) → Read expert answer → Decision (Approve / Re-transcribe / Reject / No answer).
5. **Save** (10): Approve → Make .txt file (e.g. `FRANOM88_1MIOM31_0188.txt`) → Save .txt to Results → Move scan
   to Results → Board: approved. Re-transcribe → Board: back to the reader → Expert note as feedback → back to
   Build reader request (attempts reset). Reject → "Rejected: scan stays in In review" → Board: rejected.
   No answer → "No answer after 7 days" → Board: no answer.

**Board steps** write one row per page into the n8n **data table "Diwan pages"**: stage `reading`, `expert`,
`approved`, `rejected`, `no_answer`, with confidence, flagged lines, attempts, problem, reviewer, updated.
If a Board step fails, the run carries on.

### 6.2 "Diwan door: board" (id `cu6glfzTRnmqZGYO`)
Read-only webhook `https://hsm38.app.n8n.cloud/webhook/diwan-board` (GET). Checks header **`X-Diwan-Code`**
(Header Auth credential "Diwan board code"), returns `{ok, updated, pages:[…], inbox:[…]}` from "Diwan pages" and
the Inbox folder. Used by `docs/board.html` and by the optional live mode of the demo. **Not published** either.

### 6.3 n8n ↔ GitHub
Trial plan: no n8n API, so no automatic sync. A starter kit was produced in an earlier session (zip
`diwan-htr-n8n-starter-kit.zip`: `n8n/scripts/n8n_sync.py` pull/diff/export/push/validate, workflows
n8n-deploy.yml / n8n-check.yml / n8n-drift.yml, CLAUDE.md, .mcp.json, PR template). **It is not in the repo.**
A Claude Doc "diwan-htr: Claude + n8n + GitHub Team Workflow" explains the protocol (Claude artifact, bound to the
owner's account). Edit n8n through the n8n MCP connector (call get_user_preferences / get_instance_context first).

## 7. Pilot results (real, recorded in n8n)

| Page | Court / date | Checker | Expert |
|---|---|---|---|
| **0188** (folio 162) | Hanafi court, Algiers · 3 Rajab 1257 AH (1841) | first reading 0.85 (5 flagged lines) → after the expert's note 0.92 (3 flags) | **Approved** by Yacine Daddi Addoun after 2 rounds |
| **0038** (folio 33) | court not named on the page · early Ramadan 1231 AH (1816) | 0.88 (4 flags) | Expert transcription by Yacine (approved) |
| **0100** (folio 86) | Maliki court, **Annaba** · date not yet verified | 0.88 (5 flags) | **Waiting** for the expert |

The demo data (`docs/assets/demo-data.js`) holds the drafts, checker issues (in Arabic), the recorded second
reading of 0188 and the expert texts. Line 9 of 0188: first draft «وبالمحكمة المنجفية بدار الجزائر المحمية بالله
تعلى امام قاضيها انت حجة ابو السه الواضع خطه بعد»; approved «وبالمحكمة الحنفية من بلد الجزائر المحمية بالله تعلى
امام قاضيها في التاريخ ايده الله الواضع طابعه». The site typesets the motto with **تعالى** (owner's choice; the
scribe wrote تعلى, and the speaker notes say so).

## 8. The presentation site (Direction B, "Kasbah zellige", Ottoman-era Algiers)

### 8.1 Decisions
Owner chose **Direction B** over A. Fonts: **Amiri everywhere** (Amiri Bold headlines, Amiri main text; Reem
Kufi was removed); IBM Plex Sans / Plex Sans Arabic only for small controls (nav, buttons, chips, labels).
The licence question was waived ("don't worry about licence"; all fonts are OFL anyway).

### 8.2 Design tokens
Night indigo `#111A2D`, night-2 `#18233A`, night line `#2A3651`, whitewash `#F7F5EF`, Algerian green `#16684E`
(approved), terracotta `#B4532A` (doubtful; text `#9A4422` on `#F6E3D9`), faience cobalt `#2A4F8F` (links),
lamp brass `#E2BD55` (on indigo only), parchment `#E9DCC0`/`#EFE3C8`. Motifs: eight-point-star zellige band, blue
faience dado band at section thresholds, horseshoe arch after Djamaa el Kebir (SVG
`M -360 120 L -360 0 A 395 395 0 1 1 360 0 L 360 120`), round seals. Colour = tile meaning (green approved,
terracotta doubtful, brass on indigo).

### 8.3 Bilingual mechanics
Each text exists twice: `data-l="ar"` (lang ar, dir rtl) and `data-l="en"`. `html[data-ui]` hides one;
`diwan.js` sets `lang`, `dir`, `data-ui`, the page title (`data-title-ar/en`), persists the choice in
localStorage (`diwan-lang`, wrapped in try/catch), accepts `?lang=ar|en`, fires `diwan:lang`. Default Arabic.
`?embed=1` hides header/footer (used when the pitch opens the demo); Esc inside it closes the pitch overlay.

### 8.4 Pages
- **Welcome**: motto «الجزائر المحمية بالله» (Amiri 700, brass) inside the arch with the line-9 image above it, ink
  reveal right-to-left (off under reduced motion), "Algiers, protected by God", source line, buttons
  «جرّب بنفسك» / «شاهد العرض»; المشكلة / الفكرة columns; "About the motto" caption with two sources (§9).
- **How it works**: 5 steps, send-back loop, three rules, why agentic, and **the real workflow**: overview + 5 stage
  diagrams with Arabic/English explanations (drawn from the workflow; no screenshots, because n8n node names
  contain the vendor name).
- **Try it** (demo): pick 0188 / 0038 / 0100 → highlight moves line by line over the scan → draft types in RTL →
  checker flags lines in terracotta with its note and confidence → visitor accepts a suggestion, edits a line
  (click the line number), approves, or sends back with a note (0188 replays the **recorded** second reading at
  0.92; others are labelled **simulated**) → final view with counter «هذا السطر صار بيانات تدريب / this line is now
  training data» and the expert's real text to compare. `?page=0188` starts at once. **Live mode** (off by default)
  GETs the n8n door with the access code and shows a table of stages.
- **Pitch** (`/pitch/`): 15 slides. Keys: →/← follow reading direction (in Arabic, ← goes forward), PageUp/Down,
  Space, Home/End, click (leading third goes back), swipe, **N** speaker notes (Arabic/English), **F** full screen,
  `#n` deep links, 15 progress tiles, star lattice background, one ink reveal per headline.
  1 Hook (line 9 on parchment, "Who can still read it?") · 2 Gap (1,000-square grid, 6 lit = 0.6%; ≈0.004%) ·
  3 Hidden heritage (125 reels; ≈30,000 registers) · 4 Solution (reading loop with send-back arrow, **Try it** opens
  the demo in an overlay, QR) · **5 Whole workflow** (40 steps, 5 stages, 2 loops, board table) · **6–10 the five
  stages**, each drawn like the n8n canvas and lit step by step · 11 Knowledge transfer (21% → 10% bars) ·
  12 Pilot results (3 pages; 85–88% → 92%; estimated curve) · 13 Vision (three nested arches) ·
  14 «لماذا يعنيكم، د. مراد بوعاش وطلبة الذكاء الاصطناعي الوكيلي؟» (two AI agents + one human expert; orchestrated
  in n8n; a real archive) · 15 Close (motto + two seals with photos, Arabic and English names). The "our ask"
  line was **removed** at the owner's request. Pitch slides stay under 35 words.
- **The archive**: 125 reels (Grangaud 2026), ≈75,000 folios (our estimate: 125 × ~600), ≈30,000 registers (ISAM
  estimate), 23,756 held digitally by ISAM; filmed by operators with no Arabic (reels backwards, negatives);
  Maghrebi fa/qaf; pilot pages; sources.
- **The creators**: deed «الحمد لله. حضر ديوانُ الوثائق لدى شهيديه، المكرّمَين حسام الدين شقرون وياسين دادي عدون،
  وأشهد على نفسه…» with an English gloss and **[date] placeholder**; two round seals (photos inside) opening dialogs
  with role and **placeholder story** ("[ تُكتب القصة لاحقًا ]"); ijāza chain: court scribes 1841 → expert reviewers →
  the two witnesses → you. Both signatures (seal + name) close every page's footer.

### 8.5 QR code
Slide 4 QR → **`https://diwan-alwathaiq.onrender.com/demo/?page=0188`** (opens a real attempt on page 0188).
Generated by `build_site.py` from `SITE_URL`; verified by decoding. Phones need internet to open it.
A live n8n run from phones was offered but **not built** (needs a new webhook, costs AI credit, not offline).

### 8.6 Pictures (`docs/assets/img/`; any of .jpg .png .webp .jpeg is accepted)
Uploaded by the owner: `houssam.jpg`, `motto-line9.jpg`, `scan-0188.jpg`, `scan-0038.jpg`, `scan-0100.jpg`.
**Missing: `yacine.jpg`** (Yacine's seal shows his name until it exists) and `diwan-site-og-card.jpg` (1200×630).
Upload page: https://github.com/hchagroune/diwan-htr/upload/website/docs/assets/img (commit to `website`).

### 8.7 Testing approach used
Local server + headless Chrome (Playwright) screenshots: every page in Arabic and English, 375 px phone width (no
horizontal scroll), keyboard tab order, demo flow for 0188 and 0100, pitch keys/swipe/notes/overlay, word counts,
vendor-name grep = 0, QR decoded with OpenCV.

## 9. Facts and sources used (use only these; label estimates)

- Arabic = **0.6%** of websites (W3Techs, Nov 2026).
- OpenITI: 2.31 billion Arabic tokens, 101,336 from transcribed handwriting → **≈0.004%** (our estimate).
- **≈30,000** Ottoman court registers survive (ISAM estimate; ISAM holds **23,756** digitally).
- ANOM Algiers microfilm: **125 reels**, filmed by operators who knew no Arabic (Grangaud, *Insaniyat* 111, 2026);
  ~600 folios per reel (estimate) → **≈75,000 folios** (our estimate).
- Off-the-shelf character error on historical Arabic handwriting **33–70%** (KITAB-Bench 2025; never name the
  models) → **3–12%** after fine-tuning on verified lines.
- Maghrebi: **21.24% → 9.99%** after ~80 verified lines, **7.7%** after ~160; proofreading time **−42%** (Lucas, Salah &
  Vidal-Gorène 2022, arXiv 2211.16147).
- Motto: Ottoman epithets of Algiers «الجزائر المحمية / المحروسة» (Zakia Rajai, Journal of the General Union of Arab
  Archaeologists, https://cguaa.journals.ekb.eg/article_31924.html); al-Maḥrūsa = "la bien gardée", divine and
  human protection ("Les fortifications ottomanes d'Alger (1516–1830)", https://shs.hal.science/halshs-01309755).
- **Avoid**: "5 million manuscripts", "only 5–10% edited".

## 10. MongoDB on the home server (separate deliverable)

Home Ubuntu server with Docker, Traefik, Portainer, it-tools, an Omeka site and n8n (`n8n.ibadica.org`); DNS at
OVHcloud (domain `ibadica.org`). MongoDB 8.0 in Docker behind Traefik **TCP router with HostSNI on 443** and a
Let's Encrypt certificate (port 27017 never published). DB `arabic_docs`, user `n8n_app` (readWrite, authSource
admin), collection `documents` with a unique `driveFileId` index and a text index (`default_language: none`).
Connection: `mongodb://n8n_app:<password>@mongo.ibadica.org:443/arabic_docs?tls=true&authSource=admin`
(inside Docker: `mongodb:27017`). Optional mongo-express (`ui` profile), optional SRV record for `mongodb+srv`.
Full guide: Claude Project doc `claude/mongodb-setup.md` (files were delivered as `mongodb-docker.zip`:
docker-compose.yml, .env.example, init/01-init-app.js, README.md). Not in this repo. Not yet used by the workflow.

## 11. Open items / next steps (none started unless stated)

1. **The app on `main` names the AI vendor** (README front matter, README text, `htr/engines/` file names,
   requirements, render.yaml variable). The owner said "report it to next stage": decide whether to scrub it.
2. **`yacine.jpg`** and the og-card picture to upload. Creators' **stories**, the deed's **[date]**, and the
   **Arabic spellings** of the names (incl. د. مراد بوعاش) to confirm.
3. **Publish the n8n workflows** if the schedule and the board should run on their own (trial plan limits).
   Check **reviewFolderId = resultsFolderId** in Settings.
4. **MongoDB** is ready but not connected: add a MongoDB upsert (by `driveFileId`) after "Save .txt to Results".
5. **PR #1** (README line) is still open.
6. `docs/board.html` is English only and loads fonts from the internet (breaks the "bilingual" and "offline"
   rules for that one page); `docs/README.md` still describes GitHub Pages and old picture names.
7. Optional **live mode from the QR** (real n8n run from phones) was offered, not built.
8. GitHub Pages status unknown; not needed now that Render serves the site.
9. n8n Cloud trial will expire: export the workflows (JSON) before it does.

## 12. Working conventions for Claude

- Branch from the target branch, commit with clear messages, push, open a PR with
  `gh api repos/hchagroune/diwan-htr/pulls -f title=… -f head=… -f base=… -F body=@file` (GraphQL `gh pr create`
  is blocked by the proxy). Merging and force-pushing from Claude's sandbox are blocked: **the owner merges**.
- Site work targets **`website`**; Render redeploys it within a minute of the merge. App work targets **`main`**.
- After site changes: `cd tools && python build_site.py`, then test (see §8.7) and grep for vendor names.
- The sandbox cannot reach onrender.com or most websites directly; ask the owner to approve a web fetch or to check.
- Claude artifacts from earlier sessions are bound to the owner's original Claude account and will not open from
  another account: the design canvas (directions A/B, mockups) https://claude.ai/artifact/UxuKn8rLDPwBQeuLaUpunX and
  the team-workflow Claude Doc https://claude.ai/artifact/RpEUrKSsfSojFTFb1o7rwG. Everything needed is in this file.
- Keep this file up to date at the end of each working session.
