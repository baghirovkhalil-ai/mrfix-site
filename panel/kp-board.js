/* Mr.Fix panel · Kontent plan: rəhbərlik üçün yan-yana cədvəl
   - "İstehsal planı" kartları çıxarılır
   - Həftələr sətirdə, iş günləri (B.e – Cümə) sütunda yan-yana göstərilir
   - Sətrə/karta toxunanda mövcud detallı pəncərə açılır */
(function () {
  if (typeof kpSimpleV !== 'function') return;

  /* Rəhbərin 12–13 noyabr qeydlərindən sonra zavod çəkilişinin təsviri (16.11.2026) */
  try {
    var z = KP_SHOOTS.find(function (x) { return x.id === 'zavod'; });
    if (z) z.need = 'Tarix: 18 noyabr (çərşənbə), Sumqayıt zavodu. Bir gündə 5 video çəkilir: ' +
      'suvaq sistemi (PRATIX HP 30 + PRATIX RM 75 setka + THERMOMAX dekorativ suvaq) → 24 noyabr; ' +
      'usta sualları, quruma müddətləri ilə (IZOMAX Aqualastic, CERAMAX FLEX, FUGAMAX COLORFUL tətbiqi, Engin bəy kameraya danışır) → 26 noyabr; ' +
      'yapışdırıcı test nümunələri, laboratoriya → 30 noyabr; dərz demosu → 2 dekabr; çat demosu (TAMCRETE) → 10 dekabr. ' +
      'Əlavə: IZOMAX Aqualastic tətbiq kadrları və yekun video üçün ümumi kadrlar. ' +
      'Rekvizit: beton–qazbeton birləşməli divar nümunəsi, PRATIX HP 30, PRATIX RM 75, THERMOMAX dekorativ suvaq, IZOMAX Aqualastic, CERAMAX FLEX, kafel nümunəsi, FUGAMAX COLORFUL, çatlı səth, TAMCRETE, laboratoriya test nümunələri. ' +
      'Quruma gözlənilmir: hər mərhələ üçün əvvəlcədən hazırlanmış nümunələr istifadə olunur. İlk video 24 noyabr (çərşənbə axşamı) çıxır.';
    if (KP_DEC && KP_DEC[0] && /Zavod/.test(KP_DEC[0][0])) KP_DEC[0][3] = 'Əsas fokus zavoddur. Bir gündə 5 video çəkilir, ilk video 24 noyabr (çərşənbə axşamı) çıxır. Tarix dəyişsə videolar da sürüşür.';
  } catch (e) {}

  var orig = kpSimpleV;
  var MODE_KEY = 'kpBoardMode';
  var mode = 'board';
  try { mode = localStorage.getItem(MODE_KEY) || 'board'; } catch (e) {}

  var DAYS = [[1, 'Bazar ertəsi'], [2, 'Çərşənbə axşamı'], [3, 'Çərşənbə'], [4, 'Cümə axşamı'], [5, 'Cümə']];
  var AYQ = ['', 'yan', 'fev', 'mar', 'apr', 'may', 'iyn', 'iyl', 'avq', 'sen', 'okt', 'noy', 'dek'];
  var sd = function (k) { var p = k.split('-'); return +p[2] + ' ' + AYQ[+p[1]]; };
  var mon = function (k) { var d = new Date(k + 'T00:00'); d.setDate(d.getDate() - ((d.getDay() + 6) % 7)); return iso(d); };
  var add = function (k, n) { var d = new Date(k + 'T00:00'); d.setDate(d.getDate() + n); return iso(d); };
  var col = function (st) { return (KP_STN[st] || KP_STN.plan)[2]; };
  var srcN = function (r) { var n = KP_SRCN[r.src]; return n ? n[0] + ' ' + n[1] : ''; };
  var PLS = { ig: 'IG', fb: 'FB', tt: 'TT', li: 'in', yt: 'YT' };

  function card(r) {
    var isFix = r.st === 'fix';
    if (r.kind === 'story') {
      return '<button class="kbs" data-kp="open" data-id="' + esc(r.id) + '" style="--c:' + col(r.st) + '">' +
        '<i></i><span>' + (r.stype === 'əlamətdar' ? '🇦🇿 ' : r.stype === 'bayram' ? '🎉 ' : '✨ ') + 'Story</span><b>' + esc(r.title || r.topic || '') + '</b>' +
        (isFix && r.fix ? '<em>💬 ' + esc(r.fix) + '</em>' : '') + '</button>';
    }
    return '<button class="kbc' + (isFix ? ' fx' : '') + '" data-kp="open" data-id="' + esc(r.id) + '" style="--c:' + col(r.st) + '">' +
      '<div class="kbc-t"><span class="kbf">' + (kpIsV(r) ? '🎬 Video' : '🖼️ Statik') + '</span>' + kpPill(r.st) + '</div>' +
      '<b class="kbc-n">' + esc(r.title || r.topic || 'Adsız') + '</b>' +
      (r.topic && r.topic !== r.title ? '<small class="kbc-m">' + esc(r.topic) + '</small>' : '') +
      '<div class="kbc-p">' + KP_PL.filter(function (x) { return kpOn(r, x[0]); }).map(function (x) { return '<i class="pl-' + x[0] + '" title="' + x[1] + '">' + PLS[x[0]] + '</i>'; }).join('') +
      '<span class="kbc-s">' + esc(srcN(r)) + '</span></div>' +
      (isFix && r.fix ? '<div class="kbc-x"><small>Rəhbərin qeydi</small>' + esc(r.fix) + '</div>' : '') +
      '</button>';
  }

  function board(L) {
    var W = {};
    L.forEach(function (r) {
      var w = mon(r.k), g = r.g;
      if (g === 0 || g === 6) g = 5;
      (W[w] = W[w] || {})[g] = (W[w][g] || []).concat([r]);
    });
    var weeks = Object.keys(W).sort();
    var leg = KP_ST.map(function (s) { return '<span><i style="background:' + s[2] + '"></i>' + s[1] + '</span>'; }).join('');
    var h = '<div class="kbtop"><div class="kbleg">' + leg + '</div><button class="btn kbpr" data-kpb="print">🖨 Çap / PDF</button></div>';
    h += '<div class="pn kpwrap kbwrap"><div class="kpscroll"><table class="kbt"><colgroup><col class="kbw"><col><col><col><col><col></colgroup><thead><tr><th>Həftə</th>' +
      DAYS.map(function (d) { return '<th>' + d[1] + '</th>'; }).join('') + '</tr></thead><tbody>';
    if (!weeks.length) h += '<tr><td colspan="6" class="kmu" style="padding:24px;text-align:center">Bu filtrə uyğun paylaşım yoxdur</td></tr>';
    weeks.forEach(function (w) {
      var all = []; Object.keys(W[w]).forEach(function (g) { all = all.concat(W[w][g]); });
      var p = all.filter(function (r) { return r.kind === 'post'; }).length, s = all.length - p;
      var ok = all.filter(function (r) { return r.st === 'ok' || r.st === 'pub'; }).length;
      var fx = all.filter(function (r) { return r.st === 'fix'; }).length;
      var cur = today >= w && today <= add(w, 6);
      h += '<tr class="' + (cur ? 'kbcur' : '') + '"><td class="kbwk"><b>' + sd(w) + ' – ' + sd(add(w, 4)) + '</b>' +
        (cur ? '<span class="kbnow">Bu həftə</span>' : '') +
        '<small>' + p + ' post · ' + s + ' story</small>' +
        '<div class="kbbar"><i style="width:' + (all.length ? Math.round(ok / all.length * 100) : 0) + '%"></i></div>' +
        '<small>' + ok + ' / ' + all.length + ' təsdiqlənib' + (fx ? ' · <em>' + fx + ' düzəliş</em>' : '') + '</small></td>';
      DAYS.forEach(function (d) {
        var k = add(w, d[0] - 1), its = (W[w][d[0]] || []).slice().sort(function (a, b) { return a.kind === b.kind ? 0 : a.kind === 'post' ? -1 : 1; });
        var out = k < KP_FROM || k > KP_TO;
        h += '<td class="kbd' + (k === today ? ' kbtoday' : '') + (out ? ' kbout' : '') + (its.length ? '' : ' kbempty') + '">' +
          '<div class="kbdate">' + sd(k) + (k === today ? ' · bu gün' : '') + '</div>' +
          (its.length ? its.map(card).join('') : '<div class="kbno">—</div>') + '</td>';
      });
      h += '</tr>';
    });
    h += '</tbody></table></div></div>' +
      '<div class="kmu kpnote">Həftələr sətirdə, iş günləri yan-yana. Postlar Instagram, Facebook, TikTok və LinkedIn-ə gedir; videolar həm də YouTube Shorts-a. Şənbə-bazar plan yoxdur. Karta toxunun: tam caption, ssenari, təsdiq və düzəliş orada.</div>';
    return h;
  }

  function filtered(all) {
    return all.filter(function (r) {
      return (kpMon === 'all' || r.k.slice(5, 7) === kpMon) && (kpStf === 'all' || r.st === kpStf);
    });
  }

  kpSimpleV = function (all) {
    kpSrc = 'all';
    var t = document.createElement('template');
    t.innerHTML = orig(all);
    var root = t.content;
    var prod = root.querySelector('.kpprod'); if (prod) prod.remove();
    var tools = root.querySelector('.kptools');
    if (tools) {
      var sw = document.createElement('div');
      sw.className = 'kbsw';
      sw.innerHTML = '<button class="' + (mode === 'board' ? 'on' : '') + '" data-kpb="mode" data-v="board">📅 Rəhbərlik cədvəli</button>' +
        '<button class="' + (mode === 'list' ? 'on' : '') + '" data-kpb="mode" data-v="list">📋 Siyahı</button>';
      tools.insertBefore(sw, tools.firstChild);
    }
    if (mode === 'board') {
      var wrap = root.querySelector('.pn.kpwrap'), note = root.querySelector('.kpnote');
      var box = document.createElement('div');
      box.innerHTML = board(filtered(all));
      if (wrap) { wrap.replaceWith.apply(wrap, Array.prototype.slice.call(box.childNodes)); }
      if (note) note.remove();
    }
    var d = document.createElement('div'); d.appendChild(root.cloneNode(true));
    return d.innerHTML;
  };

  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-kpb]'); if (!b) return;
    if (b.dataset.kpb === 'mode') {
      mode = b.dataset.v; try { localStorage.setItem(MODE_KEY, mode); } catch (x) {}
      render();
    } else if (b.dataset.kpb === 'print') {
      document.body.classList.add('kbprint'); window.print();
      setTimeout(function () { document.body.classList.remove('kbprint'); }, 500);
    }
  });

  var css = document.createElement('style');
  css.textContent = [
    '.kbsw{display:inline-flex;background:var(--hov);border:1px solid var(--bd);border-radius:11px;padding:3px;gap:2px;margin-right:6px}',
    '.kbsw button{border:0;background:transparent;color:var(--mu);font:inherit;font-size:13px;font-weight:600;padding:7px 12px;border-radius:8px;cursor:pointer}',
    '.kbsw button.on{background:var(--pn);color:var(--tx);box-shadow:var(--sh)}',
    '.kbtop{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin:-2px 0 10px}',
    '.kbleg{display:flex;flex-wrap:wrap;gap:12px;font-size:12px;color:var(--mu)}',
    '.kbleg span{display:inline-flex;align-items:center;gap:6px}',
    '.kbleg i{width:9px;height:9px;border-radius:50%;display:inline-block}',
    '.kbwrap .kpscroll{max-height:none;min-height:0;overflow-x:auto;overflow-y:visible}',
    '.kbt{border-collapse:separate;border-spacing:0;width:100%;min-width:1000px;table-layout:fixed;font-size:13px}',
    '.kbt col.kbw{width:134px}',
    '.kbt th{position:sticky;top:0;z-index:2;background:var(--hov);text-align:left;font-size:11.5px;text-transform:uppercase;letter-spacing:.04em;color:var(--mu);padding:10px 12px;border-bottom:1px solid var(--bd);white-space:nowrap}',
    '.kbt th:first-child,.kbt td:first-child{position:sticky;left:0;z-index:1}',
    '.kbt th:first-child{z-index:3}',
    '.kbt td{vertical-align:top;border-bottom:1px solid var(--bd);border-left:1px solid var(--bd);padding:10px;background:var(--pn)}',
    '.kbt td:first-child{border-left:0;background:var(--hov)}',
    '.kbwk b{display:block;font-size:13.5px;white-space:nowrap}',
    '.kbwk small{display:block;color:var(--mu);font-size:11.5px;margin-top:4px}',
    '.kbwk small em{color:var(--late);font-style:normal;font-weight:600}',
    '.kbnow{display:inline-block;margin-top:5px;background:var(--ac);color:#fff;font-size:10.5px;font-weight:700;border-radius:20px;padding:2px 8px}',
    '.kbbar{height:5px;background:var(--bd);border-radius:5px;margin-top:8px;overflow:hidden}',
    '.kbbar i{display:block;height:100%;background:var(--ok);border-radius:5px}',
    '.kbcur td{background:color-mix(in srgb,var(--ac) 3%,var(--pn))}',
    '.kbcur td:first-child{box-shadow:inset 4px 0 0 var(--ac)}',
    '.kbdate{font-size:11px;font-weight:700;color:var(--mu);margin-bottom:7px;text-transform:uppercase;letter-spacing:.03em}',
    '.kbtoday{background:color-mix(in srgb,var(--ac) 7%,var(--pn))!important;box-shadow:inset 0 3px 0 var(--ac)}',
    '.kbtoday .kbdate{color:var(--ac)}',
    '.kbout{opacity:.45}',
    '.kbempty .kbno{color:var(--bd);font-size:20px;text-align:center;padding:14px 0}',
    '.kbc{display:block;width:100%;text-align:left;font:inherit;color:inherit;background:var(--pn);border:1px solid var(--bd);border-left:4px solid var(--c);border-radius:11px;padding:9px 10px;margin-bottom:8px;cursor:pointer;box-shadow:var(--sh);transition:transform .12s,box-shadow .12s}',
    '.kbc:hover{transform:translateY(-1px);box-shadow:var(--shh)}',
    '.kbc.fx{background:color-mix(in srgb,var(--late) 5%,var(--pn))}',
    '.kbc-t{display:flex;justify-content:space-between;align-items:center;gap:6px;margin-bottom:6px}',
    '.kbf{font-size:11.5px;font-weight:600;color:var(--stx);white-space:nowrap}',
    '.kbc .kpst{font-size:10.5px}',
    '.kbc-n{display:block;font-size:13.5px;line-height:1.3;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}',
    '.kbc-m{display:block;color:var(--mu);font-size:11.5px;margin-top:3px}',
    '.kbc-p{display:flex;flex-wrap:wrap;align-items:center;gap:3px;margin-top:8px}',
    '.kbc-p i{font-style:normal;font-size:10px;font-weight:700;color:var(--mu);border:1px solid var(--bd);border-radius:5px;padding:1px 4px}',
    '.kbc-s{margin-left:auto;font-size:11px;color:var(--mu);white-space:nowrap}',
    '.kbc-x{margin-top:8px;border-radius:8px;background:color-mix(in srgb,var(--late) 10%,var(--pn));color:var(--tx);font-size:12px;line-height:1.35;padding:7px 8px;display:-webkit-box;-webkit-line-clamp:5;-webkit-box-orient:vertical;overflow:hidden}',
    '.kbc-x small{display:block;color:var(--late);font-weight:700;font-size:10.5px;text-transform:uppercase;letter-spacing:.04em;margin-bottom:2px}',
    '.kbs{display:flex;flex-wrap:wrap;align-items:center;gap:5px;width:100%;text-align:left;font:inherit;color:inherit;background:var(--hov);border:1px dashed var(--bd);border-radius:9px;padding:6px 8px;margin-bottom:8px;cursor:pointer;font-size:12px}',
    '.kbs i{width:8px;height:8px;border-radius:50%;background:var(--c);flex:none}',
    '.kbs span{color:var(--mu);font-weight:600}',
    '.kbs b{font-weight:600;flex:1 1 100%}',
    '.kbs em{flex:1 1 100%;font-style:normal;color:var(--late);font-size:11.5px}',
    '@media print{body.kbprint .side,body.kbprint aside,body.kbprint nav,body.kbprint header,body.kbprint .kpsum,body.kbprint .kptools,body.kbprint .kbpr,body.kbprint .kpbr{display:none!important}',
    'body.kbprint .kpscroll{overflow:visible!important}body.kbprint .kbt{min-width:0;font-size:10.5px}body.kbprint .kbc,body.kbprint .kbs{break-inside:avoid;box-shadow:none}}'
  ].join('\n');
  document.head.appendChild(css);

  try { if (typeof tab !== 'undefined' && tab === 'kp') render(); } catch (e) {}
})();
