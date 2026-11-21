/* Dīwān al-Wathāʾiq: workspace board.
   Reads the n8n door "Diwan door: board" and draws one card per page.
   The access code is kept in this browser only and sent in the header X-Diwan-Code. */
(function () {
  'use strict';

  var DOOR = 'https://hsm38.app.n8n.cloud/webhook/diwan-board';
  var KEY = 'diwan-board-code';
  var STUCK_MINUTES = 60;
  var APPROVED_SHOWN = 6;

  var code = readCode();
  var data = null;
  var busy = false;

  var el = {
    pill: byId('pill'), subtitle: byId('subtitle'), tools: byId('tools'), find: byId('find'),
    refresh: byId('refresh'), notice: byId('notice'), gate: byId('gate'), form: byId('gate-form'),
    code: byId('code'), remember: byId('remember'), gateError: byId('gate-error'), gateGo: byId('gate-go'),
    board: byId('board'), today: byId('today'), todayList: byId('today-list'), lock: byId('lock')
  };

  var COLUMNS = [
    { id: 'inbox', name: 'Inbox', sub: 'Waiting in the Drive folder', dot: '#5f6577', empty: 'No scan is waiting.' },
    { id: 'reading', name: 'Being read', sub: 'The AI reader and the AI checker', dot: '#22508f', empty: 'Nothing is being read.' },
    { id: 'expert', name: 'With the expert', sub: 'Review form sent by email', dot: '#c08a14', empty: 'No page is waiting for the expert.' },
    { id: 'approved', name: 'Approved', sub: 'Text saved to Results', dot: '#16684e', empty: 'No approved page yet.' },
    { id: 'attention', name: 'Needs attention', sub: 'Rejected, or no answer', dot: '#962d28', empty: 'Nothing needs attention.' }
  ];

  var ICON = {
    plain: '<svg aria-hidden="true" width="30" height="38" viewBox="0 0 30 38"><path d="M3 1.5h17l7 7v28H3z" fill="#f6f1e6" stroke="#cdbf9f"/><path d="M20 1.5v7h7" fill="none" stroke="#cdbf9f"/><path d="M8 15h14M8 19.5h14M8 24h14M8 28.5h9" stroke="#b9ab89" stroke-width="1.4" stroke-linecap="round"/></svg>',
    approved: '<svg aria-hidden="true" width="30" height="38" viewBox="0 0 30 38"><path d="M3 1.5h17l7 7v28H3z" fill="#dcebe2" stroke="#8fbfa6"/><path d="M20 1.5v7h7" fill="none" stroke="#8fbfa6"/><path d="M9 21l4 4 8-9" fill="none" stroke="#16684e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    rejected: '<svg aria-hidden="true" width="30" height="38" viewBox="0 0 30 38"><path d="M3 1.5h17l7 7v28H3z" fill="#f6dedb" stroke="#d9a39d"/><path d="M20 1.5v7h7" fill="none" stroke="#d9a39d"/><path d="M10.5 17.5l9 9M19.5 17.5l-9 9" stroke="#962d28" stroke-width="2" stroke-linecap="round"/></svg>',
    waiting: '<svg aria-hidden="true" width="30" height="38" viewBox="0 0 30 38"><path d="M3 1.5h17l7 7v28H3z" fill="#f6dedb" stroke="#d9a39d"/><path d="M20 1.5v7h7" fill="none" stroke="#d9a39d"/><circle cx="15" cy="22" r="6" fill="none" stroke="#962d28" stroke-width="1.8"/><path d="M15 18.8V22l2.2 1.6" fill="none" stroke="#962d28" stroke-width="1.8" stroke-linecap="round"/></svg>'
  };

  /* ---------- small helpers ---------- */
  function byId(id) { return document.getElementById(id); }
  function make(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined && text !== null) n.textContent = String(text);
    return n;
  }
  function storage(kind) {
    try { return kind === 'local' ? window.localStorage : window.sessionStorage; } catch (e) { return null; }
  }
  function readCode() {
    var kinds = ['session', 'local'];
    for (var i = 0; i < kinds.length; i++) {
      var s = storage(kinds[i]);
      try { var v = s && s.getItem(KEY); if (v) return v; } catch (e) { /* storage blocked */ }
    }
    return '';
  }
  function saveCode(value, remember) {
    var s = storage(remember ? 'local' : 'session');
    try { if (s) s.setItem(KEY, value); } catch (e) { /* the code then lives only in memory */ }
  }
  function forgetCode() {
    ['session', 'local'].forEach(function (k) {
      var s = storage(k);
      try { if (s) s.removeItem(KEY); } catch (e) { /* nothing to do */ }
    });
    code = '';
  }
  function arabic(text) { return /[؀-ۿ]/.test(text); }

  /* ---------- dates ---------- */
  function toDate(iso) { var d = new Date(iso); return isNaN(d.getTime()) ? null : d; }
  function two(n) { return (n < 10 ? '0' : '') + n; }
  function clock(d) { return two(d.getHours()) + ':' + two(d.getMinutes()); }
  function sameDay(a, b) { return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate(); }
  function when(d) {
    if (!d) return '';
    var now = new Date();
    var y = new Date(now); y.setDate(now.getDate() - 1);
    if (sameDay(d, now)) return 'today, ' + clock(d);
    if (sameDay(d, y)) return 'yesterday, ' + clock(d);
    return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }) + ', ' + clock(d);
  }
  function minutesSince(d) { return d ? Math.max(0, Math.round((Date.now() - d.getTime()) / 60000)) : 0; }
  function ago(d) {
    var m = minutesSince(d);
    if (m < 1) return 'just now';
    if (m < 60) return m + ' min';
    var h = Math.round(m / 60);
    if (h < 24) return h + ' h';
    var days = Math.round(h / 24);
    return days + (days === 1 ? ' day' : ' days');
  }

  /* ---------- pages ---------- */
  function shortName(stem) {
    var m = /(\d+)$/.exec(stem || '');
    return m ? 'Page ' + m[1] : (stem || 'Page');
  }
  function shortNumber(stem) {
    var m = /(\d+)$/.exec(stem || '');
    return m ? m[1] : stem;
  }
  function columnOf(p) {
    if (p.stage === 'reading') return 'reading';
    if (p.stage === 'expert') return 'expert';
    if (p.stage === 'approved') return 'approved';
    return 'attention';
  }
  function matches(stem) {
    var q = (el.find.value || '').trim().toLowerCase();
    return !q || String(stem).toLowerCase().indexOf(q) !== -1;
  }

  /* ---------- cards ---------- */
  function cardShell(stem, icon, extraClass) {
    var li = make('li', 'card' + (extraClass ? ' ' + extraClass : ''));
    var top = make('div', 'card-top');
    var holder = document.createElement('span');
    holder.innerHTML = ICON[icon];
    top.appendChild(holder.firstChild);
    var names = make('span', 'card-names');
    names.appendChild(make('span', 'card-title', shortName(stem)));
    var s = make('span', 'card-stem', stem);
    s.title = stem;
    names.appendChild(s);
    top.appendChild(names);
    li.appendChild(top);
    return li;
  }
  function line(text, cls) { return make('span', 'card-line' + (cls ? ' ' + cls : ''), text); }
  function note(text) {
    var n = make('span', 'card-note', text);
    if (arabic(text)) { n.lang = 'ar'; n.dir = 'rtl'; }
    return n;
  }
  function scanLink(url) {
    if (!/^https:\/\/(drive|docs)\.google\.com\//.test(url || '')) return null;
    var a = make('a', 'card-link', 'Open the scan ↗');
    a.href = url; a.target = '_blank'; a.rel = 'noopener noreferrer';
    return a;
  }
  function meter(kind, percent) {
    var m = make('span', 'meter is-' + kind);
    m.setAttribute('aria-hidden', 'true');
    var fill = document.createElement('span');
    if (percent !== undefined) fill.style.width = Math.max(4, Math.min(100, percent)) + '%';
    m.appendChild(fill);
    return m;
  }

  function inboxCard(f) {
    var li = cardShell(f.page, 'plain');
    var d = toDate(f.added);
    li.appendChild(line(d ? 'Added ' + when(d) : 'Waiting in the Inbox'));
    var a = scanLink(f.link); if (a) li.appendChild(a);
    return li;
  }

  function readingCard(p) {
    var d = toDate(p.updated);
    var stuck = minutesSince(d) >= STUCK_MINUTES;
    var li = cardShell(p.page, 'plain', stuck ? 'is-stuck' : 'is-reading');
    li.appendChild(meter('blue'));
    var sentBack = /^Sent back by the expert/.test(p.problem);
    li.appendChild(line(sentBack ? 'Read again after the expert’s note' : 'The AI reader is reading, then the AI checker compares', 'is-blue'));
    if (sentBack) {
      var n = p.problem.replace(/^Sent back by the expert:?\s*/, '');
      if (n) li.appendChild(note(n));
    }
    if (stuck) {
      li.appendChild(line('No change for ' + ago(d) + '. The run may have stopped: check the executions in n8n.', 'is-red'));
    } else if (d) {
      li.appendChild(line('Started ' + clock(d) + ' · ' + ago(d) + ' ago'));
    }
    var a = scanLink(p.scanLink); if (a) li.appendChild(a);
    return li;
  }

  function expertCard(p) {
    var pct = Math.round((p.confidence || 0) * 100);
    var kind = pct >= 85 ? 'green' : pct >= 50 ? 'brass' : 'red';
    var li = cardShell(p.page, 'plain', kind === 'green' ? 'is-expert' : 'is-low');
    li.appendChild(meter(kind, pct));
    var row = make('span', 'card-line');
    row.appendChild(make('span', 'strong', pct + '% sure'));
    if (p.flagged > 0) row.appendChild(make('span', 'flagged', p.flagged + (p.flagged === 1 ? ' line flagged' : ' lines flagged')));
    else row.appendChild(make('span', '', 'no flags'));
    li.appendChild(row);
    if (p.problem) li.appendChild(note(p.problem));
    var d = toDate(p.updated);
    var tail = d ? 'Waiting ' + ago(d) : 'Waiting';
    if (p.attempts > 1) tail += ' · ' + p.attempts + ' readings';
    li.appendChild(line(tail));
    var a = scanLink(p.scanLink); if (a) li.appendChild(a);
    return li;
  }

  function approvedCard(p) {
    var li = cardShell(p.page, 'approved');
    var d = toDate(p.updated);
    li.appendChild(line('Approved ' + (d ? when(d) : '') + (p.reviewer ? ' · ' + p.reviewer : '')));
    return li;
  }

  function attentionCard(p) {
    var d = toDate(p.updated);
    var li;
    if (p.stage === 'no_answer') {
      li = cardShell(p.page, 'waiting', 'is-attention');
      li.appendChild(line('No answer after 7 days', 'is-red'));
      li.appendChild(line('The scan stays in In review. Move it back to the Inbox to send it again.'));
    } else if (p.stage === 'rejected') {
      li = cardShell(p.page, 'rejected', 'is-attention');
      li.appendChild(line('Rejected ' + (d ? when(d) : '') + (p.reviewer ? ' by ' + p.reviewer : ''), 'is-red'));
      if (p.problem && p.problem !== 'Rejected by the expert') li.appendChild(note(p.problem));
      li.appendChild(line('The scan stays in In review. Move it back to the Inbox to read it again.'));
    } else {
      li = cardShell(p.page, 'rejected', 'is-attention');
      li.appendChild(line('Unknown stage: ' + (p.stage || 'empty'), 'is-red'));
    }
    var a = scanLink(p.scanLink); if (a) li.appendChild(a);
    return li;
  }

  /* ---------- drawing ---------- */
  function drawBoard() {
    if (!data) return;
    var groups = { inbox: [], reading: [], expert: [], approved: [], attention: [] };
    (data.inbox || []).forEach(function (f) { if (matches(f.page)) groups.inbox.push(f); });
    (data.pages || []).forEach(function (p) { if (matches(p.page)) groups[columnOf(p)].push(p); });
    groups.inbox.sort(function (a, b) { return String(a.added).localeCompare(String(b.added)); });
    groups.expert.sort(function (a, b) { return String(a.updated).localeCompare(String(b.updated)); });

    el.board.textContent = '';
    COLUMNS.forEach(function (c) {
      var list = groups[c.id];
      var sec = make('section', 'col');
      sec.setAttribute('aria-labelledby', 'col-' + c.id);
      var head = make('div', 'col-head');
      var h = make('h2');
      h.id = 'col-' + c.id;
      var dot = make('span', 'col-dot'); dot.style.background = c.dot; dot.setAttribute('aria-hidden', 'true');
      h.appendChild(dot);
      h.appendChild(make('span', 'name', c.name));
      var count = make('span', 'count', list.length);
      count.setAttribute('aria-label', list.length + (list.length === 1 ? ' page' : ' pages'));
      h.appendChild(count);
      head.appendChild(h);
      head.appendChild(make('p', 'col-sub', c.sub));
      sec.appendChild(head);

      if (!list.length) {
        sec.appendChild(make('p', 'col-empty', el.find.value.trim() ? 'No match here.' : c.empty));
      } else {
        var ul = make('ul');
        var shown = c.id === 'approved' ? list.slice(0, APPROVED_SHOWN) : list;
        shown.forEach(function (item) {
          if (c.id === 'inbox') ul.appendChild(inboxCard(item));
          else if (c.id === 'reading') ul.appendChild(readingCard(item));
          else if (c.id === 'expert') ul.appendChild(expertCard(item));
          else if (c.id === 'approved') ul.appendChild(approvedCard(item));
          else ul.appendChild(attentionCard(item));
        });
        sec.appendChild(ul);
        if (list.length > shown.length) {
          sec.appendChild(make('p', 'col-more', '+ ' + (list.length - shown.length) + ' more approved'));
        }
      }
      el.board.appendChild(sec);
    });
    drawToday();
  }

  function todayText(p) {
    if (p.stage === 'reading') return /^Sent back by the expert/.test(p.problem) ? 'sent back to the AI reader' + (p.reviewer ? ' by ' + p.reviewer : '') : 'sent to the AI reader';
    if (p.stage === 'expert') {
      var t = 'sent to the expert, ' + Math.round((p.confidence || 0) * 100) + '% sure';
      if (p.flagged > 0) t += ', ' + p.flagged + (p.flagged === 1 ? ' line flagged' : ' lines flagged');
      return t;
    }
    if (p.stage === 'approved') return 'approved' + (p.reviewer ? ' by ' + p.reviewer : '') + ' · text saved to Results';
    if (p.stage === 'rejected') return 'rejected' + (p.reviewer ? ' by ' + p.reviewer : '') + (p.problem && p.problem !== 'Rejected by the expert' ? ': ' + p.problem : '');
    if (p.stage === 'no_answer') return 'no answer from the expert after 7 days';
    return 'stage ' + p.stage;
  }

  function drawToday() {
    var now = new Date();
    var rows = [];
    (data.pages || []).forEach(function (p) {
      var d = toDate(p.updated);
      if (d && sameDay(d, now) && matches(p.page)) rows.push({ d: d, page: p.page, text: todayText(p) });
    });
    (data.inbox || []).forEach(function (f) {
      var d = toDate(f.added);
      if (d && sameDay(d, now) && matches(f.page)) rows.push({ d: d, page: f.page, text: 'added to the Inbox' });
    });
    rows.sort(function (a, b) { return b.d - a.d; });

    el.todayList.textContent = '';
    if (!rows.length) {
      el.todayList.appendChild(make('li', 'empty', 'Nothing has moved today yet.'));
      return;
    }
    rows.slice(0, 30).forEach(function (r) {
      var li = make('li');
      li.appendChild(make('span', 't', clock(r.d)));
      var what = make('span', 'what');
      what.appendChild(make('strong', '', shortNumber(r.page)));
      what.appendChild(document.createTextNode(' ' + r.text));
      li.appendChild(what);
      el.todayList.appendChild(li);
    });
  }

  /* ---------- states ---------- */
  function setPill(kind, text) {
    el.pill.className = 'pill pill-' + kind;
    el.pill.textContent = text;
  }
  function showNotice(html, info) {
    el.notice.className = 'notice' + (info ? ' is-info' : '');
    el.notice.textContent = '';
    el.notice.appendChild(html);
    el.notice.hidden = false;
  }
  function hideNotice() { el.notice.hidden = true; el.notice.textContent = ''; }
  function message(strong, rest) {
    var p = make('p');
    p.appendChild(make('strong', '', strong));
    p.appendChild(document.createTextNode(' ' + rest));
    return p;
  }

  function showGate(error) {
    data = null;
    el.board.hidden = true; el.today.hidden = true; el.tools.hidden = true; el.lock.hidden = true;
    el.gate.hidden = false;
    setPill('locked', 'Locked');
    el.subtitle.textContent = 'One card per page. The board opens with the access code.';
    el.gateError.textContent = error || '';
    el.code.setAttribute('aria-invalid', error ? 'true' : 'false');
    el.code.value = '';
    el.code.focus();
  }

  function showBoard() {
    el.gate.hidden = true;
    el.board.hidden = false; el.today.hidden = false; el.tools.hidden = false; el.lock.hidden = false;
  }

  function setBusy(on) {
    busy = on;
    el.refresh.disabled = on;
    el.gateGo.disabled = on;
    el.refresh.querySelector('span').textContent = on ? 'Refreshing…' : 'Refresh';
    el.gateGo.textContent = on ? 'Opening…' : 'Open the board';
    if (on) setPill('busy', 'Loading');
  }

  /* ---------- talking to n8n ---------- */
  function load(fromGate) {
    if (busy || !code) return;
    setBusy(true);
    var ctrl = typeof AbortController === 'function' ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, 30000);

    fetch(DOOR, {
      method: 'GET',
      headers: { 'X-Diwan-Code': code, 'Accept': 'application/json' },
      cache: 'no-store',
      credentials: 'omit',
      referrerPolicy: 'no-referrer',
      signal: ctrl ? ctrl.signal : undefined
    }).then(function (res) {
      if (res.status === 401 || res.status === 403) {
        var wasRemembered = !fromGate;
        forgetCode();
        showGate(wasRemembered ? 'The saved code is no longer accepted. Enter the current code.' : 'That code was not accepted. Check it and try again.');
        hideNotice();
        return null;
      }
      if (res.status === 404) throw { kind: 'off' };
      if (!res.ok) throw { kind: 'server', status: res.status };
      return res.json().catch(function () { throw { kind: 'shape' }; });
    }).then(function (json) {
      if (!json) return;
      if (!json.ok || !Array.isArray(json.pages)) throw { kind: 'shape' };
      if (fromGate) saveCode(code, el.remember.checked);
      data = json;
      hideNotice();
      showBoard();
      drawBoard();
      var d = toDate(json.updated) || new Date();
      var total = json.pages.length + (json.inbox || []).length;
      setPill('live', 'Live data');
      el.subtitle.textContent = total + (total === 1 ? ' page' : ' pages') + ' · updated ' + clock(d) + '. Click Refresh to see new changes.';
    }).catch(function (err) {
      var kind = err && err.kind;
      var node;
      if (kind === 'off') node = message('The board door is switched off.', 'In n8n, open the workflow “Diwan door: board” and click Publish.');
      else if (kind === 'server') node = message('n8n answered with an error (' + err.status + ').', 'Open the executions of “Diwan door: board” in n8n to see which step failed.');
      else if (kind === 'shape') node = message('n8n sent an answer the board cannot read.', 'Check that “Send board data” is the last step of the door workflow.');
      else if (err && err.name === 'AbortError') node = message('n8n took too long to answer.', 'Try Refresh again in a minute.');
      else node = message('n8n could not be reached.', 'Check the internet connection, and that the workflow “Diwan door: board” is published.');
      showNotice(node);
      if (!fromGate && !data) {
        /* saved code, but n8n did not answer: keep the code and offer Refresh */
        el.tools.hidden = false;
        el.lock.hidden = false;
      }
      return 'error';
    }).then(function (outcome) {
      clearTimeout(timer);
      setBusy(false);
      if (outcome === 'error') setPill('error', 'Not updated');
      else if (!data) setPill('locked', 'Locked');
    });
  }

  /* ---------- events ---------- */
  el.form.addEventListener('submit', function (e) {
    e.preventDefault();
    var v = el.code.value.trim();
    if (!v) {
      el.gateError.textContent = 'Type the access code first.';
      el.code.setAttribute('aria-invalid', 'true');
      el.code.focus();
      return;
    }
    code = v;
    el.gateError.textContent = '';
    load(true);
  });
  el.refresh.addEventListener('click', function () { load(false); });
  el.find.addEventListener('input', drawBoard);
  el.lock.addEventListener('click', function () {
    forgetCode();
    hideNotice();
    showGate('');
  });

  if (code) { el.gate.hidden = true; load(false); }
  else showGate('');
})();
