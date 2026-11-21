/* Dīwān al-Wathāʾiq · shared page script: the Arabic / English switch and offline support.
   Both languages ship in every page; this only chooses which one shows. No network calls. */
(function () {
  "use strict";
  var KEY = "diwan-lang";
  var root = document.documentElement;

  function read() {
    var q = /[?&]lang=(ar|en)\b/.exec(location.search);
    if (q) return q[1];
    try { return localStorage.getItem(KEY) || "ar"; } catch (e) { return "ar"; }
  }

  function apply(lang) {
    root.lang = lang;
    root.dir = lang === "ar" ? "rtl" : "ltr";
    root.setAttribute("data-ui", lang);
    var t = root.getAttribute("data-title-" + lang);
    if (t) document.title = t;
    var btns = document.querySelectorAll("[data-lang-switch]");
    for (var i = 0; i < btns.length; i++) {
      btns[i].textContent = lang === "ar" ? "English" : "عربي";
      btns[i].setAttribute("lang", lang === "ar" ? "en" : "ar");
      btns[i].setAttribute("aria-label", lang === "ar" ? "Switch to English" : "التبديل إلى العربية");
    }
    try { localStorage.setItem(KEY, lang); } catch (e) { /* storage may be unavailable */ }
    document.dispatchEvent(new CustomEvent("diwan:lang", { detail: lang }));
  }

  if (/[?&]embed=1\b/.test(location.search)) {
    root.classList.add("embed");
    // inside the pitch overlay, Esc closes the overlay even when focus is in this frame
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && window.parent !== window) window.parent.postMessage("diwan:close-demo", "*"); });
  }

  window.diwanLang = function () { return root.getAttribute("data-ui") || "ar"; };
  apply(read());

  document.addEventListener("click", function (ev) {
    var b = ev.target.closest && ev.target.closest("[data-lang-switch]");
    if (b) apply(window.diwanLang() === "ar" ? "en" : "ar");
  });

  // Keep the site working without a network once it has been opened (https only).
  if ("serviceWorker" in navigator && location.protocol === "https:") {
    var sw = root.getAttribute("data-root") + "sw.js";
    window.addEventListener("load", function () { navigator.serviceWorker.register(sw).catch(function () {}); });
  }
})();
