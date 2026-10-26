/* Mr.Fix sayt skriptləri — bütün səhifələr üçün */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement;
  root.classList.add("js");
  var ROOT = doc.body.getAttribute("data-root") || "./";
  var WA = doc.body.getAttribute("data-wa") || "";
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, c) { return (c || doc).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };
  function esc(t) { return String(t).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function norm(t) { return String(t).toLocaleLowerCase("az").replace(/®/g, "").replace(/\s+/g, " ").trim(); }
  window.MRFIX_WA = function (text) { return "https://wa.me/" + WA + "?text=" + encodeURIComponent(text); };

  /* Header */
  var header = $(".header");
  var onScroll = function () {
    if (header) header.classList.toggle("scrolled", scrollY > 8);
    var pr = $(".progress");
    if (pr) { var h = doc.documentElement.scrollHeight - innerHeight; pr.style.width = (h > 0 ? scrollY / h * 100 : 0) + "%"; }
  };
  addEventListener("scroll", onScroll, { passive: true }); onScroll();
  $$(".has-mega > button").forEach(function (b) {
    b.addEventListener("click", function () { var li = b.parentNode; var o = !li.classList.contains("open"); $$(".has-mega").forEach(function (x) { x.classList.remove("open"); }); li.classList.toggle("open", o); b.setAttribute("aria-expanded", o); });
  });
  doc.addEventListener("click", function (e) { if (!e.target.closest(".has-mega")) $$(".has-mega").forEach(function (x) { x.classList.remove("open"); }); });

  /* Drawer */
  var drawer = $("#drawer");
  function drawerSet(o) { if (!drawer) return; drawer.classList.toggle("open", o); drawer.setAttribute("aria-hidden", !o); doc.body.style.overflow = o ? "hidden" : ""; if (o) setTimeout(function () { var c = $(".drawer-close"); c && c.focus(); }, 50); }
  $$("[data-drawer-open]").forEach(function (b) { b.addEventListener("click", function () { drawerSet(true); }); });
  $$("[data-drawer-close]").forEach(function (b) { b.addEventListener("click", function () { drawerSet(false); }); });

  /* Reveal + split text */
  $$(".split").forEach(function (el) {
    var words = el.textContent.split(/(\s+)/);
    if (el.querySelector("*")) return;
    el.innerHTML = words.map(function (w, i) { return /^\s+$/.test(w) ? w : '<span class="w" style="transition-delay:' + (i * 0.035).toFixed(2) + 's">' + esc(w) + "</span>"; }).join("");
  });
  var io = "IntersectionObserver" in window ? new IntersectionObserver(function (ents) {
    ents.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 }) : null;
  $$(".rv, .split").forEach(function (el) {
    var r = el.getBoundingClientRect();
    if (!io || reduce || r.top < innerHeight) el.classList.add("in"); else io.observe(el);
  });

  /* Counters */
  var cio = "IntersectionObserver" in window ? new IntersectionObserver(function (ents) {
    ents.forEach(function (en) {
      if (!en.isIntersecting) return; cio.unobserve(en.target);
      var el = en.target, to = +el.getAttribute("data-count"), t0 = performance.now(), d = 1400;
      (function tick(t) { var p = Math.min(1, (t - t0) / d); var v = Math.round(to * (1 - Math.pow(1 - p, 3))); el.firstChild.nodeValue = v; if (p < 1) requestAnimationFrame(tick); })(t0);
    });
  }, { threshold: .4 }) : null;
  $$("[data-count]").forEach(function (el) { if (cio && !reduce) cio.observe(el); });

  /* Word rotator */
  $$(".rotator").forEach(function (r) {
    var items = $$("span", r), i = 0; if (items.length < 2 || reduce) { items[0] && items[0].classList.add("on"); return; }
    items[0].classList.add("on");
    setInterval(function () { var cur = items[i]; cur.classList.remove("on"); cur.classList.add("out"); i = (i + 1) % items.length; var nx = items[i]; nx.classList.remove("out"); void nx.offsetWidth; nx.classList.add("on"); setTimeout(function () { cur.classList.remove("out"); }, 700); }, 2400);
  });

  /* Animated network canvas */
  $$(".fx canvas").forEach(function (cv) {
    var ctx = cv.getContext("2d"), pts = [], W, H, dpr = Math.min(2, devicePixelRatio || 1), run = true;
    function size() { var r = cv.getBoundingClientRect(); W = r.width; H = r.height; cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); var n = Math.round(Math.min(70, W * H / 16000)); pts = []; for (var k = 0; k < n; k++) pts.push({ x: Math.random() * W, y: Math.random() * H, vx: (Math.random() - .5) * .25, vy: (Math.random() - .5) * .25, r: Math.random() * 1.6 + .6, y2: Math.random() < .12 }); }
    function draw() {
      ctx.clearRect(0, 0, W, H);
      for (var a = 0; a < pts.length; a++) {
        var p = pts[a]; if (!reduce) { p.x += p.vx; p.y += p.vy; if (p.x < 0 || p.x > W) p.vx *= -1; if (p.y < 0 || p.y > H) p.vy *= -1; }
        for (var b = a + 1; b < pts.length; b++) { var q = pts[b], dx = p.x - q.x, dy = p.y - q.y, d = dx * dx + dy * dy; if (d < 15000) { ctx.strokeStyle = "rgba(167,179,196," + (0.16 * (1 - d / 15000)).toFixed(3) + ")"; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y); ctx.stroke(); } }
        ctx.fillStyle = p.y2 ? "rgba(255,194,26,.9)" : "rgba(238,242,247,.55)"; ctx.beginPath(); ctx.arc(p.x, p.y, p.y2 ? p.r + 1 : p.r, 0, 6.283); ctx.fill();
      }
      if (run && !reduce) requestAnimationFrame(draw);
    }
    size(); draw(); addEventListener("resize", function () { size(); if (reduce) draw(); });
    if ("IntersectionObserver" in window) new IntersectionObserver(function (e) { var was = run; run = e[0].isIntersecting; if (run && !was && !reduce) draw(); }).observe(cv);
  });

  /* Tabs */
  $$("[data-tabs]").forEach(function (box) {
    var tabs = $$('[role="tab"]', box);
    function sel(t) { tabs.forEach(function (x) { var on = x === t; x.setAttribute("aria-selected", on); x.tabIndex = on ? 0 : -1; var p = doc.getElementById(x.getAttribute("aria-controls")); if (p) p.hidden = !on; }); }
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { sel(t); });
      t.addEventListener("keydown", function (e) { var k = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0; if (k) { var n = tabs[(i + k + tabs.length) % tabs.length]; n.focus(); sel(n); } });
    });
    if (tabs[0]) sel(tabs[0]);
  });

  /* Generic list filter: [data-filter-list] with search input and chips */
  $$("[data-filter]").forEach(function (box) {
    var list = $(box.getAttribute("data-filter")), items = list ? $$("[data-k]", list) : [], q = "", grp = "all";
    var input = $("input[type=search]", box), count = $("[data-count-out]", box.parentNode) || $("[data-count-out]"), empty = $("[data-empty]", box.parentNode);
    function apply() {
      var n = 0, nq = norm(q);
      items.forEach(function (it) { var ok = (grp === "all" || (" " + it.getAttribute("data-g") + " ").indexOf(" " + grp + " ") > -1) && (!nq || norm(it.getAttribute("data-k")).indexOf(nq) > -1); it.hidden = !ok; if (ok) n++; });
      if (count) count.textContent = n + " nəticə"; if (empty) empty.hidden = n > 0;
    }
    if (input) input.addEventListener("input", function () { q = input.value; apply(); });
    $$("[data-g-btn]", box).forEach(function (b) { b.addEventListener("click", function () { grp = b.getAttribute("data-g-btn"); $$("[data-g-btn]", box).forEach(function (x) { x.setAttribute("aria-pressed", x === b); }); apply(); }); });
    var pre = new URLSearchParams(location.search).get("q"); if (pre && input) { input.value = pre; q = pre; }
    apply();
  });

  /* Search overlay */
  var ov = $("#search"), sIn = $("#searchInput"), sRes = $("#searchRes"), idx = null, act = -1;
  function loadIdx(cb) { if (idx) return cb(); fetch(ROOT + "search.json").then(function (r) { return r.json(); }).then(function (j) { idx = j; cb(); }).catch(function () { idx = { items: [], systems: [] }; cb(); }); }
  function openSearch() { if (!ov) return; ov.classList.add("open"); ov.setAttribute("aria-hidden", "false"); setTimeout(function () { sIn.focus(); }, 30); loadIdx(renderS); }
  function closeSearch() { if (!ov) return; ov.classList.remove("open"); ov.setAttribute("aria-hidden", "true"); }
  function find(q, lim) { var n = norm(q); if (!n) return []; var parts = n.split(" "); return idx.items.map(function (it) { var h = norm(it.t + " " + (it.d || "") + " " + (it.x || "")); var s = 0; parts.forEach(function (p) { if (h.indexOf(p) > -1) s += 1; if (norm(it.t).indexOf(p) > -1) s += 2; }); return [s, it]; }).filter(function (a) { return a[0] >= parts.length; }).sort(function (a, b) { return b[0] - a[0]; }).slice(0, lim || 12).map(function (a) { return a[1]; }); }
  function renderS() {
    var q = sIn.value, res = find(q, 12); act = -1;
    if (!q) { sRes.innerHTML = '<p class="search-hint">Məhsul adı, standart (C2TE, R4), səth (hamam, teras) və ya məqalə axtarın.</p>'; return; }
    sRes.innerHTML = res.length ? res.map(function (r) { return '<a href="' + ROOT + r.u + '"><span class="k">' + esc(r.k) + '</span><span><b>' + esc(r.t) + '</b><span>' + esc(r.d || "") + "</span></span></a>"; }).join("") : '<p class="search-hint">Heç nə tapılmadı. Başqa söz yoxlayın və ya köməkçidən soruşun.</p>';
  }
  $$("[data-search-open]").forEach(function (b) { b.addEventListener("click", openSearch); });
  if (ov) {
    $$("[data-search-close]", ov).forEach(function (b) { b.addEventListener("click", closeSearch); });
    sIn.addEventListener("input", function () { loadIdx(renderS); });
    sIn.addEventListener("keydown", function (e) {
      var links = $$("a", sRes); if (!links.length) return;
      if (e.key === "ArrowDown" || e.key === "ArrowUp") { e.preventDefault(); act = (act + (e.key === "ArrowDown" ? 1 : -1) + links.length) % links.length; links.forEach(function (l, i) { l.classList.toggle("act", i === act); }); links[act].scrollIntoView({ block: "nearest" }); }
      if (e.key === "Enter" && act > -1) { e.preventDefault(); links[act].click(); }
    });
  }
  doc.addEventListener("keydown", function (e) {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); openSearch(); }
    if (e.key === "Escape") { closeSearch(); drawerSet(false); var h = $("#helper"); if (h && !h.hidden) h.hidden = true; }
  });

  /* Helper widget */
  var hp = $("#helper"), hLog = $("#helperLog"), hForm = $("#helperForm"), hIn = $("#helperInput"), hStarted = false;
  function say(html, who) { var d = doc.createElement("div"); d.className = "msg " + who; d.innerHTML = html; hLog.appendChild(d); hLog.scrollTop = hLog.scrollHeight; }
  function answer(text) {
    say(esc(text), "me");
    loadIdx(function () {
      var t = norm(text);
      var sys = (idx.systems || []).filter(function (s) { return s.k.some(function (k) { return t.indexOf(k) > -1; }); })[0];
      setTimeout(function () {
        if (sys) {
          say("<b>" + esc(sys.n) + "</b> üçün tövsiyə olunan sistem:<ol>" + sys.l.map(function (l) { return "<li>" + esc(l[0]) + ': <a href="' + ROOT + l[2] + '">' + esc(l[1]) + "</a></li>"; }).join("") + '</ol><a href="' + ROOT + sys.u + '">Tam sistemə və tətbiq qaydasına bax →</a>', "bot");
          return;
        }
        var hits = find(text, 4);
        if (hits.length) { say("Bunlar uyğun ola bilər:<ul>" + hits.map(function (r) { return '<li><a href="' + ROOT + r.u + '">' + esc(r.t) + "</a> — " + esc(r.d || r.k) + "</li>"; }).join("") + "</ul>", "bot"); return; }
        say('Bunu dəqiq tapa bilmədim. Texniki məsləhətçimizə yazın: <a href="' + window.MRFIX_WA("Salam! Saytdan yazıram. Sualım: " + text) + '" target="_blank" rel="noopener">WhatsApp</a>', "bot");
      }, 350);
    });
  }
  function helperOpen() {
    if (!hp) return; hp.hidden = !hp.hidden;
    if (!hp.hidden) {
      if (!hStarted) { hStarted = true; say("Salam! Mən Mr.Fix məhsul köməkçisiyəm. Nə tikirsiniz və ya hansı problemi həll edirsiniz?", "bot"); var q = doc.createElement("div"); q.className = "quick"; ["Hamam izolyasiyası", "Teras kafeli", "Zirzəmidə rütubət", "Fasad istiliyi", "Böyük plitə yapışdırıcısı"].forEach(function (s) { var b = doc.createElement("button"); b.type = "button"; b.textContent = s; b.onclick = function () { q.remove(); answer(s); }; q.appendChild(b); }); hLog.appendChild(q); }
      setTimeout(function () { hIn.focus(); }, 50);
    }
  }
  $$("[data-helper-open]").forEach(function (b) { b.addEventListener("click", helperOpen); });
  $$("[data-helper-close]").forEach(function (b) { b.addEventListener("click", function () { hp.hidden = true; }); });
  if (hForm) hForm.addEventListener("submit", function (e) { e.preventDefault(); var v = hIn.value.trim(); if (!v) return; hIn.value = ""; var qk = $(".quick", hLog); if (qk) qk.remove(); answer(v); });

  /* Copy buttons */
  $$("[data-copy]").forEach(function (b) { b.addEventListener("click", function () { var t = b.getAttribute("data-copy"); var o = b.textContent; if (navigator.clipboard) navigator.clipboard.writeText(t).then(function () { b.textContent = "Kopyalandı"; setTimeout(function () { b.textContent = o; }, 1500); }, function () {}); }); });

  /* Contact form → WhatsApp / e-poçt */
  var cf = $("#contactForm");
  if (cf) cf.addEventListener("submit", function (e) {
    e.preventDefault();
    var f = new FormData(cf), via = (e.submitter && e.submitter.value) || "wa";
    var txt = "Ad: " + f.get("name") + "\nTelefon: " + f.get("phone") + "\nMövzu: " + f.get("topic") + "\n\n" + f.get("msg");
    if (via === "mail") location.href = "mailto:" + cf.getAttribute("data-mail") + "?subject=" + encodeURIComponent("Saytdan sorğu: " + f.get("topic")) + "&body=" + encodeURIComponent(txt);
    else window.open(window.MRFIX_WA(txt), "_blank", "noopener");
    var ok = $("#formOk"); if (ok) ok.hidden = false;
  });
})();
