(() => {
"use strict";

/* ====================================================================== i18n */
const STR = {
  ar: {
    appName: "ديوان الوثائق",
    tagline: "نسخ عقود المحكمة المكتوبة بالخط المغربي — الجزائر، القرنان الثامن عشر والتاسع عشر",
    langBtn: "English",
    tabs: { pages: "الأوراق", review: "المراجعة", library: "الخزانة", register: "السجل" },
    hijri: "اليوم",
    stepsTitle: "كيف يعمل الديوان",
    steps: [["ارفع صور الأوراق", "صور ‎.jpg‎ أو ملف ‎.zip‎، أو ضعها في مجلد الوارد على Google Drive."],
            ["النسخ الآلي", "يقرأ Gemini الورقة مستعينا بأشبه الأوراق الموثقة في الخزانة، ثم يراجع مدقق ثان نسخته."],
            ["المراجعة والاعتماد", "يصحح الخبير النص سطرا بسطر ثم يعتمده؛ يحفظ ملف ‎.txt‎ في مجلد النتائج وتنضم الورقة إلى الخزانة."]],
    dropTitle: "اسحب صور الأوراق هنا",
    dropSub: "‎.jpg‎ أو ‎.png‎ أو ‎.zip‎ — أو انقر للاختيار",
    pagesTitle: "الأوراق الواردة",
    filterAll: "الكل",
    transcribeAll: n => `انسخ كل الجديد (${n})`,
    transcribe: "انسخ",
    open: "افتح",
    stop: "أوقف الطابور",
    fetchDrive: "اجلب الجديد من Drive",
    noPages: "لا توجد أوراق بعد. ارفع صور الأوراق في الخانة أعلاه، أو ضعها في مجلد الوارد على Drive.",
    lines: n => `${n} سطرا`,
    status: { new: "جديدة", queued: "في الطابور", transcribing: "قيد النسخ", review: "للمراجعة", approved: "معتمدة", rejected: "مرفوضة", error: "خطأ" },
    pair: { verified: "موثقة", conflict: "نسخ متعارضة", unverified: "غير موثقة" },
    working: (n) => `يعمل الخادم… ${n ? `${n} في الانتظار` : ""}`,
    task: { transcribe: "ينسخ ورقة", sync: "يزامن الخزانة من Drive", discover: "يبحث عن أوراق جديدة في Drive", eval: "يقيس الدقة" },
    uploading: p => `يرفع… ${p}`,
    uploaded: n => `أضيفت ${n} ورقة`,
    reviewEmpty: "اختر ورقة من «الأوراق» أو من «الخزانة» لمراجعتها هنا.",
    prev: "السابقة", next: "التالية",
    confidence: "ثقة المدقق",
    noConfidence: "لم تفحص بعد",
    editorLabel: "النص المعتمد",
    reviewer: "اسم المراجع",
    approve: "اعتمد",
    saveDraft: "احفظ المسودة",
    reject: "ارفض الورقة",
    del: "أزل من القائمة",
    delConfirm: "تأكيد الإزالة",
    download: "نزل ‎.txt‎",
    addLib: "أضف الورقة وتصحيحها إلى الخزانة",
    retrans: "أعد النسخ مع ملاحظة",
    notePh: "مثال: السطر ٤ حاشية في الهامش؛ لا تنسخ نص الختم",
    send: "أرسل إلى Gemini",
    saveVerified: "احفظ كنص موثق",
    gtNotice: "مراجعة نص من الخزانة: صحح النص ليطابق المخطوط حرفيا. الأوراق الموثقة وحدها تستعمل أمثلة للنسخ.",
    altTitle: n => `نسخة أخرى رقم ${n} بالاسم نفسه`,
    examplesUsed: "الأمثلة المستعملة:",
    inQueue: "الورقة في طابور النسخ…",
    libTitle: "الخزانة: أوراق ونصوص موثقة",
    libSub: "أزواج الصور والنصوص التي يتعلم منها الناسخ. تطابق الملفات بالاسم: FRANOM88_1MIOM31_0038.jpg مع FRANOM88_1MIOM31_0038.txt",
    libDrop: "اسحب الصور والنصوص معا، أو ملف ‎.zip‎",
    expert: "هذه النصوص راجعها خبير",
    syncDrive: "زامن الخزانة من Drive",
    libEmpty: "الخزانة فارغة. زامنها من Drive أو أضف أزواجا من الصور والنصوص.",
    colPage: "الورقة", colState: "الحالة", colFirst: "أول سطر", colLines: "أسطر", colSplit: "القسم", colAct: "",
    split: { train: "تعلم", val: "تحقق", test: "اختبار" },
    verify: "راجع",
    pairsAdded: (n, c) => `أضيف ${n} زوجا${c ? `، منها ${c} بنسخ متعارضة تحتاج قرار الخبير` : ""}`,
    orphans: (a, b) => `${a} صورة بلا نص، ${b} نص بلا صورة — لم تضف.`,
    regTitle: "السجل",
    tPages: "الأوراق", tReview: "تنتظر المراجعة", tApproved: "معتمدة", tLib: "في الخزانة",
    tLibSub: (v, c) => `${v} موثقة · ${c} متعارضة`,
    editRate: "نسبة تصحيح الخبير",
    editRateSub: "نسبة الحروف التي غيرها الخبير في كل ورقة معتمدة، بالترتيب الزمني. كلما نمت الخزانة ينبغي أن تنخفض.",
    noRate: "تظهر هنا نسبة التصحيح بعد اعتماد أول ورقة.",
    avgLast: n => `متوسط آخر ${n}`,
    evalTitle: "قياس الدقة",
    evalSub: "ينسخ Gemini أوراق الاختبار من الخزانة (التي لا تستعمل أمثلة أبدا) ويقارنها بنصوص الخبير.",
    evalRun: n => `قس على ${n} ورقة اختبار`,
    evalNone: "لم يجر قياس بعد.",
    evalRes: (c, l, w, n) => `معدل خطأ الحروف ${c} · (مرن ${l}) · معدل خطأ الكلمات ${w} · على ${n} ورقة`,
    methodTitle: "منهج النسخ",
    modelLabel: "نموذج Gemini للنسخ", modelHint: "مثال: gemini-3.1-pro-preview",
    kLabel: "عدد الأمثلة لكل ورقة", kHint: "أشبه الأوراق الموثقة في الخزانة ترسل مع الورقة.",
    samplesLabel: "عدد القراءات", samplesHint: "قراءتان تكشفان الأسطر غير المؤكدة لكنهما تضاعفان الكلفة.",
    criticLabel: "مدقق ثان يفحص كل نسخة",
    criticModelLabel: "نموذج المدقق",
    retriesLabel: "محاولات التصحيح الذاتي",
    notesLabel: "لغة ملاحظات المدقق",
    convLabel: "قواعد النسخ", convHint: "ترسل حرفيا مع كل ورقة. اكتب أعراف فريقك (رقم الورقة، الأختام، الحواشي…).",
    saveMethod: "احفظ المنهج",
    saved: "حفظ",
    downloadAll: "نزل كل المعتمد (zip)",
    driveOn: "Google Drive متصل: الأوراق الجديدة تقرأ من مجلد الوارد، والنصوص المعتمدة تكتب في مجلد النتائج.",
    driveOff: "Google Drive غير متصل: الملفات محفوظة مؤقتا على الخادم وقد تضيع عند إعادة تشغيله. نزل نتائجك، أو صل Drive (انظر دليل الإعداد).",
    noGemini: "مفتاح Gemini غير مضبوط. أضف GEMINI_API_KEY في إعدادات الـSpace ثم أعد تشغيله.",
    lastError: "آخر خطأ في الخادم:",
    loginTitle: "ادخل إلى الديوان",
    loginSub: "هذا الديوان محمي بكلمة مرور.",
    password: "كلمة المرور",
    enter: "ادخل",
    wrong: "كلمة المرور غير صحيحة.",
    offline: "تعذر الاتصال بالخادم. قد يكون الـSpace في طور التشغيل؛ أعد المحاولة بعد دقيقة.",
    footL: "عقود المحكمة الشرعية بالجزائر · الأرشيف الوطني لما وراء البحار (ANOM)، رصيد 1 MiOM 31",
    footR: "النسخ بواسطة Gemini · المراجعة بيد الخبير",
    flags: { empty: "لم يرجع النموذج أي نص.", not_arabic: "أقل من ٨٠٪ من الحروف عربية.", latin: "حروف لاتينية: ربما تعليق أو ترجمة.",
             markdown: "تنسيق Markdown في النص.", loop: "السطر نفسه مكرر ثلاث مرات أو أكثر.", repetitive: "أكثر من نصف الأسطر مكرر.",
             short: "أقصر بكثير من أوراق الخزانة.", long: "أطول بكثير من أوراق الخزانة.", uncertain_line: "القراءتان مختلفتان في هذا السطر." },
    removed: "أزيلت من القائمة",
    approved: "اعتمدت الورقة وحفظ النص",
    verifiedSaved: "حفظ النص الموثق",
    by: "بقلم",
    generic: "حدث خطأ. أعد المحاولة.",
  },
  en: {
    appName: "Dīwān al-Wathāʾiq",
    tagline: "Transcribing Maghrebi-script court deeds from Algiers, 18th–19th century",
    langBtn: "العربية",
    tabs: { pages: "Pages", review: "Review", library: "Library", register: "Register" },
    hijri: "Today",
    stepsTitle: "How the Diwan works",
    steps: [["Upload page scans", ".jpg scans or a .zip, or drop them in the Google Drive inbox folder."],
            ["Machine transcription", "Gemini reads the page with the most similar verified Library pages as examples, then a second checker reviews its work."],
            ["Review and approve", "An expert corrects the text line by line and approves it; the .txt is saved to the results folder and the page joins the Library."]],
    dropTitle: "Drop page scans here",
    dropSub: ".jpg, .png or .zip — or click to choose",
    pagesTitle: "Incoming pages",
    filterAll: "All",
    transcribeAll: n => `Transcribe all new (${n})`,
    transcribe: "Transcribe",
    open: "Open",
    stop: "Stop the queue",
    fetchDrive: "Fetch new pages from Drive",
    noPages: "No pages yet. Upload scans in the box above, or put them in the Drive inbox folder.",
    lines: n => `${n} lines`,
    status: { new: "New", queued: "Queued", transcribing: "Transcribing", review: "To review", approved: "Approved", rejected: "Rejected", error: "Error" },
    pair: { verified: "Verified", conflict: "Conflicting versions", unverified: "Unverified" },
    working: (n) => `The server is working… ${n ? `${n} waiting` : ""}`,
    task: { transcribe: "transcribing a page", sync: "syncing the Library from Drive", discover: "looking for new pages in Drive", eval: "measuring accuracy" },
    uploading: p => `Uploading… ${p}`,
    uploaded: n => `${n} page(s) added`,
    reviewEmpty: "Pick a page from Pages or the Library to review it here.",
    prev: "Previous", next: "Next",
    confidence: "Checker confidence",
    noConfidence: "Not checked yet",
    editorLabel: "Validated transcription",
    reviewer: "Reviewer name",
    approve: "Approve",
    saveDraft: "Save draft",
    reject: "Reject page",
    del: "Remove from list",
    delConfirm: "Confirm removal",
    download: "Download .txt",
    addLib: "Add this page and its correction to the Library",
    retrans: "Re-transcribe with a note",
    notePh: "e.g. line 4 is a marginal note; do not transcribe the seal",
    send: "Send to Gemini",
    saveVerified: "Save as verified",
    gtNotice: "Library check: correct the text so it matches the manuscript exactly. Only verified pages are used as examples.",
    altTitle: n => `Other version #${n} with the same name`,
    examplesUsed: "Examples used:",
    inQueue: "This page is in the transcription queue…",
    libTitle: "Library: verified pages and texts",
    libSub: "Image and text pairs the transcriber learns from. Files are matched by name: FRANOM88_1MIOM31_0038.jpg with FRANOM88_1MIOM31_0038.txt",
    libDrop: "Drop images and texts together, or a .zip",
    expert: "These texts were checked by an expert",
    syncDrive: "Sync the Library from Drive",
    libEmpty: "The Library is empty. Sync it from Drive or add image and text pairs.",
    colPage: "Page", colState: "State", colFirst: "First line", colLines: "Lines", colSplit: "Set", colAct: "",
    split: { train: "Learning", val: "Validation", test: "Test" },
    verify: "Check",
    pairsAdded: (n, c) => `${n} pair(s) added${c ? `, ${c} with conflicting versions that need an expert decision` : ""}`,
    orphans: (a, b) => `${a} image(s) without text, ${b} text(s) without image — not added.`,
    regTitle: "Register",
    tPages: "Pages", tReview: "Awaiting review", tApproved: "Approved", tLib: "In the Library",
    tLibSub: (v, c) => `${v} verified · ${c} conflicting`,
    editRate: "Expert correction rate",
    editRateSub: "Share of characters the expert changed on each approved page, in time order. It should fall as the Library grows.",
    noRate: "The correction rate appears here after the first approval.",
    avgLast: n => `average of last ${n}`,
    evalTitle: "Measure accuracy",
    evalSub: "Gemini transcribes the Library's test pages (never used as examples) and compares them with the expert texts.",
    evalRun: n => `Measure on ${n} test pages`,
    evalNone: "No measurement yet.",
    evalRes: (c, l, w, n) => `Character error rate ${c} · (loose ${l}) · word error rate ${w} · on ${n} pages`,
    methodTitle: "Transcription method",
    modelLabel: "Gemini model for transcription", modelHint: "e.g. gemini-3.1-pro-preview",
    kLabel: "Examples per page", kHint: "The most similar verified Library pages are sent with each page.",
    samplesLabel: "Readings per page", samplesHint: "Two readings reveal uncertain lines but double the cost.",
    criticLabel: "Second checker reviews each transcription",
    criticModelLabel: "Checker model",
    retriesLabel: "Self-correction rounds",
    notesLabel: "Language of the checker's notes",
    convLabel: "Transcription rules", convHint: "Sent word for word with every page. Write your team's conventions (folio number, seals, marginal notes…).",
    saveMethod: "Save method",
    saved: "Saved",
    downloadAll: "Download all approved (.zip)",
    driveOn: "Google Drive is connected: new pages are read from the inbox folder and approved texts are written to the results folder.",
    driveOff: "Google Drive is not connected: files are kept on the server temporarily and can be lost when it restarts. Download your results, or connect Drive (see the setup guide).",
    noGemini: "The Gemini key is not set. Add GEMINI_API_KEY in the Space settings, then restart it.",
    lastError: "Last server error:",
    loginTitle: "Enter the Diwan",
    loginSub: "This Diwan is protected by a password.",
    password: "Password",
    enter: "Enter",
    wrong: "Wrong password.",
    offline: "Can't reach the server. The Space may be starting; try again in a minute.",
    footL: "Sharia court deeds of Algiers · Archives nationales d'outre-mer (ANOM), fonds 1 MiOM 31",
    footR: "Transcribed by Gemini · reviewed by an expert",
    flags: { empty: "The model returned no text.", not_arabic: "Less than 80% of letters are Arabic.", latin: "Latin letters: possible commentary or translation.",
             markdown: "Markdown formatting in the text.", loop: "Same line repeated 3+ times.", repetitive: "More than half of the lines are duplicates.",
             short: "Much shorter than Library pages.", long: "Much longer than Library pages.", uncertain_line: "The two readings disagree on this line." },
    removed: "Removed from the list",
    approved: "Page approved and text saved",
    verifiedSaved: "Verified text saved",
    by: "by",
    generic: "Something went wrong. Try again.",
  }
};

/* ====================================================================== state */
const S = {
  lang: "ar", view: "pages", token: "", reviewer: "",
  pages: [], pairs: [], info: null, loaded: false, offline: false,
  sel: null, detail: null, editor: { key: null, dirty: false, stamp: null },
  filter: "all", upload: null, confirmDel: null, pollT: null,
};
try {
  S.lang = localStorage.getItem("diwan.lang") || "ar";
  S.token = localStorage.getItem("diwan.token") || "";
  S.reviewer = localStorage.getItem("diwan.reviewer") || "";
} catch (e) {}
const L = () => STR[S.lang];
const store = (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} };

/* ====================================================================== helpers */
const $ = (s, r = document) => r.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const num = n => new Intl.NumberFormat(S.lang === "ar" ? "ar-EG" : "en").format(n);
const pct = x => new Intl.NumberFormat(S.lang === "ar" ? "ar-EG" : "en", { style: "percent", maximumFractionDigits: 1 }).format(x);
const star = () => '<svg aria-hidden="true"><use href="#i-star"/></svg>';
const withKey = u => S.token ? u + (u.includes("?") ? "&" : "?") + "k=" + encodeURIComponent(S.token) : u;
function toast(msg) { const el = $("#toast"); el.textContent = msg; el.hidden = false; clearTimeout(toast.t); toast.t = setTimeout(() => { el.hidden = true; }, 3600); }

async function api(path, opts = {}) {
  const headers = { ...(opts.headers || {}) };
  if (S.token) headers["X-Diwan-Key"] = S.token;
  let body = opts.body;
  if (opts.json !== undefined) { headers["Content-Type"] = "application/json"; body = JSON.stringify(opts.json); }
  let r;
  try { r = await fetch(path, { method: opts.method || (body ? "POST" : "GET"), headers, body }); }
  catch (e) { S.offline = true; renderNotices(); throw { message: L().offline }; }
  S.offline = false;
  if (r.status === 401) { showLogin(); throw { code: "auth", message: L().wrong }; }
  if (!r.ok) { let m = ""; try { m = (await r.json()).detail; } catch (e) {} throw { message: typeof m === "string" && m ? m : L().generic }; }
  return (r.headers.get("content-type") || "").includes("json") ? r.json() : r;
}
function upload(path, files, extra = {}) {
  return new Promise((resolve, reject) => {
    const fd = new FormData(); files.forEach(f => fd.append("files", f, f.name));
    Object.entries(extra).forEach(([k, v]) => fd.append(k, v));
    const x = new XMLHttpRequest(); x.open("POST", path);
    if (S.token) x.setRequestHeader("X-Diwan-Key", S.token);
    x.upload.onprogress = e => { if (e.lengthComputable && S.upload) { S.upload.p = e.loaded / e.total; paintUpload(); } };
    x.onload = () => { if (x.status === 401) { showLogin(); reject({ message: L().wrong }); } else if (x.status < 300) resolve(JSON.parse(x.responseText)); else { let m = ""; try { m = JSON.parse(x.responseText).detail; } catch (e) {} reject({ message: m || L().generic }); } };
    x.onerror = () => reject({ message: L().offline });
    x.send(fd);
  });
}
function saveFile(url) { const a = document.createElement("a"); a.href = withKey(url); a.download = ""; document.body.append(a); a.click(); a.remove(); }

/* ====================================================================== login & polling */
function showLogin() {
  const box = $("#login"); box.hidden = false;
  $("#loginTitle").textContent = L().loginTitle; $("#loginSub").textContent = L().loginSub;
  $("#pwLabel").textContent = L().password; $("#loginBtn").textContent = L().enter;
  setTimeout(() => $("#pw").focus(), 50);
}
$("#loginForm").addEventListener("submit", async e => {
  e.preventDefault(); $("#loginErr").textContent = "";
  try {
    const r = await fetch("api/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ password: $("#pw").value }) });
    if (!r.ok) { $("#loginErr").textContent = L().wrong; return; }
    S.token = (await r.json()).token; store("diwan.token", S.token);
    $("#login").hidden = true; $("#pw").value = ""; poll();
  } catch (err) { $("#loginErr").textContent = L().offline; }
});

async function poll() {
  clearTimeout(S.pollT);
  try {
    const data = await api("api/state");
    S.pages = data.pages; S.pairs = data.pairs; S.info = data; S.loaded = true;
    onData();
  } catch (e) { if (e.code !== "auth") renderNotices(); }
  const busy = S.info && (S.info.worker.current || S.info.worker.queued.length);
  S.pollT = setTimeout(poll, busy ? 3000 : 15000);
}
function onData() {
  renderTabs(); renderNotices();
  if (S.view === "review") refreshDetail(); else renderView(true);
}

/* ====================================================================== routing & chrome */
const VIEWS = ["pages", "review", "library", "register"];
function route() {
  const h = (location.hash || "").slice(1);
  S.view = VIEWS.includes(h) ? h : "pages";
  for (const v of VIEWS) $("#view-" + v).hidden = v !== S.view;
  renderTabs();
  if (S.view === "review") { S.editor.key = null; refreshDetail(true); } else renderView();
}
window.addEventListener("hashchange", route);
function go(view) { if (location.hash !== "#" + view) location.hash = view; else route(); }

function applyLang() {
  const ar = S.lang === "ar";
  document.documentElement.lang = ar ? "ar" : "en";
  document.documentElement.dir = ar ? "rtl" : "ltr";
  $("#appName").textContent = L().appName; $("#tagline").textContent = L().tagline;
  $("#langBtn").textContent = L().langBtn; $("#footL").textContent = L().footL; $("#footR").textContent = L().footR;
  const d = new Date(); let hijri = "", greg = "";
  try { hijri = new Intl.DateTimeFormat(ar ? "ar-u-ca-islamic-umalqura-nu-arab" : "en-u-ca-islamic-umalqura", { day: "numeric", month: "long", year: "numeric" }).format(d); } catch (e) {}
  try { greg = new Intl.DateTimeFormat(ar ? "ar-DZ-u-nu-arab" : "en-GB", { day: "numeric", month: "long", year: "numeric" }).format(d); } catch (e) {}
  $("#dateChip").innerHTML = `${esc(L().hijri)} · <b>${esc(hijri)}</b>${greg ? " · " + esc(greg) : ""}`;
}
$("#langBtn").addEventListener("click", () => {
  S.lang = S.lang === "ar" ? "en" : "ar"; store("diwan.lang", S.lang);
  S.editor.key = null; applyLang(); renderTabs(); renderNotices();
  if (S.view === "review") refreshDetail(true); else renderView();
});

function renderTabs() {
  const c = { pages: S.pages.length, review: S.pages.filter(p => p.status === "review").length, library: S.pairs.length };
  $("#tabs").innerHTML = VIEWS.map(v => `<a href="#${v}" ${S.view === v ? 'aria-current="page"' : ""}>${esc(L().tabs[v])}${c[v] ? `<span class="count">${num(c[v])}</span>` : ""}</a>`).join("");
}
function renderNotices() {
  const t = L(), n = [], i = S.info;
  if (S.offline) n.push(`<div class="notice warn">${esc(t.offline)}</div>`);
  if (i) {
    if (!i.gemini) n.push(`<div class="notice warn">${esc(t.noGemini)}</div>`);
    n.push(`<div class="notice">${esc(i.drive ? t.driveOn : t.driveOff)}</div>`);
    if (i.error) n.push(`<div class="notice warn">${esc(t.lastError)} <span class="mono">${esc(i.error)}</span></div>`);
    const w = i.worker;
    if (w.current || w.queued.length) {
      const what = w.current ? (t.task[w.current.kind] || "") : "";
      n.push(`<div class="panel queue" aria-live="polite"><span class="chip st-transcribing">${esc(t.status.transcribing)}</span>
        <span class="small">${esc(t.working(w.queued.length ? num(w.queued.length) : ""))} ${esc(what)}</span>
        <span style="flex:1"></span>${w.queued.length ? `<button class="btn sm danger" id="stopQueue">${esc(t.stop)}</button>` : ""}</div>`);
    }
  }
  $("#notices").innerHTML = n.join("");
  $("#stopQueue")?.addEventListener("click", async () => { await api("api/stop", { method: "POST" }); poll(); });
}
function renderView(fromData) {
  if (S.view === "pages") renderPages();
  else if (S.view === "library") renderLibrary();
  else if (S.view === "register") renderRegister(fromData);
}
function chip(status, kind = "page") {
  const label = kind === "page" ? L().status[status] : L().pair[status];
  return `<span class="chip st-${esc(status)}">${esc(label || status)}</span>`;
}
const pairState = p => p.verified ? "verified" : (p.conflict ? "conflict" : "unverified");
const lineCount = t => (t || "").split("\n").filter(l => l.trim()).length;

/* ====================================================================== pages */
function renderPages() {
  const el = $("#view-pages"), t = L();
  const fresh = S.pages.filter(p => p.status === "new" || p.status === "error");
  const list = S.filter === "all" ? S.pages : S.pages.filter(p => p.status === S.filter);
  const statuses = ["all", "new", "queued", "review", "approved", "rejected", "error"].filter(s => s === "all" || S.pages.some(p => p.status === s));
  el.innerHTML = `
    <div class="intro">
      <label class="drop" id="pageDrop" for="pageFiles">
        <svg width="40" height="40" aria-hidden="true"><use href="#i-star"/></svg>
        <strong>${esc(t.dropTitle)}</strong>
        <span class="muted small">${esc(t.dropSub)}</span>
        <div id="upPages"></div>
        <input type="file" id="pageFiles" multiple accept=".jpg,.jpeg,.png,.webp,.tif,.tiff,.zip,image/*">
      </label>
      <div class="panel steps">
        <h3>${esc(t.stepsTitle)}</h3>
        <ol>${t.steps.map((s, i) => `<li><span class="n">${num(i + 1)}</span><div><b>${esc(s[0])}</b><span>${esc(s[1])}</span></div></li>`).join("")}</ol>
      </div>
    </div>
    <div class="toolbar">
      <h2 class="sec">${star()}${esc(t.pagesTitle)}</h2>
      <div class="row">
        ${statuses.length > 1 ? `<select id="pageFilter" aria-label="Filter" class="btn sm">${statuses.map(s => `<option value="${s}" ${S.filter === s ? "selected" : ""}>${esc(s === "all" ? t.filterAll : t.status[s])}</option>`).join("")}</select>` : ""}
        ${S.info && S.info.drive ? `<button class="btn" id="fetchDrive">${esc(t.fetchDrive)}</button>` : ""}
        <button class="btn primary" id="runAll" ${!fresh.length ? "disabled" : ""}>${esc(t.transcribeAll(num(fresh.length)))}</button>
      </div>
    </div>
    ${!S.loaded ? `<div class="empty">…</div>` : list.length ? `<div class="grid-cards">${list.map(pageCard).join("")}</div>` : `<div class="empty">${esc(t.noPages)}</div>`}`;
  paintUpload();
  wireDrop("#pageDrop", "#pageFiles", ingestPages);
  $("#pageFilter")?.addEventListener("change", e => { S.filter = e.target.value; renderPages(); });
  $("#runAll")?.addEventListener("click", async () => { try { await api("api/transcribe-all", { method: "POST" }); poll(); } catch (e) { toast(e.message); } });
  $("#fetchDrive")?.addEventListener("click", async () => { try { await api("api/discover", { method: "POST" }); poll(); } catch (e) { toast(e.message); } });
  el.querySelectorAll("[data-open]").forEach(b => {
    b.addEventListener("click", () => openItem("page", b.dataset.open));
    if (b.getAttribute("role") === "button") b.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openItem("page", b.dataset.open); } });
  });
  el.querySelectorAll("[data-run]").forEach(b => b.addEventListener("click", () => runOne(b.dataset.run)));
}
function pageCard(p) {
  const t = L();
  return `<article class="card">
    <div class="thumb" data-open="${esc(p.id)}" role="button" tabindex="0" aria-label="${esc(t.open)} ${esc(p.stem)}">
      <img loading="lazy" src="${esc(withKey("api/pages/" + encodeURIComponent(p.id) + "/image"))}" alt="">${chip(p.status)}
    </div>
    <div class="body">
      <div class="name">${esc(p.stem)}</div>
      ${p.preview ? `<div class="preview">${esc(p.preview)}</div>` : ""}
      <div class="meta">${p.lines ? `<span>${esc(t.lines(num(p.lines)))}</span>` : ""}${p.confidence != null ? `<span>${esc(t.confidence)} ${pct(p.confidence)}</span>` : ""}</div>
      <div class="actions">
        <button class="btn sm" data-open="${esc(p.id)}">${esc(t.open)}</button>
        ${p.status === "new" || p.status === "error" ? `<button class="btn sm primary" data-run="${esc(p.id)}">${esc(t.transcribe)}</button>` : ""}
      </div>
    </div>
  </article>`;
}
async function runOne(id, note) {
  try { await api("api/pages/" + encodeURIComponent(id) + "/transcribe", { json: { note: note || "" } }); poll(); }
  catch (e) { toast(e.message); }
}
function wireDrop(dropSel, inputSel, handler) {
  const d = $(dropSel), inp = $(inputSel); if (!d || !inp) return;
  inp.addEventListener("change", () => { if (inp.files.length) handler([...inp.files]); inp.value = ""; });
  ["dragenter", "dragover"].forEach(ev => d.addEventListener(ev, e => { e.preventDefault(); d.classList.add("over"); }));
  ["dragleave", "drop"].forEach(ev => d.addEventListener(ev, e => { e.preventDefault(); d.classList.remove("over"); }));
  d.addEventListener("drop", e => { const f = [...(e.dataTransfer?.files || [])]; if (f.length) handler(f); });
}
function paintUpload() {
  for (const [sel, kind] of [["#upPages", "pages"], ["#upPairs", "pairs"]]) {
    const box = $(sel); if (!box) continue;
    box.innerHTML = S.upload && S.upload.kind === kind ? `<div class="progress"><i style="width:${(S.upload.p || 0) * 100}%"></i></div><span class="small muted">${esc(L().uploading(Math.round((S.upload.p || 0) * 100) + "%"))}</span>` : "";
  }
}
/* send files in batches so a big folder doesn't become one huge request */
function batches(files, maxBytes = 60e6) {
  const out = []; let cur = [], size = 0;
  for (const f of files) { if (cur.length && size + f.size > maxBytes) { out.push(cur); cur = []; size = 0; } cur.push(f); size += f.size; }
  if (cur.length) out.push(cur); return out;
}
async function ingestPages(files) {
  let added = 0;
  try {
    for (const b of batches(files)) { S.upload = { kind: "pages", p: 0 }; paintUpload(); added += (await upload("api/pages/upload", b)).added; }
    toast(L().uploaded(num(added)));
  } catch (e) { toast(e.message); }
  S.upload = null; paintUpload(); poll();
}

/* ====================================================================== review */
function openItem(kind, id) { S.sel = { kind, id }; S.detail = null; S.editor = { key: null, dirty: false, stamp: null }; S.confirmDel = null; go("review"); }
async function refreshDetail(force) {
  if (!S.sel) {
    const first = S.pages.find(p => p.status === "review");
    if (first) S.sel = { kind: "page", id: first.id };
  }
  if (!S.sel) { $("#view-review").innerHTML = `<div class="empty">${esc(L().reviewEmpty)}</div>`; return; }
  const summary = S.sel.kind === "page" ? S.pages.find(p => p.id === S.sel.id) : S.pairs.find(p => p.stem === S.sel.id);
  const stamp = summary ? JSON.stringify(summary) : null;
  if (!force && S.detail && stamp === S.editor.stamp) return;
  try {
    S.detail = await api(S.sel.kind === "page" ? "api/pages/" + encodeURIComponent(S.sel.id) : "api/pairs/" + encodeURIComponent(S.sel.id));
  } catch (e) { if (e.code !== "auth") { S.sel = null; S.detail = null; $("#view-review").innerHTML = `<div class="empty">${esc(L().reviewEmpty)}</div>`; } return; }
  S.editor.stamp = stamp;
  renderReview();
}
function siblings() {
  if (!S.sel) return [];
  if (S.sel.kind === "pair") return S.pairs.map(p => p.stem);
  const rev = S.pages.filter(p => p.status === "review" || p.id === S.sel.id);
  return (rev.length > 1 ? rev : S.pages).map(p => p.id);
}
function renderReview() {
  const el = $("#view-review"), t = L(), it = S.detail; if (!it) return;
  const isPair = S.sel.kind === "pair";
  const key = S.sel.kind + ":" + S.sel.id + ":" + S.lang;
  const textNow = isPair ? it.text : (it.final || it.draft || "");
  const state = isPair ? pairState(it) : it.status;
  if (S.editor.key === key) {               /* same page: keep unsaved edits, refresh the rest */
    const ta = $("#editor");
    if (ta && !S.editor.dirty && ta.value !== textNow) { ta.value = textNow; syncGutter(); }
    renderSide(it, isPair);
    if (S.editor.state !== state) { S.editor.state = state; const c = $("#wsChip"); if (c) c.innerHTML = isPair ? chip(state, "pair") : chip(state); renderActions(it, isPair); }
    return;
  }
  S.editor.key = key; S.editor.dirty = false; S.editor.state = state;
  const sib = siblings(), idx = sib.indexOf(S.sel.id);
  const imgUrl = withKey(isPair ? "api/pairs/" + encodeURIComponent(it.stem) + "/image" : "api/pages/" + encodeURIComponent(it.id) + "/image");
  el.innerHTML = `
    <div class="ws-nav">
      <div class="ws-title"><span id="wsChip">${isPair ? chip(state, "pair") : chip(state)}</span><span class="name">${esc(it.stem)}</span></div>
      <div class="row">
        <button class="btn sm" id="prevItem" ${idx <= 0 ? "disabled" : ""}>${esc(t.prev)}</button>
        <button class="btn sm" id="nextItem" ${idx < 0 || idx >= sib.length - 1 ? "disabled" : ""}>${esc(t.next)}</button>
      </div>
    </div>
    ${isPair ? `<div class="notice">${esc(t.gtNotice)}</div>` : ""}
    <div class="ws">
      <div class="door">
        <div class="scan" id="scan"><img id="scanImg" src="${esc(imgUrl)}" alt="${esc(it.stem)}"></div>
        <div class="zoom"><span>−</span><input type="range" id="zoom" min="60" max="400" step="10" value="100" aria-label="Zoom"><span>+</span><span class="mono" id="zoomVal">100%</span></div>
      </div>
      <div class="desk">
        <div id="side"></div>
        <div>
          <label class="small muted" for="editor" style="display:block;margin-bottom:6px">${esc(t.editorLabel)}</label>
          <div class="editor"><div class="gutter" id="gutter" aria-hidden="true"></div><textarea class="text" id="editor" spellcheck="false" dir="rtl">${esc(textNow)}</textarea></div>
        </div>
        <div class="field" style="max-width:260px"><label for="reviewerName" class="small">${esc(t.reviewer)}</label>
          <input id="reviewerName" class="note" style="min-height:0" value="${esc(S.reviewer)}" autocomplete="name"></div>
        <div id="actions"></div>
      </div>
    </div>`;
  wireScan();
  const ta = $("#editor");
  ta.addEventListener("input", () => { S.editor.dirty = true; syncGutter(); });
  ta.addEventListener("scroll", () => { $("#gutter").scrollTop = ta.scrollTop; });
  $("#reviewerName").addEventListener("change", e => { S.reviewer = e.target.value.trim(); store("diwan.reviewer", S.reviewer); });
  $("#prevItem").addEventListener("click", () => { if (idx > 0) openItem(S.sel.kind, sib[idx - 1]); });
  $("#nextItem").addEventListener("click", () => { if (idx < sib.length - 1) openItem(S.sel.kind, sib[idx + 1]); });
  renderSide(it, isPair); renderActions(it, isPair); syncGutter();
}
function hotLines(it) { return new Set((it.flags || []).filter(f => f.line).map(f => +f.line)); }
function syncGutter() {
  const ta = $("#editor"), g = $("#gutter"); if (!ta || !g) return;
  const hot = S.detail ? hotLines(S.detail) : new Set(), n = Math.max(1, ta.value.split("\n").length);
  g.innerHTML = Array.from({ length: n }, (_, i) => `<div class="${hot.has(i + 1) ? "hot" : ""}">${i + 1}</div>`).join("");
  g.scrollTop = ta.scrollTop;
}
function renderSide(it, isPair) {
  const t = L(), side = $("#side"); if (!side) return;
  let h = "";
  if (!isPair) {
    const c = it.confidence;
    const color = c == null ? "var(--line)" : c >= 0.85 ? "var(--zellige)" : c >= 0.6 ? "var(--brass)" : "var(--seal)";
    h += `<div class="panel meter"><span class="small">${esc(t.confidence)}</span><div class="bar"><i style="width:${c == null ? 0 : c * 100}%;background:${color}"></i></div><span class="val">${c == null ? esc(t.noConfidence) : pct(c)}</span></div>`;
    if (it.status === "queued" || it.status === "transcribing") h += `<div class="panel live">${esc(t.inQueue)}</div>`;
    if (it.status === "error" && it.error) h += `<div class="flag hard"><span class="ln">!</span><span class="mono">${esc(it.error)}</span></div>`;
    const flags = it.flags || [];
    if (flags.length) h += `<div class="flags" style="margin-top:10px">${flags.map(f => {
      const msg = f.code === "critic" ? f.msg : (t.flags[f.code] || f.msg);
      return `<div class="flag ${f.hard ? "hard" : ""}"><span class="ln">${f.line ? (S.lang === "ar" ? "س " : "L") + num(f.line) : "•"}</span><span><bdi>${esc(msg)}</bdi>${f.fix ? ` ${S.lang === "ar" ? "←" : "→"} <bdi class="fix">${esc(f.fix)}</bdi>` : ""}</span></div>`;
    }).join("")}</div>`;
    if (it.examples && it.examples.length) h += `<p class="small muted" style="margin:8px 0 0">${esc(t.examplesUsed)} <span class="mono">${it.examples.map(esc).join(", ")}</span></p>`;
    if (it.reviewer && it.status === "approved") h += `<p class="small muted" style="margin:4px 0 0">${esc(t.status.approved)} ${esc(t.by)} ${esc(it.reviewer)}${it.reviewCer != null ? ` · ${esc(t.editRate)} ${pct(it.reviewCer)}` : ""}</p>`;
  } else {
    if (it.dupCer != null && it.dupCer > 0.02) h += `<div class="flag"><span class="ln">≠</span><span>${esc(S.lang === "ar" ? `النسختان تختلفان في ${pct(it.dupCer)} من الحروف.` : `The versions differ in ${pct(it.dupCer)} of characters.`)}</span></div>`;
    if ((it.alts || []).length) h += `<div class="alts" style="display:grid;gap:8px;margin-top:8px">${it.alts.map((a, i) => `<details><summary>${esc(t.altTitle(num(i + 1)))}</summary><pre>${esc(a)}</pre></details>`).join("")}</div>`;
    if (it.verifiedBy) h += `<p class="small muted" style="margin:6px 0 0">${esc(t.pair.verified)} ${esc(t.by)} ${esc(it.verifiedBy)}</p>`;
  }
  side.innerHTML = h; syncGutter();
}
function renderActions(it, isPair) {
  const t = L(), box = $("#actions"); if (!box) return;
  const txtUrl = isPair ? null : "api/pages/" + encodeURIComponent(it.id) + "/txt";
  if (isPair) {
    box.innerHTML = `<div class="row"><button class="btn primary" id="saveVer">${esc(t.saveVerified)}</button></div>`;
    $("#saveVer").addEventListener("click", () => saveVerified(it));
    return;
  }
  const busy = it.status === "queued" || it.status === "transcribing";
  box.innerHTML = `
    <div class="row" style="margin-bottom:10px"><label class="check"><input type="checkbox" id="addLib" checked> ${esc(t.addLib)}</label></div>
    <div class="row">
      <button class="btn primary" id="approve" ${busy ? "disabled" : ""}>${esc(t.approve)}</button>
      <button class="btn" id="saveDraft" ${busy ? "disabled" : ""}>${esc(t.saveDraft)}</button>
      <button class="btn" id="dlOne">${esc(t.download)}</button>
      ${it.status === "new" || it.status === "error" ? `<button class="btn" id="runOne">${esc(t.transcribe)}</button>` : ""}
      <span style="flex:1"></span>
      <button class="btn danger sm" id="rejectItem">${esc(t.reject)}</button>
      <button class="btn danger sm" id="delItem">${esc(S.confirmDel === it.id ? t.delConfirm : t.del)}</button>
    </div>
    <details style="margin-top:12px"><summary class="small muted" style="cursor:pointer">${esc(t.retrans)}</summary>
      <div style="display:grid;gap:8px;margin-top:8px"><textarea class="note" id="noteBox" placeholder="${esc(t.notePh)}"></textarea>
      <div><button class="btn sm" id="sendNote" ${busy ? "disabled" : ""}>${esc(t.send)}</button></div></div></details>`;
  const body = () => ({ text: $("#editor").value, reviewer: S.reviewer, addToLibrary: !!$("#addLib")?.checked });
  $("#approve").addEventListener("click", async () => {
    if (!$("#editor").value.trim()) return;
    try {
      await api("api/pages/" + encodeURIComponent(it.id) + "/approve", { json: body() });
      S.editor.dirty = false; toast(t.approved); saveFile(txtUrl);
      await poll();
      const next = S.pages.find(p => p.status === "review" && p.id !== it.id);
      if (next) openItem("page", next.id); else refreshDetail(true);
    } catch (e) { toast(e.message); }
  });
  $("#saveDraft").addEventListener("click", async () => { try { await api("api/pages/" + encodeURIComponent(it.id) + "/draft", { json: body() }); S.editor.dirty = false; toast(t.saved); } catch (e) { toast(e.message); } });
  $("#dlOne").addEventListener("click", () => saveFile(txtUrl));
  $("#runOne")?.addEventListener("click", () => runOne(it.id));
  $("#sendNote").addEventListener("click", () => { S.editor.dirty = false; runOne(it.id, $("#noteBox").value.trim() || " "); });
  $("#rejectItem").addEventListener("click", async () => { try { await api("api/pages/" + encodeURIComponent(it.id) + "/reject", { json: body() }); poll(); } catch (e) { toast(e.message); } });
  $("#delItem").addEventListener("click", async () => {
    if (S.confirmDel !== it.id) { S.confirmDel = it.id; renderActions(it, false); return; }
    try { await api("api/pages/" + encodeURIComponent(it.id), { method: "DELETE" }); S.sel = null; S.detail = null; toast(t.removed); await poll(); go("pages"); } catch (e) { toast(e.message); }
  });
}
async function saveVerified(it) {
  try {
    await api("api/pairs/" + encodeURIComponent(it.stem) + "/verify", { json: { text: $("#editor").value, reviewer: S.reviewer } });
    S.editor.dirty = false; toast(L().verifiedSaved); await poll();
    const next = S.pairs.find(p => !p.verified && p.stem !== it.stem);
    if (next) openItem("pair", next.stem); else refreshDetail(true);
  } catch (e) { toast(e.message); }
}
function wireScan() {
  const scan = $("#scan"), img = $("#scanImg"), z = $("#zoom"); if (!scan || !img) return;
  const apply = () => { img.style.width = (scan.clientWidth * z.value / 100) + "px"; $("#zoomVal").textContent = z.value + "%"; };
  img.addEventListener("load", apply); z.addEventListener("input", apply); window.addEventListener("resize", apply); apply();
  let drag = null;
  scan.addEventListener("pointerdown", e => { if (e.pointerType === "touch") return; drag = { x: e.clientX, y: e.clientY, l: scan.scrollLeft, t: scan.scrollTop }; scan.classList.add("drag"); scan.setPointerCapture(e.pointerId); });
  scan.addEventListener("pointermove", e => { if (!drag) return; scan.scrollLeft = drag.l - (e.clientX - drag.x); scan.scrollTop = drag.t - (e.clientY - drag.y); });
  const end = () => { drag = null; scan.classList.remove("drag"); };
  scan.addEventListener("pointerup", end); scan.addEventListener("pointercancel", end);
}

/* ====================================================================== library */
function renderLibrary() {
  const el = $("#view-library"), t = L();
  const v = S.pairs.filter(p => p.verified).length, c = S.pairs.filter(p => p.conflict && !p.verified).length;
  const rows = [...S.pairs].sort((a, b) => (a.verified - b.verified) || ((b.dupCer || 0) - (a.dupCer || 0)) || a.stem.localeCompare(b.stem));
  el.innerHTML = `
    <div class="lib-head">
      <div>
        <h2 class="sec">${star()}${esc(t.libTitle)}</h2>
        <p class="muted small" style="margin:0 0 10px;max-width:62ch">${esc(t.libSub)}</p>
        <div class="legend">${chip("verified", "pair")} ${num(v)} ${chip("conflict", "pair")} ${num(c)} ${chip("unverified", "pair")} ${num(S.pairs.length - v - c)}</div>
        ${S.info && S.info.drive ? `<div class="row" style="margin-top:14px"><button class="btn" id="syncDrive">${esc(t.syncDrive)}</button>
          ${S.info.sync ? `<span class="small muted mono">${esc(S.info.sync.at)}</span>` : ""}</div>` : ""}
      </div>
      <div style="display:grid;gap:8px">
        <label class="drop" id="libDrop" for="libFiles" style="min-height:130px">
          <strong>${esc(t.libDrop)}</strong>
          <span class="muted small">.jpg + .txt · .zip</span>
          <div id="upPairs"></div>
          <input type="file" id="libFiles" multiple accept=".jpg,.jpeg,.png,.webp,.txt,.zip,image/*,text/plain">
        </label>
        <label class="check"><input type="checkbox" id="expert" checked> ${esc(t.expert)}</label>
      </div>
    </div>
    ${S.pairs.length ? `<div class="tablebox"><table class="list">
      <thead><tr><th>${esc(t.colPage)}</th><th>${esc(t.colState)}</th><th>${esc(t.colFirst)}</th><th>${esc(t.colLines)}</th><th>${esc(t.colSplit)}</th><th>${esc(t.colAct)}</th></tr></thead>
      <tbody>${rows.map(p => `<tr>
        <td class="name">${esc(p.stem)}</td><td>${chip(pairState(p), "pair")}</td>
        <td class="first">${esc(p.first)}</td><td class="mono">${num(p.lines)}</td>
        <td class="small muted">${esc(t.split[p.split] || "")}</td>
        <td><button class="btn sm" data-pair="${esc(p.stem)}">${esc(p.verified ? t.open : t.verify)}</button></td>
      </tr>`).join("")}</tbody></table></div>` : `<div class="empty">${esc(t.libEmpty)}</div>`}`;
  paintUpload();
  wireDrop("#libDrop", "#libFiles", ingestPairs);
  $("#syncDrive")?.addEventListener("click", async () => { try { await api("api/sync", { method: "POST" }); poll(); } catch (e) { toast(e.message); } });
  el.querySelectorAll("[data-pair]").forEach(b => b.addEventListener("click", () => openItem("pair", b.dataset.pair)));
}
async function ingestPairs(files) {
  const expert = $("#expert") ? $("#expert").checked : true;
  /* keep each image with its texts in the same batch */
  const key = f => f.name.replace(/\.[^.]+$/, "").replace(/\s*\(\d+\)$/, "").replace(/\s+\d+$/, "").trim();
  const zips = files.filter(f => /\.zip$/i.test(f.name)), groups = new Map();
  files.filter(f => !/\.zip$/i.test(f.name)).forEach(f => { const k = key(f); if (!groups.has(k)) groups.set(k, []); groups.get(k).push(f); });
  const units = [...zips.map(z => [z]), ...groups.values()];
  const chunks = []; let cur = [], size = 0;
  for (const u of units) { const s = u.reduce((a, f) => a + f.size, 0); if (cur.length && size + s > 60e6) { chunks.push(cur); cur = []; size = 0; } cur.push(...u); size += s; }
  if (cur.length) chunks.push(cur);
  const tot = { added: 0, conflicts: 0, imagesWithoutText: 0, textsWithoutImage: 0 };
  try {
    for (const c of chunks) {
      S.upload = { kind: "pairs", p: 0 }; paintUpload();
      const r = await upload("api/pairs/upload", c, { expert: expert ? "true" : "false" });
      for (const k in tot) tot[k] += r[k] || 0;
    }
    const t = L();
    toast(t.pairsAdded(num(tot.added), tot.conflicts ? num(tot.conflicts) : 0) + (tot.imagesWithoutText || tot.textsWithoutImage ? " " + t.orphans(num(tot.imagesWithoutText), num(tot.textsWithoutImage)) : ""));
  } catch (e) { toast(e.message); }
  S.upload = null; paintUpload(); poll();
}

/* ====================================================================== register */
function renderRegister(fromData) {
  const el = $("#view-register"), t = L();
  if (fromData && $("#methodForm")) { renderRegisterTop(); return; }
  const st = (S.info && S.info.settings) || {};
  el.innerHTML = `
    <h2 class="sec">${star()}${esc(t.regTitle)}</h2>
    <div id="regTop"></div>
    <div class="reg">
      <div style="display:grid;gap:18px">
        <div class="panel chart" id="chartBox"></div>
        <div class="panel form" id="evalBox"></div>
      </div>
      <form class="panel form" id="methodForm">
        <h3>${esc(t.methodTitle)}</h3>
        <div class="two">
          <div class="field"><label for="fModel">${esc(t.modelLabel)}</label><input id="fModel" class="note" style="min-height:0;direction:ltr" value="${esc(st.model || "")}"><span class="hint">${esc(t.modelHint)}</span></div>
          <div class="field"><label for="fK">${esc(t.kLabel)}</label><input id="fK" type="number" min="0" max="6" value="${+st.k || 0}"><span class="hint">${esc(t.kHint)}</span></div>
          <div class="field"><label for="fSamples">${esc(t.samplesLabel)}</label><input id="fSamples" type="number" min="1" max="3" value="${+st.samples || 1}"><span class="hint">${esc(t.samplesHint)}</span></div>
          <div class="field"><label for="fRetries">${esc(t.retriesLabel)}</label><input id="fRetries" type="number" min="0" max="2" value="${+st.retries || 0}"></div>
          <div class="field"><label for="fCriticModel">${esc(t.criticModelLabel)}</label><input id="fCriticModel" class="note" style="min-height:0;direction:ltr" value="${esc(st.critic_model || "")}"></div>
          <div class="field"><label for="fNotes">${esc(t.notesLabel)}</label><select id="fNotes">${["Arabic", "English", "French"].map(l => `<option ${st.notes_language === l ? "selected" : ""}>${l}</option>`).join("")}</select></div>
        </div>
        <label class="check"><input type="checkbox" id="fCritic" ${st.critic ? "checked" : ""}> ${esc(t.criticLabel)}</label>
        <div class="field"><label for="fConv">${esc(t.convLabel)}</label><textarea id="fConv" dir="ltr">${esc(st.conventions || "")}</textarea><span class="hint">${esc(t.convHint)}</span></div>
        <div><button class="btn primary" type="submit">${esc(t.saveMethod)}</button></div>
      </form>
    </div>`;
  renderRegisterTop();
  $("#methodForm").addEventListener("submit", async e => {
    e.preventDefault();
    const v = { model: $("#fModel").value, k: +$("#fK").value, samples: +$("#fSamples").value, retries: +$("#fRetries").value,
      critic_model: $("#fCriticModel").value, notes_language: $("#fNotes").value, critic: $("#fCritic").checked, conventions: $("#fConv").value };
    try { const s = await api("api/settings", { json: v }); if (S.info) S.info.settings = s; toast(L().saved); } catch (err) { toast(err.message); }
  });
}
function renderRegisterTop() {
  const t = L(), box = $("#regTop"); if (!box) return;
  const ok = S.pages.filter(p => p.status === "approved");
  const v = S.pairs.filter(p => p.verified).length, c = S.pairs.filter(p => p.conflict && !p.verified).length;
  box.innerHTML = `<div class="tiles">
      <div class="panel tile"><div class="k">${esc(t.tPages)}</div><div class="v">${num(S.pages.length)}</div></div>
      <div class="panel tile"><div class="k">${esc(t.tReview)}</div><div class="v" style="color:var(--seal)">${num(S.pages.filter(p => p.status === "review").length)}</div></div>
      <div class="panel tile"><div class="k">${esc(t.tApproved)}</div><div class="v" style="color:var(--zellige)">${num(ok.length)}</div>
        ${ok.length ? `<button class="btn ghost sm" id="dlAll">${esc(t.downloadAll)}</button>` : ""}</div>
      <div class="panel tile"><div class="k">${esc(t.tLib)}</div><div class="v">${num(S.pairs.length)}</div><div class="s">${esc(t.tLibSub(num(v), num(c)))}</div></div>
    </div>`;
  $("#dlAll")?.addEventListener("click", () => saveFile("api/approved.zip"));
  drawChart(ok); renderEval();
}
function renderEval() {
  const t = L(), box = $("#evalBox"); if (!box) return;
  const e = S.info && S.info.eval, tests = S.pairs.filter(p => p.split === "test").length;
  box.innerHTML = `<h3>${esc(t.evalTitle)}</h3><p class="muted small" style="margin:0">${esc(t.evalSub)}</p>
    <p class="small" style="margin:0">${e ? esc(t.evalRes(pct(e.cer), pct(e.cer_loose), pct(e.wer), num(e.pages))) + ` <span class="muted mono">${esc(e.model || "")} · ${esc((e.at || "").slice(0, 10))}</span>` : esc(t.evalNone)}</p>
    <div><button class="btn" id="runEval" ${tests ? "" : "disabled"}>${esc(t.evalRun(num(Math.min(20, tests))))}</button></div>`;
  $("#runEval")?.addEventListener("click", async () => { try { await api("api/eval", { json: { n: 20 } }); poll(); } catch (err) { toast(err.message); } });
}
function drawChart(approved) {
  const t = L(), box = $("#chartBox"); if (!box) return;
  const pts = approved.filter(p => p.reviewCer != null).sort((a, b) => String(a.approvedAt).localeCompare(String(b.approvedAt)));
  if (!pts.length) { box.innerHTML = `<h3>${esc(t.editRate)}</h3><p class="muted small">${esc(t.editRateSub)}</p><div class="empty">${esc(t.noRate)}</div>`; return; }
  const W = 560, H = 230, pl = 40, pr = 14, pt = 12, pb = 26;
  const maxV = Math.max(0.1, Math.ceil(Math.max(...pts.map(p => p.reviewCer)) * 10) / 10);
  const x = i => pts.length === 1 ? pl + (W - pl - pr) / 2 : pl + i * (W - pl - pr) / (pts.length - 1);
  const y = v => pt + (1 - v / maxV) * (H - pt - pb);
  const line = pts.map((p, i) => `${i ? "L" : "M"}${x(i).toFixed(1)} ${y(p.reviewCer).toFixed(1)}`).join(" ");
  const area = `${line} L${x(pts.length - 1).toFixed(1)} ${y(0)} L${x(0).toFixed(1)} ${y(0)} Z`;
  const lastN = Math.min(10, pts.length), avg = pts.slice(-lastN).reduce((s, p) => s + p.reviewCer, 0) / lastN;
  box.innerHTML = `<h3>${esc(t.editRate)}</h3><p class="muted small" style="margin-top:0">${esc(t.editRateSub)}</p>
    <svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(t.editRate)}" style="direction:ltr">
      ${[0, maxV / 2, maxV].map(v => `<line class="ax" x1="${pl}" x2="${W - pr}" y1="${y(v)}" y2="${y(v)}" stroke-dasharray="${v ? "3 4" : ""}"/><text class="tick" x="${pl - 6}" y="${y(v) + 3}" text-anchor="end">${Math.round(v * 100)}%</text>`).join("")}
      <path class="ar" d="${area}" opacity=".6"/><path class="ln" d="${line}"/>
      ${pts.map((p, i) => `<circle class="${i === pts.length - 1 ? "end" : "pt"}" cx="${x(i)}" cy="${y(p.reviewCer)}" r="${i === pts.length - 1 ? 5 : 3.5}"><title>${esc(p.stem)} · ${Math.round(p.reviewCer * 100)}%</title></circle>`).join("")}
      ${pts.length > 1 ? `<text class="tick" x="${pl}" y="${H - 6}">1</text><text class="tick" x="${W - pr}" y="${H - 6}" text-anchor="end">${pts.length}</text>` : ""}
    </svg>
    <p class="small" style="margin:6px 0 0"><b class="mono">${pct(avg)}</b> <span class="muted">${esc(t.avgLast(num(lastN)))}</span></p>`;
}

/* ====================================================================== boot */
applyLang(); route(); poll();
})();
