/* /pitch controls: arrows, PageUp/PageDown, Space, click, swipe; N notes; F full screen; #3 deep links.
   The demo opens in place in an overlay and works offline. */
(function () {
  "use strict";
  var slides = [].slice.call(document.querySelectorAll(".slide"));
  var n = slides.length, cur = 0, notes = false;
  var $ = function (id) { return document.getElementById(id); };
  var ov = $("demoOverlay");

  function rtl() { return document.documentElement.dir === "rtl"; }
  function go(i) {
    cur = Math.max(0, Math.min(n - 1, i));
    slides.forEach(function (s, k) {
      var on = k === cur;
      s.classList.toggle("on", on);
      s.setAttribute("aria-hidden", on ? "false" : "true");
      s.querySelector(".notes").hidden = !(on && notes);
      [].forEach.call(s.querySelectorAll("a,button"), function (b) { b.tabIndex = on ? 0 : -1; });
    });
    $("count").textContent = (cur + 1) + " / " + n;
    if (history.replaceState) history.replaceState(null, "", "#" + (cur + 1));
  }
  function next() { go(cur + 1); }
  function prev() { go(cur - 1); }
  function toggleNotes() { notes = !notes; $("notesBtn").setAttribute("aria-pressed", String(notes)); go(cur); }
  function fullscreen() {
    var d = document;
    if (d.fullscreenElement) { d.exitFullscreen && d.exitFullscreen(); return; }
    var el = d.documentElement;
    (el.requestFullscreen || el.webkitRequestFullscreen || function () {}).call(el);
  }
  function openDemo() {
    var f = ov.querySelector("iframe");
    if (!f.src) f.src = f.getAttribute("data-src");
    if (ov.showModal) ov.showModal(); else ov.setAttribute("open", "");
  }

  document.addEventListener("keydown", function (e) {
    if (ov.open) return;                       // the dialog handles Esc itself
    var tag = (e.target.tagName || "").toLowerCase();
    if (tag === "input" || tag === "textarea") return;
    var k = e.key;
    var fwd = rtl() ? "ArrowLeft" : "ArrowRight", back = rtl() ? "ArrowRight" : "ArrowLeft";
    if (k === fwd || k === "PageDown" || (k === " " && tag !== "button") || k === "ArrowDown") { e.preventDefault(); next(); }
    else if (k === back || k === "PageUp" || k === "ArrowUp") { e.preventDefault(); prev(); }
    else if (k === "Home") go(0);
    else if (k === "End") go(n - 1);
    else if (k === "n" || k === "N") toggleNotes();
    else if (k === "f" || k === "F") fullscreen();
  });

  document.addEventListener("click", function (e) {
    if (e.target.closest("[data-open-demo]")) { openDemo(); return; }
    if (e.target.closest("[data-close-demo]")) { ov.close(); return; }
    if (ov.open) return;
    if (e.target.closest("button,a,.deck-bar,.notes,dialog")) return;
    var x = e.clientX / window.innerWidth;
    // click the leading third to go back, anywhere else to go on
    var leading = rtl() ? x > 0.67 : x < 0.33;
    if (leading) prev(); else next();
  });

  var sx = null, sy = null;
  document.addEventListener("touchstart", function (e) { if (e.touches.length === 1) { sx = e.touches[0].clientX; sy = e.touches[0].clientY; } }, { passive: true });
  document.addEventListener("touchend", function (e) {
    if (sx == null || ov.open) return;
    var dx = e.changedTouches[0].clientX - sx, dy = e.changedTouches[0].clientY - sy; sx = null;
    if (Math.abs(dx) < 50 || Math.abs(dx) < Math.abs(dy)) return;
    var forward = rtl() ? dx > 0 : dx < 0;      // swipe in reading direction
    if (forward) next(); else prev();
  }, { passive: true });

  window.addEventListener("message", function (e) { if (e.data === "diwan:close-demo" && ov.open) { ov.close(); $("deck").focus(); } });
  $("next").addEventListener("click", next);
  $("prev").addEventListener("click", prev);
  $("notesBtn").addEventListener("click", toggleNotes);
  $("fsBtn").addEventListener("click", fullscreen);
  document.addEventListener("diwan:lang", function () {
    $("prev").textContent = rtl() ? "›" : "‹"; $("next").textContent = rtl() ? "‹" : "›";
  });
  $("prev").textContent = rtl() ? "›" : "‹"; $("next").textContent = rtl() ? "‹" : "›";

  function fromHash() { var h = parseInt((location.hash || "").slice(1), 10); go(h >= 1 && h <= n ? h - 1 : cur); }
  window.addEventListener("hashchange", fromHash);
  fromHash();
  $("deck").focus();
})();
