"""Build the static site in docs/ from one template (Direction B, "Kasbah zellige").

Run from the repository root:  python tools/build_site.py
Every page carries Arabic and English; assets/diwan.js shows one of them.
Rule for all copy: never name an AI model or vendor. Say "AI reader / القارئ الآلي"
and "AI checker / المدقق الآلي".
"""
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs"
# Public address of the static site (Render static site "diwan-alwathaiq"). The pitch QR code points here.
SITE_URL = "https://diwan-alwathaiq.onrender.com/"

# Names as they appear on the seals and signatures. Arabic spelling to be confirmed by the creators.
CREATORS = [
    {"id": "seal-1", "ar": "حسام الدين شقرون", "en": "Houssam Eddine Chagroune",
     "role_ar": "المؤسس، ليمتلس إيماجينيشن", "role_en": "Founder, Limitless imagination"},
    {"id": "seal-2", "ar": "ياسين دادي عدون", "en": "Yacine Daddi Addoun",
     "role_ar": "الشريك المؤسس، ليمتلس إيماجينيشن", "role_en": "Co-founder, Limitless imagination"},
]


def t(ar, en, tag="span", cls="", attrs=""):
    c = f' class="{cls}"' if cls else ""
    a = f" {attrs}" if attrs else ""
    return (f'<{tag} data-l="ar" lang="ar" dir="rtl"{c}{a}>{ar}</{tag}>'
            f'<{tag} data-l="en" lang="en" dir="ltr"{c}{a}>{en}</{tag}>')


def seal(size, line1, line2="", color="#b4532a", label=""):
    aria = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true"'
    l2 = (f'<text x="0" y="22" text-anchor="middle" font-family="Amiri, serif" font-size="13" '
          f'fill="{color}">{line2}</text>') if line2 else ""
    return (f'<svg width="{size}" height="{size}" viewBox="-66 -66 132 132" {aria}>'
            f'<circle r="62" fill="none" stroke="{color}" stroke-width="2.6"/>'
            f'<circle r="54" fill="{color}" fill-opacity="0.07" stroke="{color}" stroke-width="1"/>'
            f'<text x="0" y="{-2 if line2 else 6}" text-anchor="middle" font-family="Amiri, serif" '
            f'font-size="{17 if len(line1) > 10 else 21}" font-weight="700" fill="{color}">{line1}</text>{l2}</svg>')


STAR = ('<svg width="30" height="30" viewBox="-15 -15 30 30" aria-hidden="true">'
        '<rect x="-9" y="-9" width="18" height="18" fill="#16684e"/>'
        '<rect x="-9" y="-9" width="18" height="18" fill="#16684e" transform="rotate(45)"/>'
        '<circle r="4" fill="#e2bd55"/></svg>')

NAV = [
    ("", "الرئيسية", "Welcome"),
    ("how/", "كيف يعمل", "How it works"),
    ("demo/", "جرّب", "Try it"),
    ("pitch/", "العرض", "Pitch"),
    ("archive/", "الأرشيف", "The archive"),
    ("creators/", "من نحن", "The creators"),
]

HEAD_SCRIPT = ("<script>(function(){try{var m=/[?&]lang=(ar|en)\\b/.exec(location.search);"
               "var l=m?m[1]:(localStorage.getItem('diwan-lang')||'ar');var h=document.documentElement;"
               "h.lang=l;h.dir=l==='ar'?'rtl':'ltr';h.setAttribute('data-ui',l);}catch(e){}})();</script>")


def page(path, title_ar, title_en, desc, body, scripts=(), current=None, bare=False):
    depth = path.count("/")
    root = "../" * depth
    nav = "".join(
        f'<a href="{root}{href}"{" aria-current=\"page\"" if href == current else ""}>{t(ar, en)}</a>'
        for href, ar, en in NAV)
    sigs = "".join(
        f'<a class="sig" href="{root}creators/#{c["id"]}">{seal(40, c["ar"].split()[0], color="#e2bd55")}'
        f'<span class="name">{t(c["ar"], c["en"])}</span></a>' for c in CREATORS)
    header = f"""<a class="skip" href="#main">{t("تخطَّ إلى المحتوى", "Skip to the content")}</a>
<div class="band" aria-hidden="true"></div>
<header class="site-head">
  <div class="wrap head-row">
    <a class="brand" href="{root}">{STAR}{t("ديوان الوثائق", "Dīwān al-Wathāʾiq")}</a>
    <nav class="nav" aria-label="Sections">{nav}</nav>
    <button class="lang-btn" type="button" data-lang-switch lang="en">English</button>
  </div>
</header>"""
    footer = f"""<footer class="site-foot">
  <div class="dado" aria-hidden="true"></div>
  <div class="wrap foot-sign">
    <p style="margin:0">{t("شهد على هذا الديوان شاهداه", "Witnessed by its two creators")}</p>
    <div class="signatures">{sigs}</div>
  </div>
  <div class="wrap foot-meta">
    <div>
      <p style="margin:0 0 4px">{t("الصور: الأرشيف الوطني لما وراء البحار (ANOM)، إكس أون بروفانس. النصوص المعتمدة نسخ حرفي راجعه خبير.",
                                    "Scans: Archives nationales d’outre-mer (ANOM), Aix-en-Provence. Approved texts are diplomatic transcriptions checked by an expert.")}</p>
      <p style="margin:0">{t("مشروع التخرج لدورة Limitless Learning في الذكاء الاصطناعي الوكيلي.",
                              "Final project for the Limitless Learning Agentic AI course.")}</p>
    </div>
    <div class="row" style="gap:16px">
      <a href="https://github.com/hchagroune/diwan-htr">GitHub</a>
      <a href="mailto:chagroune.amc@gmail.com">chagroune.amc@gmail.com</a>
      <a class="board" href="{root}board.html">{t("لوحة الفريق", "Team board")}</a>
    </div>
  </div>
</footer>"""
    scr = "".join(f'<script src="{root}assets/{s}" defer></script>' for s in scripts)
    html = f"""<!doctype html>
<html lang="ar" dir="rtl" data-ui="ar" data-root="{root}" data-title-ar="{title_ar}" data-title-en="{title_en}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title_ar}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#111a2d">
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{root}assets/diwan.css">
{HEAD_SCRIPT}
<script src="{root}assets/diwan.js" defer></script>{scr}
</head>
<body>
{"" if bare else header}
<main id="main">
{body}
</main>
{"" if bare else footer}
</body>
</html>
"""
    out = DOCS / path / "index.html" if path else DOCS / "index.html"
    if path.endswith(".html"):
        out = DOCS / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out


ARCH_SVG = """<svg viewBox="-380 -570 760 690" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <path d="M -360 120 L -360 0 A 395 395 0 1 1 360 0 L 360 120" fill="none" stroke="#e2bd55" stroke-width="2.5"/>
  <path d="M -344 120 L -344 0 A 379 379 0 1 1 344 0 L 344 120 Z" fill="#18233a" stroke="#e2bd55" stroke-width="1"/>
  <path d="M -326 120 L -326 0 A 361 361 0 1 1 326 0 L 326 120" fill="none" stroke="#2a3651" stroke-width="1" stroke-dasharray="3 6"/>
</svg>"""


def welcome():
    body = f"""
<section class="hero on-night" aria-labelledby="motto">
  <div class="wrap hero-grid">
    <div class="side">
      {t("المشكلة", "The problem", cls="label")}
      {t("صُوِّرت ملايين الصفحات من المخطوطات، لكن خطّها لم يصر بعد نصًا يُقرأ ويُبحث فيه.",
         "Millions of manuscript pages have been photographed. Almost none of their handwriting can yet be read or searched as text.", tag="p")}
    </div>
    <div class="arch">
      {ARCH_SVG}
      <div class="arch-inner">
        <div class="crop">
          <img src="assets/img/motto-line9.jpg" alt="" onload="this.parentNode.classList.add('has-img')">
          {t("[ مقتطع السطر ٩ من الوثيقة ٠١٨٨ بخط الكاتب ]", "[ Line 9 of deed 0188 in the scribe’s hand ]", cls="ph")}
        </div>
        <h1 id="motto" class="motto" lang="ar" dir="rtl"><span class="motto-ink">الجزائر المحمية بالله</span></h1>
        <p class="motto-en" lang="en" dir="ltr">Algiers, protected by God</p>
        {t("السطر ٩ من وثيقة للمحكمة الحنفية بالجزائر، ٣ رجب ١٢٥٧ هـ (١٨٤١ م)",
           "Line 9 of a deed of the Hanafi court of Algiers, 3 Rajab 1257 AH (1841)", tag="p", cls="motto-src")}
        <div class="row" style="justify-content:center;margin-top:6px">
          <a class="btn btn-primary" href="demo/">{t("جرّب بنفسك", "Try it yourself")}</a>
          <a class="btn btn-line" href="pitch/">{t("شاهد العرض", "Watch the pitch")}</a>
        </div>
      </div>
    </div>
    <div class="side">
      {t("الفكرة", "The idea", cls="label")}
      {t("قارئ آلي يكتب المسودة، ومدقق آلي يعلّم الأسطر المشكوك فيها، وخبير يعتمد كل صفحة؛ وكل سطر يعتمده يصير بيانات تدريب.",
         "An AI reader drafts, an AI checker flags doubtful lines, and an expert approves every page. Each approved line becomes training data.", tag="p")}
    </div>
  </div>
  <div class="dado" aria-hidden="true" style="margin-top:28px"></div>
</section>

<section class="section" aria-labelledby="about-motto">
  <div class="wrap">
    <h2 id="about-motto">{t("عن العبارة", "About the motto")}</h2>
    <div class="caption-box" style="color:var(--ink-2);border-color:var(--terra)">
      {t("«الجزائر المحمية بالله» كما كتبها كاتب المحكمة الحنفية في السطر التاسع من وثيقة مؤرخة في ٣ رجب ١٢٥٧ هـ (١٨٤١ م): «وبالمحكمة الحنفية من بلد الجزائر المحمية بالله تعالى». وهي من ألقاب مدينة الجزائر في العهد العثماني، ومنها أيضًا «المحروسة»، وهو لقب يشير إلى حماية إلهية وبشرية معًا.",
         "“Algiers, protected by God”, as the Hanafi court scribe wrote it on line 9 of a deed dated 3 Rajab 1257 AH (1841): “…and at the Hanafi court of the city of Algiers, protected by God Most High…”. It is one of the city’s Ottoman-era epithets, alongside al-Maḥrūsa, “the well-guarded”, a name that alludes to both divine and human protection.", tag="p")}
      <p class="small" style="margin:0">{t("المصادر:", "Sources:")}
        <a href="https://cguaa.journals.ekb.eg/article_31924.html">{t("زكية راجعي، مجلة الاتحاد العام للآثاريين العرب", "Zakia Rajai, Journal of the General Union of Arab Archaeologists (in Arabic)")}</a> ·
        <a href="https://shs.hal.science/halshs-01309755">{t("التحصينات العثمانية لمدينة الجزائر (١٥١٦–١٨٣٠)", "Les fortifications ottomanes d’Alger (1516–1830)")}</a>
      </p>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="explore">
  <div class="wrap">
    <h2 id="explore" class="visually-hidden">{t("اكتشف", "Explore")}</h2>
    <div class="grid-3">
      <a class="card" href="how/" style="text-decoration:none;color:inherit">
        {t("كيف يعمل", "How it works", tag="h3")}
        {t("خمس مراحل من الصورة إلى النص المعتمد، وطريق لإعادة الصفحة مع ملاحظة.", "Five steps from scan to approved text, and a way to send a page back with a note.", tag="p", cls="muted")}
      </a>
      <a class="card" href="archive/" style="text-decoration:none;color:inherit">
        {t("الأرشيف", "The archive", tag="h3")}
        {t("سجلات محاكم الجزائر الشرعية، ولماذا يصعب على الآلة قراءتها.", "The sharia-court registers of Algiers, and why machines struggle to read them.", tag="p", cls="muted")}
      </a>
      <a class="card" href="creators/" style="text-decoration:none;color:inherit">
        {t("من نحن", "The creators", tag="h3")}
        {t("شاهدا هذا الديوان، كما يشهد العدلان على كل وثيقة.", "The project’s two witnesses, as two notaries witness every deed.", tag="p", cls="muted")}
      </a>
    </div>
  </div>
</section>"""
    page("", "ديوان الوثائق · الجزائر المحمية بالله", "Dīwān al-Wathāʾiq · Algiers, protected by God",
         "Sharia-court deeds of Algiers in Maghrebi script, read by an AI reader, checked by an AI checker and approved by an expert.",
         body, current="")


def how():
    steps = [
        ("الصفحة", "The scan", "تُؤخذ صورة واحدة من مجلد الوارد، فلا تُقرأ مرتين.", "One image is taken from the inbox folder, so it is never read twice.", ""),
        ("القارئ الآلي", "AI reader", "يقرأ الصفحة سطرًا بسطر، مستعينًا بأشبه الصفحات التي اعتمدها الخبير أمثلةً.", "Reads the page line by line, shown the most similar expert-approved pages as worked examples.", ""),
        ("المدقق الآلي", "AI checker", "يقارن النص بالصورة سطرًا بسطر، فيعلّم الأسطر المشكوك فيها ويعطي درجة ثقة، وقد يطلب قراءة ثانية.", "Compares the text with the image line by line, flags doubtful lines, gives a confidence score, and can ask for one more reading.", ""),
        ("الخبير", "The expert", "يرى الصورة بجانب النص، فيصحح ويقرر: اعتماد، أو إعادة مع ملاحظة، أو رفض.", "Sees the scan beside the text, corrects it and decides: approve, send back with a note, or reject.", "expert"),
        ("الأرشيف", "The archive", "يُحفظ النص المعتمد بجانب صورته، ويصير مثالًا تتعلم منه الصفحات التالية.", "The approved text is saved beside its scan and becomes an example for the next pages.", ""),
    ]
    lis = "".join(
        f'<li class="{c}">{t(a, b, tag="h3")}{t(c_ar, c_en, tag="p", cls="muted small")}</li>'
        for a, b, c_ar, c_en, c in steps)
    rules = [
        ("لا يُحفظ شيء دون خبير", "Nothing is saved without an expert", "الآلة تقترح، والمدقق يسأل، والإنسان يقرر.", "The machines propose and question; a person decides."),
        ("تبقى كتابة الوثيقة كما هي", "The deed’s own spelling stays", "سطر لكل سطر من المخطوط، دون تصحيح للنحو ولا إضافة للحركات.", "One line for each manuscript line, no corrected grammar, no added vowels."),
        ("كل صفحة معتمدة تعلّم التالية", "Every approved page teaches the next", "الصورة ونصها المعتمد يصيران زوجًا موثقًا للتدريب.", "The scan and its approved text become a verified training pair."),
    ]
    rl = "".join(f'<div class="card">{t(a, b, tag="h3")}{t(c, d, tag="p", cls="muted")}</div>' for a, b, c, d in rules)
    body = f"""
<section class="section">
  <div class="wrap">
    {t("كيف يعمل الديوان", "How the Dīwān works", tag="h1")}
    {t("صفحة واحدة في كل دورة. آلتان تقرآن وتسألان، وخبير يقرر قبل أن يُحفظ أي سطر.", "One page per run. Two AI agents read and question; an expert decides before any line is saved.", tag="p", cls="lead")}
    <ol class="steps" style="margin-top:22px">{lis}</ol>
    <div class="loop">
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true" style="flex:none"><path d="M4 12a8 8 0 0 1 14-5.3L20 9"/><path d="M20 4v5h-5"/><path d="M20 12a8 8 0 0 1-14 5.3L4 15"/><path d="M4 20v-5h5"/></svg>
      <div>{t("<b>الإعادة مع ملاحظة.</b> إذا رأى الخبير خطأ، كتب ملاحظة فيقرأ القارئ الآلي الصفحة من جديد مسترشدًا بها، ثم تعود إليه. في التجربة الأولية أُعيدت الصفحة ٠١٨٨ مرتين قبل اعتمادها.",
              "<b>Send back with a note.</b> When the expert sees a mistake, they write a note; the AI reader reads the page again, guided by it, and the page returns for review. In the pilot, page 0188 went back twice before it was approved.", tag="p")}</div>
    </div>
  </div>
</section>
<div class="dado" aria-hidden="true"></div>
<section class="section" style="padding-top:56px">
  <div class="wrap">
    {t("ثلاث قواعد", "Three rules", tag="h2")}
    <div class="grid-3">{rl}</div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    {t("لماذا هو نظام وكيلي", "Why it is an agentic system", tag="h2")}
    <div class="grid-3">
      <div class="card">{t("وكيلان بدورين مختلفين", "Two agents, two roles", tag="h3")}{t("القارئ يكتب، والمدقق يشكّ. وحين يجد المدقق مشكلة يطلب قراءة ثانية بملاحظاته.", "The reader writes; the checker doubts. When the checker finds a problem, it asks for a second reading with its notes.", tag="p", cls="muted")}</div>
      <div class="card">{t("إنسان في الحلقة", "A human in the loop", tag="h3")}{t("لا يقرر الوكيلان وحدهما. الخبير يعتمد أو يعيد أو يرفض، وقراره هو الحكم.", "The agents never decide alone. The expert approves, sends back or rejects, and that decision is final.", tag="p", cls="muted")}</div>
      <div class="card">{t("منسَّق في n8n", "Orchestrated in n8n", tag="h3")}{t("سير العمل كله في n8n: أخذ الصفحة، القراءة، التدقيق، بريد الخبير، الحفظ، ولوحة الفريق.", "The whole workflow runs in n8n: picking up the page, reading, checking, the expert’s email, saving, and the team board.", tag="p", cls="muted")}</div>
    </div>
  </div>
</section>"""
    page("how/", "كيف يعمل · ديوان الوثائق", "How it works · Dīwān al-Wathāʾiq",
         "From scan to approved text: AI reader, AI checker, expert, archive.", body, current="how/")


def demo():
    body = f"""
<section class="section">
  <div class="wrap">
    {t("جرّب: كن أنت الخبير", "Try it: be the expert", tag="h1")}
    {t("هذه بيانات حقيقية مسجّلة من التجربة الأولية، تعمل في المتصفح دون اتصال. اختر صفحة، وشاهد القارئ الآلي يكتب، والمدقق يعلّم الأسطر المشكوك فيها، ثم قرّر أنت.",
       "These are real recordings from the pilot, running in your browser with no connection. Pick a page, watch the AI reader write and the AI checker flag doubtful lines, then decide.", tag="p", cls="lead")}
    <div class="demo-pick" id="pick" role="group" aria-label="Pages"></div>

    <div class="workbench" id="bench" hidden>
      <div class="scan-frame">
        <div class="scan" id="scan">
          <img id="scanImg" alt="" onload="this.parentNode.classList.add('has-img')">
          <div class="scan-hl" id="hl" style="top:8%"></div>
          {t("[ صورة الصفحة: تُضاف لاحقًا ]", "[ Page scan: to be added ]", cls="ph")}
        </div>
        <p class="scan-cap" id="scanCap"></p>
      </div>
      <div>
        <div class="bench-top">
          <div id="pageTitle" style="font-weight:600"></div>
          <div class="meter" id="meter" hidden>
            {t("ثقة المدقق", "Checker confidence", cls="small muted")}
            <div class="meter-bar"><span id="meterBar"></span></div>
            <b id="meterVal"></b>
          </div>
        </div>
        <div class="row" style="margin-bottom:10px">
          <button class="btn btn-quiet" type="button" id="skip">{t("أظهر النص كاملًا", "Show the whole text")}</button>
          <span class="status" id="status" aria-live="polite"></span>
        </div>
        <ol class="lines" id="lines"></ol>
        <div class="decide" id="decide" hidden>
          {t("قرارك", "Your decision", tag="h2")}
          {t("صحّح أي سطر بالنقر على «صحّح»، أو اقبل اقتراح المدقق، ثم اعتمد الصفحة أو أعدها مع ملاحظة.",
             "Correct any line with “Edit”, or accept the checker’s suggestion, then approve the page or send it back with a note.", tag="p", cls="muted small")}
          <div class="row">
            <button class="btn btn-primary" type="button" id="approve">{t("اعتمد الصفحة", "Approve the page")}</button>
            <button class="btn btn-terra" type="button" id="sendback">{t("أعدها مع ملاحظة", "Send back with a note")}</button>
          </div>
          <div id="noteBox" hidden>
            <label for="note" class="small">{t("ملاحظتك للقارئ الآلي", "Your note for the AI reader")}</label>
            <textarea id="note" dir="auto"></textarea>
            <div class="row" style="margin-top:8px"><button class="btn btn-terra" type="button" id="sendNote">{t("أرسل الملاحظة", "Send the note")}</button></div>
          </div>
        </div>
        <div class="final" id="final" hidden tabindex="-1">
          <div class="counter" id="counter"></div>
          <p id="finalMsg" style="margin:6px 0 0;color:var(--on-night-2)"></p>
          <ol id="finalLines"></ol>
          <details class="compare" id="compare" hidden>
            <summary>{t("قارن بما اعتمده خبيرنا في التجربة", "Compare with what our expert approved in the pilot")}</summary>
            <ol id="expertLines"></ol>
          </details>
          <div class="row" style="margin-top:14px"><button class="btn btn-line" type="button" id="again">{t("جرّب صفحة أخرى", "Try another page")}</button></div>
        </div>
      </div>
    </div>

    <section class="live card" aria-labelledby="liveTitle">
      <h2 id="liveTitle" style="font-size:22px">{t("الوضع المباشر (اختياري)", "Live mode (optional)")}</h2>
      {t("يعرض حالة الصفحات الآن في سير العمل على n8n. يحتاج إلى رمز الدخول وإلى اتصال، ولذلك هو مطفأ افتراضيًا.",
         "Shows where pages stand right now in the n8n workflow. It needs the access code and a connection, so it is off by default.", tag="p", cls="muted small")}
      <label class="switch"><input type="checkbox" id="liveOn"> {t("شغّل الوضع المباشر", "Turn on live mode")}</label>
      <div id="liveBox" hidden style="margin-top:12px">
        <label for="liveCode">{t("رمز الدخول", "Access code")}</label>
        <div class="row"><input type="password" id="liveCode" autocomplete="off"><button class="btn btn-quiet" type="button" id="liveGo">{t("اعرض", "Show")}</button></div>
        <div class="live-out" id="liveOut" aria-live="polite"></div>
      </div>
    </section>
  </div>
</section>"""
    page("demo/", "جرّب · ديوان الوثائق", "Try it · Dīwān al-Wathāʾiq",
         "Play the expert on real pilot pages: approve, correct or send back with a note.", body,
         scripts=("demo-data.js", "demo.js"), current="demo/")


def archive():
    facts = [
        ("١٢٥", "125", "بكرة ميكروفيلم لأرشيف الجزائر العربي والتركي في ANOM", "microfilm reels of the Arabic and Turkish archives of Algiers at ANOM", "Grangaud, Insaniyat 111 (2026)", False),
        ("≈ ٧٥٬٠٠٠", "≈ 75,000", "ورقة في المجموع (تقديرنا: ١٢٥ × نحو ٦٠٠)", "folios in all (our estimate: 125 × about 600)", "Grangaud (2026), our arithmetic", True),
        ("≈ ٣٠٬٠٠٠", "≈ 30,000", "سجل محكمة عثماني باقٍ (تقدير مؤسسي)", "Ottoman court registers survive (institutional estimate)", "ISAM, Istanbul", True),
        ("٢٣٬٧٥٦", "23,756", "سجلًا منها مصوّرة رقميًا لدى ISAM", "of them held in digital copies by ISAM", "ISAM", False),
    ]
    fc = "".join(
        f'<div class="fact"><div class="num">{t(a, b)}</div>{t(c, d, tag="p", cls="small")}'
        f'<div class="src">{t("تقدير · ", "Estimate · ") if est else ""}{s}</div></div>'
        for a, b, c, d, s, est in facts)
    body = f"""
<section class="section">
  <div class="wrap">
    {t("الأرشيف", "The archive", tag="h1")}
    {t("سجلات المحاكم الشرعية الحنفية والمالكية في الجزائر: بيوع وأوقاف وتركات وإبراءات، كتبها كتّاب المحاكم بالخط المغربي في القرنين الثامن عشر والتاسع عشر.",
       "The registers of the Hanafi and Maliki sharia courts of Algiers: sales, endowments, inheritances and releases, written by court scribes in Maghrebi script in the 18th and 19th centuries.", tag="p", cls="lead")}
    <div class="facts" style="margin-top:20px">{fc}</div>
  </div>
</section>
<div class="dado" aria-hidden="true"></div>
<section class="section" style="padding-top:56px">
  <div class="wrap grid-3" style="align-items:start">
    <div>
      {t("أرشيف صُوِّر ولم يُقرأ", "Filmed, not read", tag="h2")}
      {t("صُوِّر الميكروفيلم المحفوظ في إكس أون بروفانس على يد مشغّلين لا يعرفون العربية: بكرات مركّبة بالمقلوب، وصور سالبة، وترقيم بالكاد يُرى. وجزء كبير من الرصيد تجميع استعماري لسجلات الملكية بين ١٨٣٠ و١٨٧٠، وهذا يزيد قيمته للمؤرخين.",
         "The microfilm kept in Aix-en-Provence was made by operators who knew no Arabic: reels mounted backwards, frames in negative, foliation barely visible. Much of the fonds is a colonial compilation of property records from 1830–1870, which makes it more valuable to historians, not less.", tag="p")}
    </div>
    <div>
      {t("لماذا تتعثر الآلة", "Why machines stumble", tag="h2")}
      {t("في الخط المغربي تقع نقطة الفاء تحتها ونقطة القاف فوقها واحدة، والأختام والحواشي تقطع الأسطر.",
         "In Maghrebi script fa carries its dot below and qaf a single dot above, and seals and marginal notes break the lines.", tag="p")}
      <div class="letters">
        <div class="letter"><span class="g" lang="ar">ڢ</span><span>→ ف · fa</span></div>
        <div class="letter"><span class="g" lang="ar">ڧ</span><span>→ ق · qaf</span></div>
      </div>
    </div>
    <div>
      {t("صفحات التجربة الأولية", "The pilot pages", tag="h2")}
      <ul class="small" style="padding-inline-start:1.2em">
        <li>{t("٠١٨٨ · المحكمة الحنفية بالجزائر، ٣ رجب ١٢٥٧ هـ (١٨٤١). اعتُمدت بعد إعادتين.", "0188 · Hanafi court of Algiers, 3 Rajab 1257 AH (1841). Approved after two rounds.")}</li>
        <li>{t("٠٠٣٨ · أوائل رمضان ١٢٣١ هـ (١٨١٦). اعتمدها الخبير.", "0038 · Early Ramadan 1231 AH (1816). Approved by the expert.")}</li>
        <li>{t("٠١٠٠ · المحكمة المالكية بعنابة. بانتظار الخبير.", "0100 · Maliki court of Annaba. Waiting for the expert.")}</li>
      </ul>
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    {t("المصادر", "Sources", tag="h2")}
    <ul class="sources">
      <li>Isabelle Grangaud, <i>Insaniyat</i> 111 (2026): {t("الميكروفيلم وطريقة تصويره ومحتواه.", "the microfilm, how it was filmed and what it holds.")}</li>
      <li>{t("مركز البحوث الإسلامية (ISAM)، إسطنبول: عدد سجلات المحاكم العثمانية الباقية ونسخها الرقمية.", "Centre for Islamic Studies (ISAM), Istanbul: surviving Ottoman court registers and their digital copies.")}</li>
      <li>{t("الأرشيف الوطني لما وراء البحار (ANOM): «الأرشيف العربي والتركي لإيالة الجزائر القديمة».", "Archives nationales d’outre-mer (ANOM): “Archives arabes et turques de l’Ancienne Régence d’Alger”.")}</li>
    </ul>
  </div>
</section>"""
    page("archive/", "الأرشيف · ديوان الوثائق", "The archive · Dīwān al-Wathāʾiq",
         "The sharia-court registers of Algiers and the ANOM microfilm.", body, current="archive/")


def creators():
    c1, c2 = CREATORS
    seals = "".join(
        f'<button class="seal-btn" type="button" id="{c["id"]}" data-story="story-{c["id"]}" aria-haspopup="dialog">'
        f'{seal(150, c["ar"].split()[0] + " " + c["ar"].split()[1] if len(c["ar"].split()) > 2 else c["ar"], "١٤٤٨", label=c["en"])}'
        f'<span class="who">{t(c["ar"], c["en"])}</span><span class="role">{t(c["role_ar"], c["role_en"])}</span>'
        f'<span class="small" style="color:var(--cobalt)">{t("انقر لقراءة قصته", "Open the story")}</span></button>'
        for c in CREATORS)
    dialogs = ""
    for c in CREATORS:
        extra = ""
        if c["id"] == "seal-2":
            extra = t("في التجربة الأولية راجع الصفحتين ٠٠٣٨ و٠١٨٨ واعتمدهما.", "In the pilot he reviewed and approved pages 0038 and 0188.", tag="p")
        dialogs += f"""<dialog class="story" id="story-{c["id"]}" aria-labelledby="story-{c["id"]}-t">
  <div class="story-in">
    {seal(72, c["ar"].split()[0], label=c["en"])}
    <h2 id="story-{c["id"]}-t" style="margin:0">{t(c["ar"], c["en"])}</h2>
    {t(c["role_ar"], c["role_en"], tag="p", cls="muted")}
    {extra}
    {t("[ تُكتب القصة لاحقًا ]", "[ Story to be written ]", tag="p", cls="ph-text")}
    <div class="row"><button class="btn btn-quiet" type="button" data-close>{t("إغلاق", "Close")}</button></div>
  </div>
</dialog>"""
    body = f"""
<section class="section">
  <div class="wrap">
    {t("من نحن: شاهدا هذا الديوان", "The creators: this Dīwān’s two witnesses", tag="h1")}
    {t("في الوثيقة الشرعية يشهد عدلان على العقد ويوقّعان في آخره. هكذا نقدّم أنفسنا: شاهدين على هذا الديوان، وتوقيعانا يختمان كل صفحة منه.",
       "In a sharia-court deed, two notarial witnesses attest the act and sign at its foot. That is how we introduce ourselves: as the two witnesses of this Dīwān, whose signatures close every page.", tag="p", cls="lead")}
    <article class="deed-paper" style="margin-top:22px" aria-label="The deed of the two witnesses">
      <p class="deed-text" lang="ar"><span class="rubric">الحمد لله.</span> حضر ديوانُ الوثائق لدى شهيديه، المكرّمَين {c1["ar"]} و{c2["ar"]}، وأشهد على نفسه أنه أُنشئ ليُقرأ ما خطّه كتّاب محاكم الجزائر بالخط المغربي، وأنه لا يحفظ سطرًا إلا بعد أن يعتمده خبير، وأن كل سطر يُعتمد يصير درسًا يُنقل إلى الجيل القادم. شهد عليه بذلك شاهداه، وعرفاه، وكُتب في [التاريخ].</p>
      <p class="deed-gloss" lang="en" dir="ltr">Praise be to God. The Dīwān al-Wathāʾiq appeared before its two witnesses, {c1["en"]} and {c2["en"]}, and declared that it was made so that what the court scribes of Algiers wrote in Maghrebi script can be read; that it saves no line until an expert approves it; and that every approved line becomes a lesson passed on to the next generation. Its two witnesses attested it, knowing it well, and it was written on [date].</p>
      <div class="seals">{seals}</div>
    </article>
  </div>
</section>
<div class="dado" aria-hidden="true"></div>
<section class="section" style="padding-top:56px">
  <div class="wrap">
    {t("سلسلة النقل", "The chain of transmission", tag="h2")}
    {t("كما تُروى الإجازة من شيخ إلى تلميذ، تنتقل القراءة هنا من حلقة إلى حلقة.", "As an ijāza passes from teacher to student, the reading passes here from link to link.", tag="p", cls="muted")}
    <ol class="chain">
      <li>{t("<b>كتّاب المحكمة</b><br>الجزائر، ١٨٤١", "<b>The court scribes</b><br>Algiers, 1841")}</li>
      <li>{t("<b>الخبراء المراجعون</b><br>يقرؤون ويعتمدون", "<b>The expert reviewers</b><br>read and approve")}</li>
      <li>{t("<b>الشاهدان</b><br>بنيا الديوان", "<b>The two witnesses</b><br>built the Dīwān")}</li>
      <li class="you">{t("<b>أنت</b><br>الحلقة التالية", "<b>You</b><br>the next link")}</li>
    </ol>
  </div>
</section>
{dialogs}
<script>
document.addEventListener("click", function (e) {{
  var s = e.target.closest("[data-story]");
  if (s) {{ var d = document.getElementById(s.getAttribute("data-story")); if (d && d.showModal) d.showModal(); }}
  var c = e.target.closest("[data-close]");
  if (c) c.closest("dialog").close();
}});
if (location.hash) {{ var b = document.querySelector(location.hash + "[data-story]"); if (b) b.focus(); }}
</script>"""
    page("creators/", "من نحن · ديوان الوثائق", "The creators · Dīwān al-Wathāʾiq",
         "The two creators, presented as the two witnesses of a deed.", body, current="creators/")


def not_found():
    body = f"""
<section class="section">
  <div class="wrap">
    {t("هذه الصفحة غير موجودة", "This page does not exist", tag="h1")}
    {t("ربما تغيّر العنوان. عد إلى الصفحة الرئيسية أو جرّب العرض.", "The address may have changed. Go back to the welcome page or try the demo.", tag="p", cls="lead")}
    <div class="row"><a class="btn btn-primary" href="./">{t("الرئيسية", "Welcome")}</a><a class="btn btn-quiet" href="demo/">{t("جرّب", "Try it")}</a></div>
  </div>
</section>"""
    p = page("404.html", "غير موجودة · ديوان الوثائق", "Not found · Dīwān al-Wathāʾiq", "Page not found.", body)
    # 404 is served at any depth and under two bases (GitHub Pages /diwan-htr/, Render /):
    # a <base> chosen before anything loads makes every relative link resolve from the site root.
    base = ("<script>document.write('<base href=\"' + (location.pathname.indexOf('/diwan-htr/') === 0 ? '/diwan-htr/' : '/') + '\">');</script>")
    s = p.read_text(encoding="utf-8").replace('<meta charset="utf-8">', '<meta charset="utf-8">\n' + base, 1)
    s = s.replace('<a class="skip" href="#main">', '<a class="skip" href="#main" onclick="var m=document.getElementById(\'main\');m.tabIndex=-1;m.focus();return false">')
    s = s.replace('href="/diwan-htr/demo/"', 'href="demo/"').replace('href="/diwan-htr/"', 'href="./"').replace('href=""', 'href="./"')
    p.write_text(s, encoding="utf-8")


if __name__ == "__main__":
    welcome(); how(); demo(); archive(); creators(); not_found()
    import pitch_page
    import qr
    (DOCS / "assets" / "qr-demo.svg").write_text(qr.to_svg(qr.build(SITE_URL + "demo/"), SITE_URL + "demo/"), encoding="utf-8")
    pitch_page.build(DOCS, page, t, seal, CREATORS, SITE_URL)
    import service_worker
    service_worker.build(DOCS)
    print("site built in", DOCS)
