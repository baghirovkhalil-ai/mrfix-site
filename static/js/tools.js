/* Hesablayıcılar və dərz rəngi studiyası */
(function () {
  "use strict";
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var ROOT = document.body.getAttribute("data-root") || "./";
  function fmt(n, d) { return (d ? n.toFixed(d) : String(Math.round(n))).replace(".", ","); }
  function seg(box, onPick) {
    $$("button", box).forEach(function (b) { b.addEventListener("click", function () { $$("button", box).forEach(function (x) { x.setAttribute("aria-pressed", x === b); }); onPick(b.getAttribute("data-v")); }); });
  }
  function wa(t) { return window.MRFIX_WA ? window.MRFIX_WA(t) : "#"; }

  /* 1. Dərz dolğusu */
  var g = $("#calc-grout");
  if (g) {
    var s = { a: 300, b: 300, j: 3, d: 8, area: 20 };
    seg($("[data-seg=size]", g), function (v) { var p = v.split("x"); s.a = +p[0]; s.b = +p[1]; run(); });
    seg($("[data-seg=joint]", g), function (v) { s.j = +v; run(); });
    $("#g-depth").addEventListener("change", function (e) { s.d = +e.target.value; run(); });
    $("#g-area").addEventListener("input", function (e) { s.area = +e.target.value; run(); });
    function run() {
      var per = ((s.a + s.b) / (s.a * s.b)) * s.j * s.d * 1.6, tot = per * s.area * 1.1;
      var pick = s.j <= 6 ? ["FUGAMAX® COLORFUL", "mehsul/fugamax-colorful/"] : s.j <= 8 ? ["FUGAMAX® FLEX", "mehsul/fugamax-flex/"] : ["FUGAMAX® COTTO", "mehsul/fugamax-cotto/"];
      $("#g-area-out").textContent = s.area + " m²";
      $("#g-meta").textContent = (s.a / 10) + "×" + (s.b / 10) + " sm · dərz " + s.j + " mm · qalınlıq " + s.d + " mm · " + s.area + " m²";
      $("#g-total").textContent = tot < 10 ? fmt(tot, 1) : fmt(tot);
      $("#g-per").textContent = fmt(per, 2) + " kq/m²";
      var a = $("#g-pick"); a.textContent = pick[0]; a.href = ROOT + pick[1];
      $("#g-order").href = wa("Salam! " + s.area + " m², " + (s.a / 10) + "×" + (s.b / 10) + " sm kafel, " + s.j + " mm dərz üçün təxminən " + $("#g-total").textContent + " kq " + pick[0] + " lazımdır. Qiymət və ən yaxın diler?");
    }
    run();
  }

  /* 2. Kafel yapışdırıcısı */
  var y = $("#calc-adh");
  if (y) {
    var ys = { area: 20, k: 1 };
    seg($("[data-seg=method]", y), function (v) { ys.k = +v; runY(); });
    $("#y-area").addEventListener("input", function (e) { ys.area = +e.target.value; runY(); });
    $("#y-prod").addEventListener("change", runY);
    function runY() {
      var lo = 5 * ys.area * ys.k, hi = 6 * ys.area * ys.k, bags = Math.ceil(hi / 25);
      var opt = $("#y-prod").selectedOptions[0];
      $("#y-area-out").textContent = ys.area + " m²";
      $("#y-total").textContent = fmt(hi);
      $("#y-range").textContent = fmt(lo) + "–" + fmt(hi) + " kq";
      $("#y-bags").textContent = bags + " kisə × 25 kq";
      var a = $("#y-pick"); a.textContent = opt.textContent; a.href = ROOT + opt.value;
      $("#y-order").href = wa("Salam! " + ys.area + " m² üçün " + opt.textContent + " — təxminən " + bags + " kisə (25 kq) lazımdır. Qiymət və ən yaxın diler?");
    }
    runY();
  }

  /* 3. Su izolyasiyası */
  var w = $("#calc-wp");
  if (w) {
    var ws = { area: 15, coats: 2 };
    seg($("[data-seg=coats]", w), function (v) { ws.coats = +v; runW(); });
    $("#w-area").addEventListener("input", function (e) { ws.area = +e.target.value; runW(); });
    $("#w-prod").addEventListener("change", runW);
    function runW() {
      var o = $("#w-prod").selectedOptions[0], lo = +o.getAttribute("data-lo"), hi = +o.getAttribute("data-hi");
      var a1 = lo * ws.coats * ws.area, a2 = hi * ws.coats * ws.area;
      $("#w-area-out").textContent = ws.area + " m²";
      $("#w-total").textContent = fmt(a2);
      $("#w-range").textContent = fmt(a1) + "–" + fmt(a2) + " kq";
      $("#w-per").textContent = fmt(lo, 2) + "–" + fmt(hi, 2) + " kq/m² × " + ws.coats + " qat";
      var a = $("#w-pick"); a.textContent = o.textContent; a.href = ROOT + o.value;
      $("#w-order").href = wa("Salam! " + ws.area + " m² sahə, " + ws.coats + " qat " + o.textContent + " üçün təxminən " + fmt(a2) + " kq lazımdır. Qiymət və ən yaxın diler?");
    }
    runW();
  }

  /* 4. Şap və təmir */
  var f = $("#calc-floor");
  if (f) {
    var fs = { area: 30, mm: 5 };
    $("#f-area").addEventListener("input", function (e) { fs.area = +e.target.value; runF(); });
    $("#f-mm").addEventListener("input", function (e) { fs.mm = +e.target.value; runF(); });
    $("#f-prod").addEventListener("change", runF);
    function runF() {
      var o = $("#f-prod").selectedOptions[0], k = +o.getAttribute("data-k"), tot = k * fs.mm * fs.area;
      $("#f-area-out").textContent = fs.area + " m²"; $("#f-mm-out").textContent = fs.mm + " mm";
      $("#f-total").textContent = fmt(tot);
      $("#f-per").textContent = fmt(k * fs.mm, 2) + " kq/m²";
      $("#f-bags").textContent = Math.ceil(tot / 25) + " kisə × 25 kq";
      var a = $("#f-pick"); a.textContent = o.textContent; a.href = ROOT + o.value;
      $("#f-order").href = wa("Salam! " + fs.area + " m², " + fs.mm + " mm qalınlıq üçün təxminən " + fmt(tot) + " kq " + o.textContent + " lazımdır. Qiymət və ən yaxın diler?");
    }
    runF();
  }

  /* Dərz rəngi studiyası */
  var st = $("#studio");
  if (st) {
    var wall = $("#wall"), state = { g: 2, tile: "#F6F5F1", lay: "square" };
    var grouts = JSON.parse($("#groutData").textContent);
    function build() {
      var n = state.lay === "square" ? 36 : state.lay === "metro" ? 40 : 6, html = "";
      for (var i = 0; i < n; i++) html += '<div class="t"></div>';
      wall.className = "wall " + state.lay; wall.innerHTML = html; paint();
    }
    function paint() {
      var gr = grouts[state.g];
      wall.style.background = gr.hex; wall.style.setProperty("--tile", state.tile);
      $("#gName").textContent = gr.name; $("#gName2").textContent = gr.name;
      $$(".sw", st).forEach(function (b, i) { b.setAttribute("aria-pressed", i === state.g); });
      $("#gOrder").href = wa("Salam! FUGAMAX® dərz dolğusu, rəng: " + gr.name + ". Qiymət və ən yaxın diler?");
    }
    $$(".sw", st).forEach(function (b, i) { b.addEventListener("click", function () { state.g = i; paint(); }); });
    seg($("[data-seg=tile]", st), function (v) { state.tile = v; paint(); });
    seg($("[data-seg=layout]", st), function (v) { state.lay = v; build(); });
    build();
  }
})();
