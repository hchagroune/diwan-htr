/* Dīwān al-Wathāʾiq · "Try it". Plays recorded pilot data (assets/demo-data.js) with no network calls.
   Flow: pick a page → the scan is read line by line → the AI reader's draft types in → the AI checker
   flags doubtful lines → the visitor approves, corrects or sends back → approved lines become training data.
   Live mode (off by default) only reads the n8n board, with the team's access code. */
(function () {
  "use strict";
  var PAGES = window.DIWAN_PAGES || [];
  var DOOR = "https://hsm38.app.n8n.cloud/webhook/diwan-board";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (id) { return document.getElementById(id); };
  var AR_DIGITS = "٠١٢٣٤٥٦٧٨٩";

  var S = { page: null, lines: [], issues: [], conf: null, fixed: {}, round: 0, simulated: false, timer: null, typing: false };

  function lang() { return window.diwanLang ? window.diwanLang() : "ar"; }
  function L(ar, en) { return lang() === "ar" ? ar : en; }
  function num(n) { var s = String(n); return lang() === "ar" ? s.replace(/[0-9]/g, function (d) { return AR_DIGITS[d]; }) : s; }
  function pct(c) { return num(Math.round(c * 100)) + (lang() === "ar" ? "٪" : "%"); }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function status(msg) { $("status").textContent = msg || ""; }

  /* ---------- page picker ---------- */
  function drawPicker() {
    var box = $("pick"); box.innerHTML = "";
    PAGES.forEach(function (p) {
      var b = el("button", "page-btn"); b.type = "button";
      b.setAttribute("aria-pressed", S.page && S.page.id === p.id ? "true" : "false");
      b.appendChild(el("b", "", L("الصفحة ", "Page ") + num(p.id)));
      b.appendChild(el("span", "muted small", p.court[lang()]));
      b.appendChild(el("span", "muted small", p.date[lang()]));
      var st = p.expert.decision === "approved"
        ? el("span", "chip chip-green", L("اعتمدها الخبير", "Approved by the expert"))
        : el("span", "chip chip-terra", L("بانتظار الخبير", "Waiting for the expert"));
      st.style.alignSelf = "flex-start"; st.style.marginTop = "6px";
      b.appendChild(st);
      b.addEventListener("click", function () { start(p); });
      box.appendChild(b);
    });
  }

  /* ---------- reading ---------- */
  function start(p) {
    stop();
    S.page = p; S.lines = p.lines.slice(); S.issues = p.issues.slice(); S.conf = p.confidence;
    S.fixed = {}; S.round = 0; S.simulated = false;
    drawPicker();
    $("bench").hidden = false; $("final").hidden = true; $("decide").hidden = true; $("noteBox").hidden = true; $("meter").hidden = true;
    $("note").value = "";
    var img = $("scanImg"); $("scan").classList.remove("has-img");
    var base = "../assets/img/scan-" + p.id;
    img.setAttribute("data-alt", base + ".png," + base + ".webp," + base + ".jpeg");
    img.onerror = function () { window.diwanImg && window.diwanImg(img); };
    img.src = base + ".jpg";
    img.alt = L("صورة الصفحة ", "Scan of page ") + p.id;
    drawTitle();
    read(L("القارئ الآلي يقرأ الصفحة سطرًا بسطر…", "The AI reader is reading the page line by line…"));
    $("bench").scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
  }

  function drawTitle() {
    var p = S.page; if (!p) return;
    $("pageTitle").textContent = L("الصفحة ", "Page ") + num(p.id) + " · " + L("ورقة ", "folio ") + num(p.folio);
    $("scanCap").textContent = p.court[lang()] + " · " + p.date[lang()];
  }

  function hlTo(i, n, flag) {
    var hl = $("hl");
    hl.style.top = (6 + (i / Math.max(n, 1)) * 88) + "%";
    hl.style.height = Math.max(2.5, 80 / Math.max(n, 1)) + "%";
    hl.classList.toggle("flag", !!flag);
  }

  function stop() { if (S.timer) { clearTimeout(S.timer); S.timer = null; } S.typing = false; }

  function read(msg) {
    var ol = $("lines"); ol.innerHTML = "";
    var n = S.lines.length;
    var rows = S.lines.map(function (txt, i) { var li = row(i, ""); ol.appendChild(li); return li; });
    status(msg);
    $("skip").hidden = false;
    if (reduce) { finishTyping(rows); return; }
    S.typing = true;
    var i = 0, pos = 0;
    (function tick() {
      if (!S.typing) return;
      if (i >= n) { finishTyping(rows); return; }
      var txt = S.lines[i], t = rows[i].querySelector(".lt");
      if (pos === 0) { rows[i].classList.add("cur"); hlTo(i, n); }
      pos = Math.min(txt.length, pos + 4);
      t.textContent = txt.slice(0, pos);
      var c = el("span", "caret"); t.appendChild(c);
      if (pos >= txt.length) { t.textContent = txt; rows[i].classList.remove("cur"); i++; pos = 0; S.timer = setTimeout(tick, 90); }
      else S.timer = setTimeout(tick, 16);
    })();
    S.finish = function () { finishTyping(rows); };
  }

  function finishTyping(rows) {
    stop();
    rows.forEach(function (li, i) { li.classList.remove("cur"); li.querySelector(".lt").textContent = S.lines[i]; });
    $("skip").hidden = true;
    status(L("المدقق الآلي يقارن النص بالصورة…", "The AI checker is comparing the text with the scan…"));
    S.timer = setTimeout(check, reduce ? 0 : 700);
  }

  function row(i, txt) {
    var li = el("li"); li.dataset.i = i;
    var ln = el("button", "ln"); ln.type = "button"; ln.textContent = num(i + 1);
    ln.setAttribute("aria-label", L("صحّح السطر ", "Edit line ") + (i + 1));
    ln.style.cssText = "background:none;border:none;cursor:pointer;font:inherit;color:inherit;min-height:44px";
    ln.addEventListener("click", function () { edit(i); });
    var lt = el("div", "lt", txt); lt.setAttribute("lang", "ar"); lt.dir = "rtl";
    li.appendChild(ln); li.appendChild(lt);
    return li;
  }

  /* ---------- checking ---------- */
  function check() {
    var n = S.lines.length, rows = $("lines").children;
    $("meter").hidden = false;
    if (S.conf == null) { $("meterBar").style.width = "0"; $("meterVal").textContent = "—"; }
    else { $("meterBar").style.width = Math.round(S.conf * 100) + "%"; $("meterVal").textContent = pct(S.conf); }
    var first = null;
    S.issues.forEach(function (is) {
      var i = is.line - 1, li = rows[i]; if (!li || S.fixed[i]) return;
      li.classList.add("flag"); if (first == null) first = i;
      var note = el("div", "note");
      note.appendChild(el("span", "", L("ملاحظة المدقق: ", "Checker’s note (Arabic): ")));
      var pr = el("span", "", is.problem); pr.lang = "ar"; pr.dir = "rtl"; note.appendChild(pr);
      var r = el("div", "row");
      var acc = el("button", "btn btn-quiet", L("اقبل الاقتراح", "Accept the suggestion")); acc.type = "button";
      acc.addEventListener("click", function () { accept(i, is); });
      var ed = el("button", "btn btn-quiet", L("صحّح", "Edit")); ed.type = "button";
      ed.addEventListener("click", function () { edit(i); });
      r.appendChild(acc); r.appendChild(ed); note.appendChild(r);
      li.appendChild(note);
    });
    if (first != null) hlTo(first, n, true); else hlTo(0, n);
    var k = S.issues.filter(function (is) { return !S.fixed[is.line - 1]; }).length;
    var head = S.simulated ? L("(محاكاة) ", "(simulated) ") : (S.round && S.page.reread ? L("(إعادة مسجّلة من التجربة) ", "(recorded in the pilot) ") : "");
    status(head + (k ? L("علّم المدقق ", "The checker flagged ") + num(k) + L(" أسطر مشكوكًا فيها. أنت الخبير الآن.", " doubtful lines. You are the expert now.")
                     : L("لا أسطر مشكوك فيها. راجع النص ثم قرّر.", "No doubtful lines. Read it through, then decide.")));
    $("decide").hidden = false;
  }

  function wrongWord(problem) {
    var m = /['«“]([^'»”]+)['»”]/.exec(problem);
    return m ? m[1].trim() : null;
  }

  function markFixed(i, how) {
    var li = $("lines").children[i]; if (!li) return;
    S.fixed[i] = true; li.classList.remove("flag"); li.classList.add("fixed");
    var note = li.querySelector(".note"); if (note) li.removeChild(note);
    var n = el("div", "note", how); li.appendChild(n);
  }

  function accept(i, is) {
    var w = wrongWord(is.problem), line = S.lines[i], s = is.suggestion;
    if (s.split(/\s+/).length > 3 || !w || line.indexOf(w) < 0) S.lines[i] = s;
    else S.lines[i] = line.split(w).join(s);
    $("lines").children[i].querySelector(".lt").textContent = S.lines[i];
    markFixed(i, L("قُبل اقتراح المدقق.", "Checker’s suggestion accepted."));
  }

  function edit(i) {
    var li = $("lines").children[i]; if (!li) return;
    var lt = li.querySelector(".lt");
    if (lt.isContentEditable) { save(); return; }
    lt.contentEditable = "true"; lt.focus();
    var range = document.createRange(); range.selectNodeContents(lt); range.collapse(false);
    var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);
    status(L("اكتب التصحيح ثم اضغط Enter أو انقر خارج السطر.", "Type the correction, then press Enter or click outside the line."));
    function save() {
      lt.contentEditable = "false"; lt.removeEventListener("blur", save); lt.removeEventListener("keydown", key);
      var v = lt.textContent.replace(/\s+/g, " ").trim();
      if (v && v !== S.lines[i]) { S.lines[i] = v; markFixed(i, L("صحّحتَ هذا السطر.", "You corrected this line.")); }
      lt.textContent = S.lines[i]; status("");
    }
    function key(e) { if (e.key === "Enter") { e.preventDefault(); lt.blur(); } if (e.key === "Escape") { lt.textContent = S.lines[i]; lt.blur(); } }
    lt.addEventListener("blur", save); lt.addEventListener("keydown", key);
  }

  /* ---------- decisions ---------- */
  function sendBack() {
    var note = $("note").value.trim();
    if (!note) { status(L("اكتب ملاحظة قصيرة للقارئ الآلي أولًا.", "Write a short note for the AI reader first.")); $("note").focus(); return; }
    $("decide").hidden = true; $("noteBox").hidden = true;
    S.round++;
    var p = S.page;
    if (p.reread && S.round === 1) {
      S.lines = p.reread.lines.slice(); S.issues = p.reread.issues.slice(); S.conf = p.reread.confidence; S.fixed = {};
      read(L("القارئ الآلي يعيد قراءة الصفحة بملاحظتك… (هذه القراءة الثانية مسجّلة من التجربة الأولية)",
             "The AI reader is reading the page again with your note… (this second reading was recorded in the pilot)"));
    } else {
      S.simulated = true;
      S.issues.forEach(function (is) {
        var i = is.line - 1; if (S.fixed[i]) return;
        var w = wrongWord(is.problem), line = S.lines[i] || "", s = is.suggestion;
        S.lines[i] = (s.split(/\s+/).length > 3 || !w || line.indexOf(w) < 0) ? s : line.split(w).join(s);
      });
      S.issues = []; S.conf = null; S.fixed = {};
      read(L("القارئ الآلي يعيد القراءة بملاحظتك… (محاكاة: تُطبَّق اقتراحات المدقق، ولا توجد درجة ثقة مسجّلة)",
             "The AI reader is reading again with your note… (simulated: the checker’s suggestions are applied; no recorded confidence)"));
    }
  }

  function approve() {
    $("decide").hidden = true;
    var f = $("final"), ol = $("finalLines"); ol.innerHTML = "";
    S.lines.forEach(function (t) { var li = el("li", "", t); ol.appendChild(li); });
    f.hidden = false; f.focus();
    var items = ol.children, k = 0, total = items.length;
    var msg = L("هذا السطر صار بيانات تدريب", "this line is now training data");
    function show() {
      $("counter").textContent = num(k) + " / " + num(total) + " · " + msg;
    }
    $("finalMsg").textContent = L("اعتمدتَ الصفحة. كل سطر معتمد يصير مع صورته زوجًا موثقًا يتعلم منه القارئ الآلي في الصفحات التالية.",
                                   "You approved the page. Each approved line, paired with its scan, becomes a verified example the AI reader learns from on the next pages.");
    if (reduce) { k = total; for (var j = 0; j < total; j++) items[j].className = "trained"; show(); }
    else (function step() { if (k >= total) return; items[k].className = "trained"; k++; show(); S.timer = setTimeout(step, 140); })();
    show();
    var e = S.page.expert, cmp = $("compare");
    if (e.lines && e.lines.length) {
      var eo = $("expertLines"); eo.innerHTML = "";
      e.lines.forEach(function (t) { eo.appendChild(el("li", "", t)); });
      cmp.hidden = false;
    } else cmp.hidden = true;
    status("");
  }

  /* ---------- live mode (optional, needs a connection and the access code) ---------- */
  function live() {
    var code = $("liveCode").value.trim(), out = $("liveOut");
    if (!code) { out.textContent = L("اكتب رمز الدخول.", "Type the access code."); return; }
    out.textContent = L("جارٍ الاتصال بـ n8n…", "Contacting n8n…");
    fetch(DOOR, { method: "GET", headers: { "X-Diwan-Code": code, "Accept": "application/json" } })
      .then(function (r) {
        if (r.status === 401 || r.status === 403) throw L("رمز الدخول غير صحيح.", "The access code is wrong.");
        if (!r.ok) throw L("أجاب n8n بخطأ ", "n8n answered with error ") + r.status + ".";
        return r.json();
      })
      .then(function (j) {
        var pages = (j && j.pages) || [];
        if (!pages.length) { out.textContent = L("لا صفحات الآن في سير العمل.", "No pages in the workflow right now."); return; }
        var tb = el("table"), h = el("tr");
        [L("الصفحة", "Page"), L("المرحلة", "Stage"), L("الثقة", "Confidence")].forEach(function (x) { h.appendChild(el("th", "", x)); });
        tb.appendChild(h);
        var names = { reading: L("قيد القراءة", "Being read"), expert: L("عند الخبير", "With the expert"), approved: L("معتمدة", "Approved"), rejected: L("مرفوضة", "Rejected"), no_answer: L("بلا جواب", "No answer") };
        pages.slice(0, 30).forEach(function (p) {
          var r = el("tr");
          r.appendChild(el("td", "", p.page));
          r.appendChild(el("td", "", names[p.stage] || p.stage || ""));
          r.appendChild(el("td", "", p.confidence ? pct(p.confidence) : "—"));
          tb.appendChild(r);
        });
        out.innerHTML = ""; out.appendChild(tb);
      })
      .catch(function (e) { out.textContent = typeof e === "string" ? e : L("تعذّر الاتصال. الوضع المسجّل يعمل دون اتصال.", "Could not connect. The recorded mode works offline."); });
  }

  /* ---------- wiring ---------- */
  function init() {
    if (!$("pick")) return;
    drawPicker();
    $("skip").addEventListener("click", function () { if (S.typing && S.finish) S.finish(); });
    $("approve").addEventListener("click", approve);
    $("sendback").addEventListener("click", function () { $("noteBox").hidden = false; $("note").focus(); });
    $("sendNote").addEventListener("click", sendBack);
    $("again").addEventListener("click", function () { stop(); $("bench").hidden = true; S.page = null; drawPicker(); $("pick").querySelector("button").focus(); });
    $("liveOn").addEventListener("change", function () { $("liveBox").hidden = !this.checked; });
    $("liveGo").addEventListener("click", live);
    $("liveCode").addEventListener("keydown", function (e) { if (e.key === "Enter") live(); });
    document.addEventListener("diwan:lang", function () { drawPicker(); drawTitle(); });
    var m = /[?&]page=(\d{4})/.exec(location.search);
    if (m) PAGES.forEach(function (p) { if (p.id === m[1]) start(p); });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
