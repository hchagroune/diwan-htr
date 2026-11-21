"""Diagrams of the real n8n workflow "Diwan al-Wathaiq - Arabic HTR with expert review" (40 steps, 5 stages).

Drawn the way the n8n canvas shows it (left to right, one box per step), so the site works offline and
never shows a model or vendor name: node names that contain one are given neutral names here
(e.g. "AI reader transcribes"). Each node gets a delay (--d) so the pitch can light the flow in order.
"""
import html

GX, GY = 160, 150          # grid spacing
BOX = 64                   # node box size

ICONS = {
    "trigger": '<circle r="13" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M0 -7V0L5 4" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>',
    "set": '<path d="M-12 -7H12M-12 0H12M-12 7H12" stroke="currentColor" stroke-width="2.2"/><circle cx="-4" cy="-7" r="3" fill="currentColor"/><circle cx="5" cy="0" r="3" fill="currentColor"/><circle cx="-2" cy="7" r="3" fill="currentColor"/>',
    "drive": '<path d="M-14 -9H-3L0 -5H14V10H-14Z" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/>',
    "image": '<rect x="-13" y="-10" width="26" height="20" rx="2" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M-10 7L-3 -1L3 5L7 1L11 7" fill="none" stroke="currentColor" stroke-width="2"/>',
    "file": '<path d="M-9 -12H4L10 -6V12H-9Z" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/><path d="M-5 -2H6M-5 3H6M-5 8H2" stroke="currentColor" stroke-width="1.8"/>',
    "code": '<text x="0" y="6" text-anchor="middle" font-size="19" font-weight="700" fill="currentColor" font-family="IBM Plex Sans, sans-serif">{ }</text>',
    "reader": '<rect x="-10" y="-10" width="20" height="20" fill="currentColor"/><rect x="-10" y="-10" width="20" height="20" fill="currentColor" transform="rotate(45)"/><circle r="4" fill="#18233a"/>',
    "checker": '<rect x="-10" y="-10" width="20" height="20" fill="currentColor"/><rect x="-10" y="-10" width="20" height="20" fill="currentColor" transform="rotate(45)"/><path d="M-5 0L-1 4L6 -4" fill="none" stroke="#18233a" stroke-width="2.6"/>',
    "if": '<path d="M0 -13L13 0L0 13L-13 0Z" fill="none" stroke="currentColor" stroke-width="2.4"/>',
    "switch": '<path d="M-12 0H-2M-2 0L10 -10M-2 0L10 -3M-2 0L10 4M-2 0L10 11" fill="none" stroke="currentColor" stroke-width="2.2"/>',
    "merge": '<path d="M-12 -9C0 -9 0 0 12 0M-12 9C0 9 0 0 12 0" fill="none" stroke="currentColor" stroke-width="2.4"/>',
    "table": '<rect x="-13" y="-10" width="26" height="20" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M-13 -3H13M-13 4H13M-4 -10V10M5 -10V10" stroke="currentColor" stroke-width="1.6"/>',
    "mail": '<rect x="-13" y="-9" width="26" height="18" rx="2" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M-12 -8L0 2L12 -8" fill="none" stroke="currentColor" stroke-width="2.2"/>',
    "stop": '<rect x="-8" y="-8" width="16" height="16" rx="2" fill="currentColor"/>',
}


def _wrap(label, width=17):
    words, lines, cur = label.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    return lines[:3]


def diagram(nodes, edges, stubs=(), title="", step=0.18, start=0.5):
    """nodes: (id, label, kind, col, row, role) role in {"", "ai", "human", "board", "faded"}
    edges: (from, to, label, style) style in {"", "loop", "branch"}
    stubs: (id, text, col, row) small text endpoints (in / out of the stage)."""
    pos, out = {}, []
    order = {n[0]: i for i, n in enumerate(nodes)}
    cols = [n[3] for n in nodes] + [s[2] for s in stubs]
    rows = [n[4] for n in nodes] + [s[3] for s in stubs]
    minc, maxc, minr, maxr = min(cols), max(cols), min(rows), max(rows)
    loops = any(e[3] == "loop" for e in edges)
    pad_x, pad_top, pad_bot = 90, (130 if loops else 50), 110
    W = (maxc - minc) * GX + 2 * pad_x
    H = (maxr - minr) * GY + pad_top + pad_bot
    X = lambda c: pad_x + (c - minc) * GX
    Y = lambda r: pad_top + BOX / 2 + (r - minr) * GY
    for n in nodes:
        pos[n[0]] = (X(n[3]), Y(n[4]))
    for s in stubs:
        pos[s[0]] = (X(s[2]), Y(s[3]))

    # edges first, under the nodes
    for a, b, lbl, style in edges:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        d = order.get(a, 0) * step + start
        sx = x1 + (BOX / 2 if a in order else 40)
        ex = x2 - (BOX / 2 if b in order else 46)
        if style == "loop":
            # loops run above the row, where there are no labels
            top = min(y1, y2) - BOX / 2
            high = top - 85
            path = f"M{x1:.0f} {top:.0f} C{x1:.0f} {high:.0f} {x2:.0f} {high:.0f} {x2:.0f} {top - 8:.0f}"
            out.append(f'<path class="ed loop" style="--d:{d:.2f}s" d="{path}"/>'
                       f'<path class="ed-head loop" d="M{x2 - 6:.0f} {top - 18:.0f}L{x2:.0f} {top - 8:.0f}L{x2 + 6:.0f} {top - 18:.0f}"/>')
            if lbl:
                out.append(f'<text class="ed-lbl loop" x="{(x1 + x2) / 2:.0f}" y="{high + 14:.0f}" text-anchor="middle">{html.escape(lbl)}</text>')
            continue
        mx = (sx + ex) / 2
        path = f"M{sx:.0f} {y1:.0f} C{mx:.0f} {y1:.0f} {mx:.0f} {y2:.0f} {ex:.0f} {y2:.0f}"
        cls = "ed" + (" branch" if style == "branch" else "") + (" faint" if style == "faint" else "")
        out.append(f'<path class="{cls}" style="--d:{d:.2f}s" d="{path}"/>'
                   f'<circle class="ed-dot" cx="{ex:.0f}" cy="{y2:.0f}" r="3.5"/>')
        if lbl:
            out.append(f'<text class="ed-lbl" x="{mx:.0f}" y="{(y1 + y2) / 2 - 8:.0f}" text-anchor="middle">{html.escape(lbl)}</text>')

    for i, (nid, label, kind, c, r, role) in enumerate(nodes):
        x, y = pos[nid]
        d = i * step + start
        shape = (f'<path d="M{-BOX/2 + 22} {-BOX/2}H{BOX/2 - 8}a8 8 0 0 1 8 8V{BOX/2 - 8}a8 8 0 0 1 -8 8H{-BOX/2 + 22}a22 32 0 0 1 0 -{BOX}Z" class="box"/>'
                 if kind == "trigger" else
                 f'<rect x="{-BOX/2}" y="{-BOX/2}" width="{BOX}" height="{BOX}" rx="8" class="box"/>')
        lines = _wrap(label)
        txt = "".join(f'<tspan x="0" dy="{0 if k == 0 else 17}">{html.escape(t)}</tspan>' for k, t in enumerate(lines))
        out.append(f'<g class="nd {kind} {role}" style="--d:{d:.2f}s" transform="translate({x:.0f} {y:.0f})">'
                   f'{shape}<g class="ic">{ICONS[kind]}</g>'
                   f'<text class="nd-lbl" y="{BOX / 2 + 22}" text-anchor="middle">{txt}</text></g>')

    for sid, text, c, r in stubs:
        x, y = pos[sid]
        out.append(f'<g class="stub" transform="translate({x:.0f} {y:.0f})"><rect x="-46" y="-15" width="92" height="30" rx="15"/>'
                   f'<text y="5" text-anchor="middle">{html.escape(text)}</text></g>')

    aria = html.escape(title or "Workflow diagram")
    return (f'<svg class="wf" direction="ltr" style="max-width:{W * 0.8:.0f}px" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="{aria}">' + "".join(out) + "</svg>")


# ---------- the five stages of the real workflow ----------

def stage1():
    n = [("t1", "Every 10 minutes", "trigger", 0, 0, ""),
         ("t2", "Test now", "trigger", 0, 1, "faded"),
         ("s", "Settings", "set", 1, 0.5, ""),
         ("f", "Find next scan in Inbox", "drive", 2, 0.5, ""),
         ("m", "Move scan to In review", "drive", 3, 0.5, ""),
         ("b", "Board: being read", "table", 4, 0.5, "board"),
         ("d", "Download scan", "drive", 5, 0.5, ""),
         ("k", "Shrink scan", "image", 6, 0.5, ""),
         ("x", "Scan to base64", "file", 7, 0.5, "")]
    e = [("t1", "s", "", ""), ("t2", "s", "", "faint"), ("s", "f", "", ""), ("f", "m", "", ""), ("m", "b", "", ""),
         ("b", "d", "", ""), ("d", "k", "", ""), ("k", "x", "", "")]
    return diagram(n, e, title="Stage 1: pick up a new scan, 9 steps")


def stage2():
    n = [("l", "List example files", "code", 0, 0.5, ""),
         ("f", "Find example files", "drive", 1, 0.5, ""),
         ("p", "Pick example files", "code", 2, 0.5, ""),
         ("d", "Download example files", "drive", 3, 0.5, ""),
         ("i", "Image or text?", "if", 4, 0.5, ""),
         ("s", "Shrink example images", "image", 5, 0, ""),
         ("m", "Put examples back together", "merge", 6, 0.5, ""),
         ("x", "Examples to base64", "file", 7, 0.5, ""),
         ("c", "Collect examples", "code", 8, 0.5, "")]
    e = [("l", "f", "", ""), ("f", "p", "", ""), ("p", "d", "", ""), ("d", "i", "", ""),
         ("i", "s", "image", "branch"), ("i", "m", "text", "branch"), ("s", "m", "", ""), ("m", "x", "", ""), ("x", "c", "", "")]
    return diagram(n, e, title="Stage 2: load the expert-approved example pages, 9 steps")


def stage3():
    n = [("b", "Build reader request", "code", 0, 0, ""),
         ("r", "AI reader transcribes", "reader", 1, 0, "ai"),
         ("rt", "Read transcription", "code", 2, 0, ""),
         ("bc", "Build checker request", "code", 3, 0, ""),
         ("c", "AI checker checks", "checker", 4, 0, "ai"),
         ("rc", "Read check", "code", 5, 0, ""),
         ("q", "Problems found? Try again", "if", 6, 0, "")]
    s = [("in", "examples + scan", -1, 0), ("out", "to the expert", 7, 0)]
    e = [("in", "b", "", ""), ("b", "r", "", ""), ("r", "rt", "", ""), ("rt", "bc", "", ""), ("bc", "c", "", ""),
         ("c", "rc", "", ""), ("rc", "q", "", ""), ("q", "out", "", ""), ("q", "b", "retry with the checker’s notes", "loop")]
    return diagram(n, e, s, title="Stage 3: the AI reader transcribes and the AI checker checks, 7 steps")


def stage4():
    n = [("p", "Prepare review email", "code", 0, 1.5, ""),
         ("b", "Board: with the expert", "table", 1, 1.5, "board"),
         ("e", "Email the expert and wait", "mail", 2, 1.5, "human"),
         ("r", "Read expert answer", "code", 3, 1.5, ""),
         ("d", "Decision", "switch", 4, 1.5, "human")]
    s = [("a", "Approve", 5.2, 0), ("t", "Re-transcribe", 5.2, 1), ("j", "Reject", 5.2, 2), ("n", "No answer", 5.2, 3)]
    e = [("p", "b", "", ""), ("b", "e", "", ""), ("e", "r", "", ""), ("r", "d", "", ""),
         ("d", "a", "", "branch"), ("d", "t", "", "branch"), ("d", "j", "", "branch"), ("d", "n", "", "branch")]
    return diagram(n, e, s, title="Stage 4: the expert reviews by email, 5 steps")


def stage5():
    n = [("d", "Decision", "switch", 0, 1.5, "faded"),
         ("m", "Make .txt file", "file", 1, 0, ""),
         ("s", "Save .txt to Results", "drive", 2, 0, ""),
         ("v", "Move scan to Results", "drive", 3, 0, ""),
         ("ba", "Board: approved", "table", 4, 0, "board"),
         ("bt", "Board: back to the reader", "table", 1, 1, "board"),
         ("f", "Expert note as feedback", "code", 2, 1, ""),
         ("rj", "Rejected: scan stays in In review", "stop", 1, 2, "faded"),
         ("br", "Board: rejected", "table", 2, 2, "board"),
         ("na", "No answer after 7 days", "stop", 1, 3, "faded"),
         ("bn", "Board: no answer", "table", 2, 3, "board")]
    s = [("back", "to the AI reader", 3.2, 1)]
    e = [("d", "m", "approve", "branch"), ("m", "s", "", ""), ("s", "v", "", ""), ("v", "ba", "", ""),
         ("d", "bt", "", "branch"), ("bt", "f", "", ""), ("f", "back", "", ""),
         ("d", "rj", "", "branch"), ("rj", "br", "", ""), ("d", "na", "", "branch"), ("na", "bn", "", "")]
    return diagram(n, e, s, title="Stage 5: save the approved text, or send the page back, 10 steps")


def overview():
    """Five stage blocks, the retry loop and the send-back loop, and the board table."""
    blocks = [("١", "التقاط صفحة", "Pick up a scan", 9), ("٢", "أمثلة الخبير", "Load examples", 9),
              ("٣", "القارئ والمدقق", "Read and check", 7), ("٤", "الخبير يقرّر", "Expert reviews", 5),
              ("٥", "الحفظ", "Save", 10)]
    W, bw, bh, gap, y0 = 1264, 196, 150, 55, 80
    out = []
    xs = [30 + i * (bw + gap) for i in range(5)]
    for i, (num, ar, en, k) in enumerate(blocks):
        x = xs[i]
        cls = "blk" + (" ai" if i == 2 else "") + (" human" if i == 3 else "")
        out.append(f'<g class="nd {cls}" style="--d:{0.4 + i * 0.35:.2f}s" transform="translate({x} {y0})">'
                   f'<rect width="{bw}" height="{bh}" rx="10" class="box"/>'
                   f'<text x="{bw/2}" y="44" text-anchor="middle" class="b-num">{num}</text>'
                   f'<text x="{bw/2}" y="86" text-anchor="middle" class="b-ar">{ar}</text>'
                   f'<text x="{bw/2}" y="112" text-anchor="middle" class="b-en">{en}</text>'
                   f'<text x="{bw/2}" y="136" text-anchor="middle" class="b-k">{k} steps</text></g>')
        if i < 4:
            x1, x2, y = x + bw, xs[i + 1], y0 + bh / 2
            out.append(f'<path class="ed" style="--d:{0.55 + i * 0.35:.2f}s" d="M{x1} {y}H{x2 - 6}"/><circle class="ed-dot" cx="{x2 - 6}" cy="{y}" r="4"/>')
    # retry loop on stage 3, send-back loop from 5 to 3
    x3 = xs[2] + bw / 2
    out.append(f'<path class="ed loop" style="--d:2.0s" d="M{x3 + 40} {y0} C{x3 + 40} {y0 - 50} {x3 - 40} {y0 - 50} {x3 - 40} {y0 - 4}"/>'
               f'<text class="ed-lbl loop" x="{x3}" y="{y0 - 38}" text-anchor="middle">retry</text>')
    x5 = xs[4] + bw / 2
    yb = y0 + bh
    out.append(f'<path class="ed loop" style="--d:2.3s" d="M{x5} {yb} C{x5} {yb + 80} {x3} {yb + 80} {x3} {yb + 6}"/>'
               f'<text class="ed-lbl loop" x="{(x3 + x5) / 2}" y="{yb + 76}" text-anchor="middle">send back with the expert’s note</text>')
    # board table under everything
    yt = yb + 110
    out.append(f'<g class="nd board" style="--d:2.6s" transform="translate({W/2 - 160} {yt})"><rect width="320" height="46" rx="8" class="box"/>'
               f'<text x="160" y="29" text-anchor="middle" class="b-en">Board: stage of each page → website</text></g>')
    for i in (0, 2, 3, 4):
        out.append(f'<path class="ed faint" d="M{xs[i] + bw/2} {yb} L{W/2} {yt}"/>')
    return (f'<svg class="wf wf-over" direction="ltr" viewBox="0 0 {W} {yt + 70}" role="img" aria-label="The whole workflow: five stages, a retry loop, a send-back loop and the board table">'
            + "".join(out) + "</svg>")


STAGES = [
    {"n": 1, "svg": stage1, "title_en": "One page per run",
     "ar": "صفحة واحدة في كل دورة",
     "en": "Every 10 minutes, one scan leaves the Inbox, never to be read twice.",
     "long_ar": "كل عشر دقائق يأخذ سير العمل صورة واحدة من مجلد الوارد وينقلها إلى «قيد المراجعة»، فلا تُقرأ مرتين. ثم ينزّل الصورة، ويصنع منها نسخة عمل لا يزيد عرضها على ٢٤٠٠ بكسل، ويحوّلها إلى نص base64 لتُرسل داخل الطلب. لا تتغيّر الصورة الأصلية في Drive.",
     "long_en": "Every 10 minutes the workflow takes one image from the Inbox folder and moves it to In review, so it is never read twice. It downloads the scan, makes a working copy of at most 2400 px, and turns it into base64 text so it can travel inside the request. The original in Drive is not changed."},
    {"n": 2, "svg": stage2, "title_en": "Examples approved by the expert",
     "ar": "أمثلة يعتمدها الخبير",
     "en": "Three expert-approved pages travel with every request as worked examples.",
     "long_ar": "يقرأ سير العمل من الإعدادات أسماء الصفحات المعتمدة (٠١٨٨ و٠١٠٠ و٠٠٣٨)، ويجد لكل منها صورتها ونصها في مكتبة Drive، ثم يصغّر الصور ويجمع كل صورة مع نصها. هذه الأزواج تُعرض على القارئ الآلي أمثلةً قبل الصفحة الجديدة.",
     "long_en": "The workflow reads the names of the approved pages from Settings (0188, 0100 and 0038), finds each one’s image and text in the Drive library, shrinks the images and pairs every image with its text. These pairs are shown to the AI reader as examples before the new page."},
    {"n": 3, "svg": stage3, "title_en": "The reader writes, the checker doubts",
     "ar": "القارئ يكتب، والمدقق يشكّ",
     "en": "The checker scores each reading; on problems, the reader tries again.",
     "long_ar": "يكتب القارئ الآلي النص سطرًا بسطر. ثم يقارنه المدقق الآلي بالصورة، فيعلّم الأسطر المشكوك فيها ويعطي درجة ثقة. تُخفض الثقة إلى ٢٠٪ عند خلل خطير (نص فارغ، أو سطر مكرر)، وإذا وُجدت مشكلات يقرأ القارئ الصفحة مرة أخرى بملاحظات المدقق، ويُحفظ أفضل نص.",
     "long_en": "The AI reader writes the text line by line. The AI checker then compares it with the scan, flags doubtful lines and gives a confidence score. A serious flag (empty text, a repeated line) caps confidence at 20%. If problems are found, the reader tries once more with the checker’s notes, and the best version is kept."},
    {"n": 4, "svg": stage4, "title_en": "The expert decides",
     "ar": "الخبير يقرّر",
     "en": "An email with the text already filled in; the workflow waits up to 7 days.",
     "long_ar": "يصل إلى الخبير بريد فيه درجة الثقة وملاحظات المدقق ورابط الصورة، وزر يفتح نموذجًا فيه النص جاهزًا. يصحّح ويختار: اعتماد، أو إعادة مع ملاحظة، أو رفض. ينتظر سير العمل حتى ٧ أيام؛ لا يُحفظ شيء دون قرار الخبير.",
     "long_en": "The expert receives an email with the confidence, the checker’s notes, a link to the scan and a button to a form with the text already filled in. They correct it and choose: approve, re-transcribe with a note, or reject. The workflow waits up to 7 days; nothing is saved without the expert’s decision."},
    {"n": 5, "svg": stage5, "title_en": "Save, or send back with a note",
     "ar": "الحفظ، أو العودة مع ملاحظة",
     "en": "Approved text joins its scan; a note sends the page back.",
     "long_ar": "عند الاعتماد يصير النص ملف .txt يُحفظ في مجلد النتائج وتنتقل الصورة بجانبه: زوج جاهز للتدريب. وعند الإعادة تعود ملاحظة الخبير إلى القارئ الآلي. وفي كل مرحلة تكتب خطوات «Board» حالة الصفحة في جدول تقرؤه لوحة الفريق على الموقع.",
     "long_en": "On approval the text becomes a .txt file saved in Results, and the scan moves next to it: a pair ready for training. On re-transcribe, the expert’s note goes back to the AI reader. At every stage the Board steps write the page’s status to a table that the team board on the website reads."},
]
