/**
 * Zero Dark Claims — zdc-cfr-enhance.js
 *
 * Adds "Align with VA rating criteria (38 CFR Part 4)" to the Review & Download
 * screen of every letter builder. Injected like zdc-letter-prefill.js — no React
 * source changes needed.
 *
 * WHAT IT DOES
 *   Sends the draft to the ZDC backend (/api/enhance-letter), which pulls the
 *   CURRENT 38 CFR Part 4 text from eCFR, finds the matching diagnostic codes, and
 *   restates the veteran's own facts in rating-schedule language. Anything the
 *   criteria ask about that the draft doesn't answer comes back as a question —
 *   the tool never fills it in. The veteran previews the result and chooses
 *   whether to use it; the original can be restored with one click.
 *
 * PRIVACY
 *   - Name, VA file / SSN, date of birth, address, phone, and email are replaced
 *     with placeholders IN THE BROWSER before anything is sent, then restored
 *     locally when the result comes back.
 *   - Nothing is stored by the backend. Results live in page memory only.
 *   - The results panel is marked ph-no-capture so analytics never records it.
 *
 * INTEGRATION
 *   <script src="./zdc-cfr-enhance.js" defer></script>   (tool/index.html body)
 */
(function () {
  'use strict';

  var API_BASE = window.ZDC_API_BASE || 'https://zdc-backend.onrender.com';
  var TEXTAREA_SEL = 'textarea[data-testid="textarea-generated-letter"]';
  var PANEL_ID = 'zdc-cfr-panel';
  var TIMEOUT_MS = 120000;

  // ── helpers ────────────────────────────────────────────────────────────
  function track(event, props) {
    try { if (window.posthog && window.posthog.capture) window.posthog.capture(event, props || {}); } catch (_) {}
  }
  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === 'style') n.setAttribute('style', attrs[k]);
      else if (k === 'text') n.textContent = attrs[k];
      else if (k.slice(0, 2) === 'on') n.addEventListener(k.slice(2), attrs[k]);
      else n.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { if (c) n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return n;
  }
  function letterTypeFromUrl() {
    var m = (location.hash + location.pathname).match(/\/build\/([a-z-]+)/);
    return m ? m[1] : null;
  }
  // React-controlled textarea: use the native setter so onChange fires
  function setReactValue(textarea, value) {
    var setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
    setter.call(textarea, value);
    textarea.dispatchEvent(new Event('input', { bubbles: true }));
  }

  // ── PII redaction (browser-side, reversible) ────────────────────────────
  var LABELS = [
    { re: /^(\s*(?:Printed Name|Name & Credentials|Name)\s*:\s*)(.+)$/gim, tag: 'NAME' },
    { re: /^(\s*VA File \/ Last 4 SSN\s*:\s*)(.+)$/gim, tag: 'VA_FILE_NUMBER' },
    { re: /^(\s*Date of Birth\s*:\s*)(.+)$/gim, tag: 'DOB' },
    { re: /^(\s*Address\s*:\s*)(.+)$/gim, tag: 'ADDRESS' },
    { re: /^(\s*Contact\s*:\s*)(.+)$/gim, tag: 'CONTACT' },
  ];
  function escapeRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

  function redact(text) {
    var map = {}; var byValue = {}; var counts = {};
    function token(tag, value) {
      value = value.trim();
      if (!value) return null;
      if (byValue[value]) return byValue[value];
      counts[tag] = (counts[tag] || 0) + 1;
      var t = '[[' + tag + (counts[tag] > 1 ? '_' + counts[tag] : '') + ']]';
      map[t] = value; byValue[value] = t;
      return t;
    }
    var out = text;
    LABELS.forEach(function (l) {
      out = out.replace(l.re, function (all, label, value) {
        var t = token(l.tag, value);
        return t ? label + t : all;
      });
    });
    // Replace every other occurrence of captured names (e.g., in the body)
    Object.keys(map).forEach(function (t) {
      var v = map[t];
      if (/^\[\[NAME/.test(t) && v.length >= 3) {
        out = out.replace(new RegExp(escapeRe(v), 'g'), t);
        // also bare last name / first name tokens of 3+ letters
        v.split(/\s+/).filter(function (p) { return p.length >= 3 && /^[A-Z]/.test(p); }).forEach(function (part) {
          out = out.replace(new RegExp('\\b' + escapeRe(part) + '\\b', 'g'), function (m) { return token('NAME_PART', m); });
        });
      }
    });
    out = out
      .replace(/\b\d{3}-?\d{2}-?\d{4}\b/g, function (m) { return token('SSN', m); })
      .replace(/[\w.+-]+@[\w-]+\.[\w.]+/g, function (m) { return token('EMAIL', m); })
      .replace(/\(?\b\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b/g, function (m) { return token('PHONE', m); });
    return { text: out, map: map };
  }
  function restore(text, map) {
    Object.keys(map).sort(function (a, b) { return b.length - a.length; }).forEach(function (t) {
      text = text.split(t).join(map[t]);
    });
    return text;
  }

  // ── styles (use the tool's CSS variables so light/dark both work) ──────
  var S = {
    panel: 'margin:0;border:1px solid hsl(var(--border));background:hsl(var(--card));color:hsl(var(--card-foreground));border-radius:12px;padding:16px 18px;font-family:inherit;',
    row: 'display:flex;flex-wrap:wrap;gap:12px;align-items:flex-start;justify-content:space-between;',
    title: 'font-weight:600;font-size:14px;margin:0 0 4px;',
    badge: 'display:inline-block;margin-left:8px;padding:1px 8px;border-radius:999px;font-size:11px;font-weight:600;background:hsl(var(--accent));color:hsl(var(--accent-foreground));vertical-align:middle;',
    text: 'font-size:12.5px;line-height:1.5;color:hsl(var(--muted-foreground));margin:0;',
    btn: 'cursor:pointer;border:0;border-radius:8px;padding:8px 14px;font-size:13px;font-weight:600;background:hsl(var(--primary));color:hsl(var(--primary-foreground));white-space:nowrap;',
    btnGhost: 'cursor:pointer;border:1px solid hsl(var(--border));border-radius:8px;padding:7px 13px;font-size:13px;font-weight:500;background:transparent;color:hsl(var(--foreground));white-space:nowrap;',
    h: 'font-size:13px;font-weight:600;margin:16px 0 6px;',
    li: 'font-size:12.5px;line-height:1.5;margin:0 0 6px;',
    pre: 'white-space:pre-wrap;font-family:"JetBrains Mono","Fira Code",monospace;font-size:11.5px;line-height:1.55;max-height:420px;overflow:auto;border:1px solid hsl(var(--border));border-radius:8px;padding:12px;background:hsl(var(--muted) / .35);margin:0;',
    warn: 'border:1px solid #d9a400;background:rgba(217,164,0,.08);border-radius:8px;padding:10px 12px;margin-top:12px;',
    err: 'border:1px solid #c0392b;background:rgba(192,57,43,.08);border-radius:8px;padding:10px 12px;margin-top:12px;font-size:12.5px;',
    small: 'font-size:11.5px;color:hsl(var(--muted-foreground));margin-top:10px;',
  };

  // ── panel ──────────────────────────────────────────────────────────────
  var state = { original: null, result: null, applied: false };

  function intro(panel, textarea) {
    panel.innerHTML = '';
    var btn = el('button', { type: 'button', style: S.btn, 'data-testid': 'button-cfr-align', text: 'Align my draft' });
    btn.addEventListener('click', function () { run(panel, textarea, btn); });
    panel.appendChild(el('div', { style: S.row }, [
      el('div', { style: 'flex:1 1 320px;min-width:0;' }, [
        el('p', { style: S.title }, ['Align with VA rating criteria (38 CFR Part 4)', el('span', { style: S.badge, text: 'Free' })]),
        el('p', { style: S.text, text: 'Restates the facts you already gave in the language of the VA rating schedule, using the current official text from eCFR. It never adds facts. Anything the criteria ask about that your draft doesn\u2019t cover comes back as a question for you to answer.' }),
        el('p', { style: S.small, text: 'Your name, VA file number, date of birth, and contact details are removed in your browser before the draft is sent, and nothing is stored.' }),
      ]),
      btn,
    ]));
  }

  function list(items, render) {
    var ul = el('ul', { style: 'margin:0;padding-left:18px;' });
    items.forEach(function (i) { ul.appendChild(el('li', { style: S.li }, render(i))); });
    return ul;
  }

  function showResult(panel, textarea, r, map) {
    var aligned = restore(r.enhancedLetter, map);
    state.result = aligned;
    panel.innerHTML = '';
    panel.classList.add('ph-no-capture');

    var useBtn = el('button', { type: 'button', style: S.btn, 'data-testid': 'button-cfr-apply', text: 'Use aligned version' });
    var keepBtn = el('button', { type: 'button', style: S.btnGhost, text: 'Keep my original' });
    useBtn.addEventListener('click', function () {
      setReactValue(textarea, aligned); state.applied = true; track('cfr_align_applied', { letter_type: letterTypeFromUrl() });
      useBtn.textContent = 'Applied \u2014 edit below or download';
      useBtn.disabled = true;
      keepBtn.textContent = 'Undo (restore original)';
    });
    keepBtn.addEventListener('click', function () {
      if (state.applied) { setReactValue(textarea, state.original); state.applied = false; track('cfr_align_undone', {}); }
      intro(panel, textarea);
    });

    var conds = (r.conditions || []).map(function (c) {
      return (c.condition || '') + (c.diagnostic_code ? ' \u2014 DC ' + c.diagnostic_code : '') + (c.cfr_section ? ' (38 CFR \u00a7 ' + c.cfr_section + ')' : '');
    }).filter(Boolean);

    panel.appendChild(el('div', { style: S.row }, [
      el('div', { style: 'flex:1 1 320px;min-width:0;' }, [
        el('p', { style: S.title, text: 'Aligned draft ready for your review' }),
        el('p', { style: S.text, text: conds.length ? 'Matched to: ' + conds.join('; ') : 'No specific diagnostic code was confidently matched; general Part 4 principles were applied.' }),
      ]),
      el('div', { style: 'display:flex;gap:8px;flex-wrap:wrap;' }, [keepBtn, useBtn]),
    ]));

    if (r.warnings && r.warnings.length) {
      panel.appendChild(el('div', { style: S.warn }, [
        el('p', { style: S.title + 'font-size:13px;', text: 'Check these before you use it' }),
        list(r.warnings, function (w) { return [w.detail]; }),
      ]));
    }

    if (r.informationGaps && r.informationGaps.length) {
      panel.appendChild(el('p', { style: S.h, text: 'Questions your draft doesn\u2019t answer yet' }));
      panel.appendChild(el('p', { style: S.text + 'margin-bottom:6px;', text: 'If any apply to you, go back, add the answer in your own words, and align again. Leave out anything that isn\u2019t true for you.' }));
      panel.appendChild(list(r.informationGaps, function (g) {
        return [el('strong', { text: g.question }), g.why_it_matters ? ' \u2014 ' + g.why_it_matters : '', g.citation ? ' (' + g.citation + ')' : ''];
      }));
    }

    panel.appendChild(el('p', { style: S.h, text: 'Aligned draft (preview)' }));
    panel.appendChild(el('pre', { style: S.pre, class: 'ph-no-capture' }, [aligned]));

    var aligns = (r.criteriaAlignment || []).filter(function (a) { return a.traceable !== false; });
    if (aligns.length) {
      var det = el('details', { style: 'margin-top:12px;' }, [
        el('summary', { style: 'cursor:pointer;font-size:13px;font-weight:600;', text: 'How your words map to the rating criteria (' + aligns.length + ')' }),
        list(aligns, function (a) {
          return ['\u201c' + (a.draft_fact || '') + '\u201d \u2192 ', el('em', { text: a.rating_language || '' }), a.citation ? ' (' + a.citation + ')' : ''];
        }),
      ]);
      panel.appendChild(det);
    }

    var reg = r.regulation || {};
    var link = el('a', { href: reg.url || 'https://www.ecfr.gov/current/title-38/chapter-I/part-4', target: '_blank', rel: 'noopener', style: 'color:inherit;text-decoration:underline;', text: '38 CFR Part 4 on eCFR' });
    panel.appendChild(el('p', { style: S.small }, [
      'Source: ', link, reg.upToDateAsOf ? ', current as of ' + reg.upToDateAsOf + '. ' : '. ',
      'This is drafting software, not legal or medical advice, and it does not predict a rating. Review every sentence for accuracy before you sign.',
    ]));
  }

  function run(panel, textarea, btn) {
    var letterType = letterTypeFromUrl();
    var draft = textarea.value || '';
    if (!letterType || draft.trim().length < 150) {
      panel.appendChild(el('div', { style: S.err, text: 'Add more detail to your draft first \u2014 there isn\u2019t enough text to align yet.' }));
      return;
    }
    state.original = draft;
    var red = redact(draft);
    btn.disabled = true;
    btn.textContent = 'Reading 38 CFR Part 4\u2026';
    var slow = setTimeout(function () { btn.textContent = 'Still working \u2014 this can take up to a minute\u2026'; }, 12000);
    track('cfr_align_requested', { letter_type: letterType });

    var ctrl = window.AbortController ? new AbortController() : null;
    var kill = setTimeout(function () { if (ctrl) ctrl.abort(); }, TIMEOUT_MS);

    fetch(API_BASE + '/api/enhance-letter', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ letterType: letterType, letterText: red.text }),
      signal: ctrl ? ctrl.signal : undefined,
    })
      .then(function (res) { return res.json().then(function (j) { if (!res.ok) throw new Error(j.error || ('HTTP ' + res.status)); return j; }); })
      .then(function (j) { track('cfr_align_succeeded', { letter_type: letterType, gaps: (j.informationGaps || []).length, warnings: (j.warnings || []).length }); showResult(panel, textarea, j, red.map); })
      .catch(function (e) {
        track('cfr_align_failed', { letter_type: letterType });
        intro(panel, textarea);
        panel.appendChild(el('div', { style: S.err, text: (e && e.name === 'AbortError' ? 'The request timed out.' : (e && e.message) || 'Something went wrong.') + ' Your original draft is unchanged.' }));
      })
      .finally(function () { clearTimeout(slow); clearTimeout(kill); });
  }

  // ── mount on the Review & Download screen ──────────────────────────────
  function mount() {
    var textarea = document.querySelector(TEXTAREA_SEL);
    var existing = document.getElementById(PANEL_ID);
    if (!textarea) { if (existing) existing.remove(); return; }
    if (existing && existing.isConnected) return;
    // Insert above the editable draft card
    var card = textarea.closest('.rounded-xl') || textarea.parentElement;
    if (!card || !card.parentElement) return;
    var panel = el('section', { id: PANEL_ID, style: S.panel, 'aria-label': 'Align with VA rating criteria' });
    card.parentElement.insertBefore(panel, card);
    state = { original: null, result: null, applied: false };
    intro(panel, textarea);
  }

  var scheduled = false;
  new MutationObserver(function () {
    if (scheduled) return; scheduled = true;
    requestAnimationFrame(function () { scheduled = false; mount(); });
  }).observe(document.documentElement, { childList: true, subtree: true });
  window.addEventListener('hashchange', mount);
  if (document.readyState !== 'loading') mount(); else document.addEventListener('DOMContentLoaded', mount);

  // Exposed for testing only
  window.__zdcCfr = { redact: redact, restore: restore };
})();
