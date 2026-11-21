"""The /pitch page: 9 full-screen slides, Arabic headline + one English line, at most 35 words each.

Facts come only from the pitch document. Estimates are labelled "تقدير / estimate".
Never name an AI model or vendor here.
"""


def build(DOCS, page, t, seal, CREATORS):
    qr = (DOCS / "assets" / "qr-demo.svg").read_text(encoding="utf-8")
    qr = qr.replace('aria-label="QR code: https://hchagroune.github.io/diwan-htr/demo/"',
                    'aria-label="QR code to the demo: hchagroune.github.io/diwan-htr/demo"')

    def slide(n, cls, body, notes_ar, notes_en):
        return (f'<section class="slide {cls}" id="s{n}" aria-roledescription="slide" aria-label="{n} / 9" data-n="{n}">'
                f'<div class="slide-in">{body}</div>'
                f'<aside class="notes" hidden>{t(notes_ar, notes_en, tag="p")}</aside></section>')

    def h(ar, en):
        return f'<h2 class="s-ar" lang="ar" dir="rtl">{ar}</h2><p class="s-en" lang="en" dir="ltr">{en}</p>'

    def stat(numtxt, label, src, est=False):
        e = '<span class="est">Estimate · </span>' if est else ""
        return (f'<div class="s-stat"><div class="s-num" lang="en" dir="ltr">{numtxt}</div>'
                f'<p lang="en" dir="ltr">{label}</p><p class="s-src" lang="en" dir="ltr">{e}{src}</p></div>')

    # estimated learning curve: verified lines (x) vs character error rate (y), Lucas, Salah & Vidal-Gorène 2022
    pts = [(0, 21.24), (80, 9.99), (160, 7.7)]
    X = lambda x: 50 + x * 2.2
    Y = lambda y: 20 + (25 - y) * 7.2
    path = " ".join(("M" if i == 0 else "L") + f"{X(x):.0f} {Y(y):.0f}" for i, (x, y) in enumerate(pts))
    dots = "".join(f'<circle cx="{X(x):.0f}" cy="{Y(y):.0f}" r="6" fill="#e2bd55"/>'
                   f'<text x="{X(x):.0f}" y="{Y(y) - 16:.0f}" fill="#f3ede1" font-size="17" text-anchor="middle">{y:g}%</text>' for x, y in pts)
    chart = f"""<svg class="s-chart" viewBox="0 0 440 220" role="img" aria-label="Estimated character error: 21% at 0 verified lines, 10% at 80, 7.7% at 160">
  <line x1="50" y1="200" x2="420" y2="200" stroke="#2a3651"/><line x1="50" y1="20" x2="50" y2="200" stroke="#2a3651"/>
  <path d="{path}" fill="none" stroke="#e2bd55" stroke-width="3" stroke-dasharray="8 6"/>{dots}
  <text x="{X(0):.0f}" y="216" fill="#9aa1b2" font-size="14" text-anchor="middle">0</text>
  <text x="{X(80):.0f}" y="216" fill="#9aa1b2" font-size="14" text-anchor="middle">80</text>
  <text x="{X(160):.0f}" y="216" fill="#9aa1b2" font-size="14" text-anchor="middle">160 lines</text>
</svg>"""

    s = []
    s.append(slide(1, "s-hook", f"""
      <div class="crop s-crop"><img src="../assets/img/motto-line9.jpg" alt="" onload="this.parentNode.classList.add('has-img')"><span class="ph">[ line 9 · deed 0188 ]</span></div>
      <p class="s-deed" lang="ar" dir="rtl">وبالمحكمة الحنفية من بلد الجزائر المحمية بالله تعالى</p>
      <p class="s-q" lang="ar" dir="rtl">من يستطيع قراءتها اليوم؟</p>
      <p class="s-en" lang="en" dir="ltr">Line 9 of a deed, Hanafi court of Algiers, 1841. Who can still read it?</p>""",
        "ابدأ بالسكوت. اقرأ السطر بصوت عالٍ. هذا السطر من الوثيقة ٠١٨٨، كتبه كاتب المحكمة الحنفية في ٣ رجب ١٢٥٧ هـ. الكاتب كتب «تعلى»، ونعرضها هنا «تعالى».",
        "Open in silence, then read the line aloud. It is line 9 of deed 0188, written by the Hanafi court scribe on 3 Rajab 1257 AH. The scribe wrote تعلى; the slide shows تعالى."))
    s.append(slide(2, "", h("العربية شبه غائبة عن الشبكة، وخطّها اليدوي أغيب", "Arabic is barely online; its handwriting even less.") +
        f'<div class="s-stats">{stat("0.6%", "of websites use Arabic", "W3Techs, Nov 2026")}'
        f'{stat("≈0.004%", "of OpenITI’s Arabic text is handwriting", "our estimate", True)}</div>',
        "OpenITI فيه ٢٫٣١ مليار كلمة عربية، منها ١٠١٬٣٣٦ فقط من خط يد منسوخ. النسبة ≈٠٫٠٠٤٪ حسابنا نحن.",
        "OpenITI holds 2.31 billion Arabic tokens; only 101,336 come from transcribed handwriting. The ≈0.004% is our own arithmetic."))
    s.append(slide(3, "", h("تراث مصوَّر… لم يُقرأ بعد", "Filmed, catalogued, and still unread.") +
        f'<div class="s-stats">{stat("≈30,000", "Ottoman court registers survive", "ISAM", True)}'
        f'{stat("125", "microfilm reels of Algiers deeds, filmed by operators who knew no Arabic", "Grangaud 2026")}</div>',
        "الرقم ٣٠ ألف تقدير من مركز ISAM، وهو يحتفظ بنسخ رقمية لـ ٢٣٬٧٥٦ سجلًا. البكرات الـ١٢٥ في الأرشيف الوطني لما وراء البحار، بحسب Grangaud في مجلة إنسانيات ١١١. لا تقل «٥ ملايين مخطوط».",
        "30,000 is ISAM’s estimate; ISAM holds 23,756 in digital copies. The 125 reels are at ANOM, per Grangaud, Insaniyat 111. Do not say “5 million manuscripts”."))
    flow = "".join(f'<li lang="ar">{x}</li>' for x in ["الصفحة", "القارئ الآلي", "المدقق الآلي", "الخبير", "الأرشيف"])
    s.append(slide(4, "", h("قارئ آلي، مدقق آلي، وخبير يقرّر", "Every approved line becomes training data.") + f"""
      <ol class="s-flow" dir="rtl">{flow}</ol>
      <div class="s-try">
        <button class="btn btn-primary s-demo" type="button" data-open-demo><span lang="ar">جرّب الآن</span> · <span lang="en">Try it</span></button>
        <figure class="s-qr">{qr}<figcaption lang="en">Scan to try</figcaption></figure>
      </div>""",
        "اضغط «جرّب الآن» لتفتح العرض هنا، أو اطلب من الحضور مسح الرمز (يحتاج الهاتف إلى إنترنت). أغلق العرض بـ Esc.",
        "Press Try it to open the demo here, or invite the room to scan the code (phones need internet). Close the demo with Esc."))
    s.append(slide(5, "", h("كل سطر يعتمده الخبير يعلّم الآلة", "Each verified line teaches the machine to read Maghrebi script.") +
        f'<div class="s-stats one">{stat("21% → 10%", "character errors after about 80 verified lines", "Lucas, Salah &amp; Vidal-Gorène 2022")}</div>',
        "على الخط المغربي نزل الخطأ من ٢١٫٢٤٪ إلى ٩٫٩٩٪ بعد نحو ٨٠ سطرًا، وإلى ٧٫٧٪ بعد نحو ١٦٠. ونقص وقت المراجعة ٤٢٪.",
        "On Maghrebi script, character error fell from 21.24% to 9.99% after about 80 lines, and to 7.7% after about 160. Proofreading time fell 42%."))
    s.append(slide(6, "", h("التجربة الأولية: ثلاث صفحات حقيقية", "Real pilot, estimated curve.") + f"""
      <div class="s-split">
        <ul class="s-facts" lang="en" dir="ltr">
          <li><b>3 pages</b> · Algiers 2, Annaba 1</li>
          <li>Checker: <b>85–88% → 92%</b></li>
          <li><span class="est">Estimate ·</span> off the shelf 33–70% → 3–12% fine-tuned</li>
        </ul>
        <figure>{chart}<figcaption class="s-src" lang="en" dir="ltr"><span class="est">Estimate</span> · Lucas 2022; KITAB-Bench 2025</figcaption></figure>
      </div>""",
        "الحقيقي: ثلاث صفحات؛ ثقة المدقق ٨٥–٨٨٪، وارتفعت إلى ٩٢٪ في الصفحة ٠١٨٨ بعد ملاحظة الخبير. المنحنى والأرقام الأخرى تقديرات من دراسات منشورة، وليست نتائجنا.",
        "Real: three pages; checker confidence 85–88%, rising to 92% on page 0188 after the expert’s note. The curve and the other figures are estimates from published studies, not our results."))
    vision = "".join(f'<li lang="ar">{x}</li>' for x in ["وثائق الجزائر", "نموذج مفتوح لقراءة الخط المغربي", "أرشيفات العربية في العالم"])
    s.append(slide(7, "", h("من سجلات الجزائر إلى أرشيفات العربية في العالم", "From Algiers’ deeds to the world’s Arabic archives.") +
        f'<ol class="s-flow s-vision" dir="rtl">{vision}</ol>',
        "الخطوة الأولى صغيرة وحقيقية: صفحات الجزائر. كل سطر معتمد يقرّبنا من نموذج مفتوح.",
        "The first step is small and real: the Algiers pages. Every approved line brings an open model closer."))
    why = "".join(f'<li lang="ar">{x}</li>' for x in ["وكيلان آليان وخبير بشري", "منسَّق في n8n", "أرشيف حقيقي، لا بيانات تجريبية"])
    s.append(slide(8, "", h("لماذا يعنيكم، د. مراد بوعاش وطلبة الذكاء الاصطناعي الوكيلي؟", "Agentic AI in practice.") +
        f'<ul class="s-why" dir="rtl">{why}</ul>',
        "اربط بالدورة: وكيل يكتب، ووكيل يشكّ ويطلب إعادة، وإنسان في الحلقة يقرر. كل ذلك في n8n.",
        "Tie it to the course: one agent writes, one doubts and asks for a re-read, and a human in the loop decides. All of it in n8n."))
    sigs = "".join(f'<div class="s-sig">{seal(96, c["ar"].split()[0], color="#e2bd55", label=c["en"])}'
                   f'<span lang="ar">{c["ar"]}</span></div>' for c in CREATORS)
    s.append(slide(9, "s-close", f"""
      <h2 class="s-ar" lang="ar" dir="rtl">طلبنا: [ يُكتب لاحقًا ]</h2>
      <p class="s-en" lang="en" dir="ltr">Our ask: [ to be written ]</p>
      <p class="s-motto" lang="ar" dir="rtl">الجزائر المحمية بالله</p>
      <div class="s-sigs">{sigs}</div>""",
        "اكتبوا الطلب قبل يوم العرض: ما الذي تريدونه من الحضور تحديدًا؟ ثم اختم بالعبارة، واترك الصمت.",
        "Write the ask before the day: what exactly do you want from the room? Then close on the motto and let it rest."))

    body = f"""
<link rel="stylesheet" href="../assets/pitch.css">
<div class="deck" id="deck" tabindex="-1">
  <div class="band" aria-hidden="true"></div>
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
