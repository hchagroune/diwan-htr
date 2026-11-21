"""The /pitch page: 9 full-screen slides, Arabic headline + one English line, at most 35 words each.

Design: a night court of Algiers. Indigo field with a faint eight-point-star lattice, brass Amiri headlines,
parchment for anything quoted from a deed, one ink reveal per slide. Each slide carries one picture made of
the data itself (a grid of websites, a strip of reels, the reading loop, nested arches).
Facts come only from the pitch document; estimates are labelled. Never name an AI model or vendor here.
"""

STAR = ('<rect x="-{r}" y="-{r}" width="{d}" height="{d}" fill="{c}"/>'
        '<rect x="-{r}" y="-{r}" width="{d}" height="{d}" fill="{c}" transform="rotate(45)"/>')


def star(r, c):
    return STAR.format(r=r, d=2 * r, c=c)


def build(DOCS, page, t, seal, CREATORS, SITE_URL):
    qr = (DOCS / "assets" / "qr-demo.svg").read_text(encoding="utf-8")
    target = SITE_URL + "demo/?page=0188"
    qr = qr.replace(f'aria-label="{target}"', 'aria-label="QR code: try the demo on page 0188"')

    def slide(n, cls, body, notes_ar, notes_en):
        return (f'<section class="slide {cls}" id="s{n}" aria-roledescription="slide" aria-label="{n} / 9" data-n="{n}">'
                f'<div class="slide-in">{body}</div>'
                f'<aside class="notes" hidden>{t(notes_ar, notes_en, tag="p")}</aside></section>')

    def h(ar, en):
        return (f'<h2 class="s-ar ink" lang="ar" dir="rtl">{ar}</h2>'
                f'<p class="s-en rise" lang="en" dir="ltr">{en}</p>')

    # ---- slide 2 picture: 1,000 cells = all websites; 6 lit = Arabic (0.6%)
    cells = []
    lit = {412, 413, 452, 453, 492, 493}
    for i in range(1000):
        x, y = (i % 40) * 12, (i // 40) * 12
        cells.append(f'<rect x="{x}" y="{y}" width="9" height="9" rx="1.5" class="{"lit" if i in lit else "dim"}"/>')
    grid = (f'<svg class="s-grid" viewBox="0 0 477 297" role="img" aria-label="1,000 squares; 6 of them, 0.6%, are Arabic websites">'
            f'{"".join(cells)}</svg>')

    # ---- slide 3 picture: 125 microfilm reels
    reels = []
    for i in range(125):
        cx, cy = 14 + (i % 25) * 26, 14 + (i // 25) * 26
        reels.append(f'<g transform="translate({cx} {cy})"><circle r="11" class="reel"/><circle r="3.2" class="hub"/></g>')
    reelsvg = (f'<svg class="s-reels" viewBox="0 0 650 130" role="img" aria-label="125 microfilm reels">{"".join(reels)}</svg>')

    # ---- slide 4 picture: the reading loop
    steps = [("الصفحة", "scan"), ("القارئ الآلي", "AI reader"), ("المدقق الآلي", "AI checker"),
             ("الخبير", "expert"), ("الأرشيف", "archive")]
    loop_nodes = "".join(
        f'<li class="{"expert" if k == 3 else ""}"><span class="mark" aria-hidden="true">'
        f'<svg viewBox="-14 -14 28 28">{star(8, "currentColor")}</svg></span>'
        f'<b lang="ar">{ar}</b><small lang="en">{en}</small></li>' for k, (ar, en) in enumerate(steps))

    # ---- slide 6 picture: estimated learning curve (Lucas, Salah & Vidal-Gorène 2022)
    pts = [(0, 21.24), (80, 9.99), (160, 7.7)]
    X = lambda x: 60 + x * 2.6
    Y = lambda y: 30 + (24 - y) * 9
    path = " ".join(("M" if i == 0 else "L") + f"{X(x):.0f} {Y(y):.0f}" for i, (x, y) in enumerate(pts))
    area = path + f" L{X(160):.0f} 246 L{X(0):.0f} 246 Z"
    dots = "".join(
        f'<g transform="translate({X(x):.0f} {Y(y):.0f})">{star(6, "#e2bd55")}</g>'
        f'<text x="{X(x):.0f}" y="{Y(y) - 18:.0f}" class="lbl" text-anchor="middle">{y:g}%</text>' for x, y in pts)
    chart = f"""<svg class="s-chart" viewBox="0 0 520 270" role="img" aria-label="Estimated character error: 21% at 0 verified lines, 10% at 80, 7.7% at 160">
  <path d="{area}" fill="#e2bd55" fill-opacity="0.08"/>
  <line x1="60" y1="246" x2="500" y2="246" class="axis"/>
  <path d="{path}" fill="none" stroke="#e2bd55" stroke-width="3" stroke-dasharray="9 7" class="draw"/>{dots}
  <text x="{X(0):.0f}" y="266" class="tick" text-anchor="middle">0</text>
  <text x="{X(80):.0f}" y="266" class="tick" text-anchor="middle">80</text>
  <text x="{X(160):.0f}" y="266" class="tick" text-anchor="middle">160 lines</text>
</svg>"""

    # ---- slide 7 picture: three nested horseshoe arches, smallest first
    def arch(w, h_):
        r = w / 2 + 6
        return f"M {-w/2:.0f} 0 L {-w/2:.0f} {-h_:.0f} A {r:.0f} {r:.0f} 0 1 1 {w/2:.0f} {-h_:.0f} L {w/2:.0f} 0"
    arches = (f'<svg class="s-arches" viewBox="-330 -545 660 565" aria-hidden="true">'
              f'<path d="{arch(600, 170)}" class="a3"/><path d="{arch(400, 120)}" class="a2"/><path d="{arch(200, 70)}" class="a1"/></svg>')

    s = []
    s.append(slide(1, "s-hook", f"""
      <div class="parch rise">
        <div class="crop s-crop"><img src="../assets/img/motto-line9.jpg" alt="" onload="this.parentNode.classList.add('has-img')"></div>
        <p class="s-deed" lang="ar" dir="rtl">وبالمحكمة الحنفية من بلد الجزائر المحمية بالله تعالى</p>
        <p class="parch-src" lang="en" dir="ltr">Line 9 · deed 0188 · Hanafi court of Algiers · 1841</p>
      </div>
      <p class="s-q ink" lang="ar" dir="rtl">من يستطيع قراءتها اليوم؟</p>
      <p class="s-en rise" lang="en" dir="ltr">Who can still read it?</p>""",
        "ابدأ بالسكوت. اقرأ السطر بصوت عالٍ. هذا السطر من الوثيقة ٠١٨٨، كتبه كاتب المحكمة الحنفية في ٣ رجب ١٢٥٧ هـ. الكاتب كتب «تعلى»، ونعرضها هنا «تعالى».",
        "Open in silence, then read the line aloud. It is line 9 of deed 0188, written by the Hanafi court scribe on 3 Rajab 1257 AH. The scribe wrote تعلى; the slide shows تعالى."))

    s.append(slide(2, "", h("العربية شبه غائبة عن الشبكة، وخطّها اليدوي أغيب", "Arabic is barely online; its handwriting even less.") + f"""
      <div class="s-two rise">
        <figure class="s-fig">{grid}
          <figcaption lang="en" dir="ltr"><b>0.6%</b> of websites use Arabic <span class="src">W3Techs, Nov 2026</span></figcaption></figure>
        <div class="s-big">
          <div class="num" lang="en" dir="ltr">≈0.004%</div>
          <p lang="en" dir="ltr">of OpenITI’s Arabic text is handwriting</p>
          <p class="src" lang="en" dir="ltr"><span class="est">Estimate</span> · ours</p>
        </div>
      </div>""",
        "المربعات ألف، والمضيئة ستة: هذه حصة العربية من المواقع. OpenITI فيه ٢٫٣١ مليار كلمة عربية، منها ١٠١٬٣٣٦ فقط من خط يد منسوخ؛ النسبة ≈٠٫٠٠٤٪ حسابنا نحن، أي أقل من جزء من مربع واحد هنا.",
        "A thousand squares, six lit: Arabic’s share of websites. OpenITI holds 2.31 billion Arabic tokens; only 101,336 come from transcribed handwriting. The ≈0.004% is our arithmetic: less than a sliver of one square here."))

    s.append(slide(3, "", h("تراث مصوَّر… لم يُقرأ بعد", "Filmed, catalogued, and still unread.") + f"""
      <figure class="s-fig wide rise">{reelsvg}
        <figcaption lang="en" dir="ltr"><b>125</b> microfilm reels of Algiers deeds, filmed by operators who knew no Arabic <span class="src">Grangaud 2026</span></figcaption></figure>
      <div class="s-big inline rise">
        <div class="num" lang="en" dir="ltr">≈30,000</div>
        <p lang="en" dir="ltr">Ottoman court registers survive <span class="src"><span class="est">Estimate</span> · ISAM</span></p>
      </div>""",
        "كل دائرة بكرة. ١٢٥ بكرة في الأرشيف الوطني لما وراء البحار، بحسب Grangaud في مجلة إنسانيات ١١١. الرقم ٣٠ ألف تقدير من مركز ISAM، وهو يحتفظ بنسخ رقمية لـ ٢٣٬٧٥٦ سجلًا. لا تقل «٥ ملايين مخطوط».",
        "Each circle is a reel: 125 at ANOM, per Grangaud, Insaniyat 111. 30,000 is ISAM’s estimate; ISAM holds 23,756 in digital copies. Do not say “5 million manuscripts”."))

    s.append(slide(4, "s-solution", h("قارئ آلي، مدقق آلي، وخبير يقرّر", "Every approved line becomes training data.") + f"""
      <div class="s-loopwrap rise">
        <ol class="s-loop" dir="rtl">{loop_nodes}</ol>
        <svg class="s-back" viewBox="0 0 1000 60" preserveAspectRatio="none" aria-hidden="true"><path d="M 300 6 C 300 54, 700 54, 700 6" fill="none" stroke="#f0b48f" stroke-width="2.5" stroke-dasharray="6 6"/><path d="M 692 16 L 700 4 L 708 16" fill="none" stroke="#f0b48f" stroke-width="2.5"/></svg>
        <p class="s-backlbl" lang="ar" dir="rtl">إعادة مع ملاحظة</p>
      </div>
      <div class="s-try rise">
        <button class="btn s-demo" type="button" data-open-demo><span lang="ar">جرّب الآن</span><span lang="en">Try it</span></button>
        <figure class="s-qr">{qr}<figcaption lang="en">Scan to try</figcaption></figure>
      </div>""",
        "اضغط «جرّب الآن» لتفتح العرض هنا، أو اطلب من الحضور مسح الرمز: يفتح على هواتفهم محاولة حقيقية على الصفحة ٠١٨٨ (يحتاج الهاتف إلى إنترنت). أغلق العرض بـ Esc.",
        "Press Try it to open the demo here, or invite the room to scan: it opens a real attempt on page 0188 on their phones (phones need internet). Close the demo with Esc."))

    s.append(slide(5, "", h("كل سطر يعتمده الخبير يعلّم الآلة", "Each verified line teaches the machine to read Maghrebi script.") + f"""
      <div class="s-drop rise" lang="en" dir="ltr">
        <div class="bar b1"><span>21%</span></div>
        <div class="arrow" aria-hidden="true">→</div>
        <div class="bar b2"><span>10%</span></div>
      </div>
      <p class="s-cap rise" lang="en" dir="ltr">character errors after about 80 verified lines <span class="src">Lucas, Salah &amp; Vidal-Gorène 2022</span></p>""",
        "على الخط المغربي نزل الخطأ من ٢١٫٢٤٪ إلى ٩٫٩٩٪ بعد نحو ٨٠ سطرًا، وإلى ٧٫٧٪ بعد نحو ١٦٠. ونقص وقت المراجعة ٤٢٪.",
        "On Maghrebi script, character error fell from 21.24% to 9.99% after about 80 lines, and to 7.7% after about 160. Proofreading time fell 42%."))

    s.append(slide(6, "", h("التجربة الأولية: ثلاث صفحات حقيقية", "Real pilot, estimated curve.") + f"""
      <div class="s-split rise">
        <ul class="s-facts" lang="en" dir="ltr">
          <li><b>3 pages</b><span>Algiers 2 · Annaba 1</span></li>
          <li><b>85–88% → 92%</b><span>checker confidence, after the expert’s note</span></li>
          <li><b>33–70% → 3–12%</b><span><span class="est">Estimate</span> · errors, off the shelf → fine-tuned</span></li>
        </ul>
        <figure>{chart}<figcaption class="src" lang="en" dir="ltr"><span class="est">Estimate</span> · Lucas 2022; KITAB-Bench 2025</figcaption></figure>
      </div>""",
        "الحقيقي: ثلاث صفحات؛ ثقة المدقق ٨٥–٨٨٪، وارتفعت إلى ٩٢٪ في الصفحة ٠١٨٨ بعد ملاحظة الخبير. المنحنى والأرقام الأخرى تقديرات من دراسات منشورة، وليست نتائجنا.",
        "Real: three pages; checker confidence 85–88%, rising to 92% on page 0188 after the expert’s note. The curve and the other figures are estimates from published studies, not our results."))

    s.append(slide(7, "s-vision", h("من سجلات الجزائر إلى أرشيفات العربية في العالم", "From Algiers’ deeds to the world’s Arabic archives.") + f"""
      <div class="s-archwrap rise">{arches}
        <span class="al l1" lang="ar">وثائق الجزائر</span>
        <span class="al l2" lang="ar">نموذج مفتوح للخط المغربي</span>
        <span class="al l3" lang="ar">أرشيفات العربية في العالم</span>
      </div>""",
        "الخطوة الأولى صغيرة وحقيقية: صفحات الجزائر. كل سطر معتمد يقرّبنا من نموذج مفتوح، ثم من أرشيفات العربية كلها.",
        "The first step is small and real: the Algiers pages. Every approved line brings an open model closer, then the world’s Arabic archives."))

    why = [("وكيلان آليان وخبير بشري", '<svg viewBox="-30 -20 60 40"><g transform="translate(-16 0)">' + star(7, "#e2bd55") + '</g><g transform="translate(0 0)">' + star(7, "#e2bd55") + '</g><circle cx="17" r="8" fill="#16684e"/></svg>'),
           ("منسَّق في n8n", '<svg viewBox="-30 -20 60 40"><circle cx="-18" r="6" fill="none" stroke="#e2bd55" stroke-width="2.5"/><circle cx="0" r="6" fill="none" stroke="#e2bd55" stroke-width="2.5"/><circle cx="18" r="6" fill="none" stroke="#e2bd55" stroke-width="2.5"/><path d="M-12 0H-6M6 0H12" stroke="#e2bd55" stroke-width="2.5"/></svg>'),
           ("أرشيف حقيقي، لا بيانات تجريبية", '<svg viewBox="-30 -20 60 40"><rect x="-20" y="-14" width="40" height="28" rx="2" fill="#e9dcc0"/><path d="M-14 -6H14M-14 0H14M-14 6H6" stroke="#5a4a33" stroke-width="2"/></svg>')]
    whyl = "".join(f'<li>{svg}<span lang="ar">{ar}</span></li>' for ar, svg in why)
    s.append(slide(8, "", h("لماذا يعنيكم، د. مراد بوعاش وطلبة الذكاء الاصطناعي الوكيلي؟", "Agentic AI in practice.") +
        f'<ul class="s-why rise" dir="rtl">{whyl}</ul>',
        "اربط بالدورة: وكيل يكتب، ووكيل يشكّ ويطلب إعادة، وإنسان في الحلقة يقرر. كل ذلك في n8n.",
        "Tie it to the course: one agent writes, one doubts and asks for a re-read, and a human in the loop decides. All of it in n8n."))

    sigs = "".join(f'<div class="s-sig">{seal(110, c["ar"].split()[0], color="#e2bd55", label=c["en"])}'
                   f'<span lang="ar">{c["ar"]}</span></div>' for c in CREATORS)
    s.append(slide(9, "s-close", f"""
      <p class="s-ask rise" lang="ar" dir="rtl">طلبنا: [ يُكتب لاحقًا ]<span lang="en" dir="ltr">Our ask: [ to be written ]</span></p>
      <p class="s-motto ink" lang="ar" dir="rtl">الجزائر المحمية بالله</p>
      <div class="s-sigs rise">{sigs}</div>""",
        "اكتبوا الطلب قبل يوم العرض: ما الذي تريدونه من الحضور تحديدًا؟ ثم اختم بالعبارة، واترك الصمت.",
        "Write the ask before the day: what exactly do you want from the room? Then close on the motto and let it rest."))

    tiles = "".join(f'<li><svg viewBox="-10 -10 20 20" aria-hidden="true">{star(6, "currentColor")}</svg></li>' for _ in range(9))
    lattice_star = ('<rect x="-18" y="-18" width="36" height="36"/>'
                    '<rect x="-18" y="-18" width="36" height="36" transform="rotate(45)"/>')
    body = f"""
<link rel="stylesheet" href="../assets/pitch.css">
<div class="deck" id="deck" tabindex="-1">
  <svg class="lattice" aria-hidden="true"><defs><pattern id="lat" width="88" height="88" patternUnits="userSpaceOnUse">
    <g transform="translate(44 44)" fill="none" stroke="#e2bd55" stroke-width="1">{lattice_star}</g>
    <path d="M0 44H18M70 44H88M44 0V18M44 70V88" stroke="#e2bd55" stroke-width="1"/></pattern></defs>
    <rect width="100%" height="100%" fill="url(#lat)"/></svg>
  <ol class="progress" id="progress" aria-hidden="true">{tiles}</ol>
  {''.join(s)}
  <div class="deck-bar">
    <a class="deck-home" href="../">{t("الرئيسية", "Welcome")}</a>
    <button type="button" class="deck-btn" id="prev" aria-label="Previous slide">‹</button>
    <span class="deck-count" id="count" aria-live="polite" dir="ltr">1 / 9</span>
    <button type="button" class="deck-btn" id="next" aria-label="Next slide">›</button>
    <button type="button" class="deck-btn" id="notesBtn" aria-pressed="false">{t("ملاحظات (N)", "Notes (N)")}</button>
    <button type="button" class="deck-btn" id="fsBtn">{t("ملء الشاشة (F)", "Full screen (F)")}</button>
    <button class="deck-btn" type="button" data-lang-switch lang="en">English</button>
  </div>
</div>
<dialog class="demo-overlay" id="demoOverlay" aria-label="Demo">
  <iframe title="Demo" data-src="../demo/?embed=1"></iframe>
  <button class="btn btn-quiet demo-close" type="button" data-close-demo>{t("إغلاق (Esc)", "Close (Esc)")}</button>
</dialog>"""
    page("pitch/", "العرض · ديوان الوثائق", "Pitch · Dīwān al-Wathāʾiq",
         "Nine-slide pitch for Dīwān al-Wathāʾiq.", body, scripts=("pitch.js",), current="pitch/", bare=True)
