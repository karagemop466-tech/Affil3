/* ==========================================================================
   Counter & Crumb — site behaviour.
   Progressive enhancement only: every page works with this file disabled.
   ========================================================================== */
(function () {
  "use strict";

  /* -- Table sorting ------------------------------------------------------- */
  function valueOf(row, col, type) {
    var cell = row.querySelector('td[data-col="' + col + '"]') || row.cells[col];
    if (!cell) return "";
    var raw = (cell.getAttribute("data-sort") || cell.textContent || "").trim();
    if (type === "num") {
      var n = parseFloat(raw.replace(/[^0-9.\-]/g, ""));
      return isNaN(n) ? -Infinity : n;
    }
    return raw.toLowerCase();
  }

  function initSort(table) {
    var headers = table.querySelectorAll("th[aria-sort]");
    Array.prototype.forEach.call(headers, function (th, idx) {
      th.setAttribute("tabindex", "0");
      th.setAttribute("role", "columnheader");
      function go() {
        var col = th.getAttribute("data-col") || String(idx);
        var type = th.getAttribute("data-type") || "text";
        var tbody = table.tBodies[0];
        if (!tbody) return;
        var current = th.getAttribute("aria-sort");
        var dir = current === "ascending" ? "descending" : "ascending";
        Array.prototype.forEach.call(headers, function (h) { h.setAttribute("aria-sort", "none"); });
        th.setAttribute("aria-sort", dir);
        var rows = Array.prototype.slice.call(tbody.rows);
        rows.sort(function (a, b) {
          var va = valueOf(a, col, type);
          var vb = valueOf(b, col, type);
          if (va < vb) return dir === "ascending" ? -1 : 1;
          if (va > vb) return dir === "ascending" ? 1 : -1;
          return 0;
        });
        rows.forEach(function (r) { tbody.appendChild(r); });
      }
      th.addEventListener("click", go);
      th.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); }
      });
    });
  }

  /* -- Table filtering ----------------------------------------------------- */
  function initFilters(table) {
    var selects = document.querySelectorAll("[data-filter-select='" + table.id + "']");
    if (!selects.length) return;
    var tbody = table.tBodies[0];
    var countEl = document.querySelector("[data-filter-count='" + table.id + "']");
    Array.prototype.forEach.call(selects, function (sel) {
      sel.addEventListener("change", function () {
        var values = {};
        Array.prototype.forEach.call(selects, function (s) {
          if (s.value) values[s.getAttribute("data-filter-name")] = s.value;
        });
        var shown = 0;
        Array.prototype.forEach.call(tbody.rows, function (row) {
          var ok = true;
          for (var name in values) {
            if (name === "q") continue;
            if ((row.getAttribute("data-" + name) || "") !== values[name]) { ok = false; break; }
          }
          var q = values.q;
          if (ok && q) {
            ok = (row.textContent || "").toLowerCase().indexOf(q.toLowerCase()) !== -1;
          }
          row.hidden = !ok;
          if (ok) shown++;
        });
        if (countEl) countEl.textContent = shown + (shown === 1 ? " row" : " rows");
      });
    });
  }

  /* -- To-top button ------------------------------------------------------- */
  function initToTop() {
    var btn = document.querySelector("[data-to-top]");
    if (!btn) return;
    var ticking = false;
    window.addEventListener(
      "scroll",
      function () {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(function () {
          btn.setAttribute("data-visible", window.scrollY > 600 ? "true" : "false");
          ticking = false;
        });
      },
      { passive: true }
    );
    btn.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
  }

  /* -- Reader capture ------------------------------------------------------ */
  function initSignup() {
    var forms = document.querySelectorAll("[data-signup]");
    Array.prototype.forEach.call(forms, function (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var note = form.parentNode.querySelector("[data-signup-note]");
        var input = form.querySelector("input[type=email]");
        if (note) {
          note.textContent =
            "Capture is not connected yet — no list provider has been chosen, so nothing was stored and your address was not sent anywhere. See the Measurement page for what happens next.";
          note.setAttribute("data-state", "pending");
        }
        if (input) input.value = "";
      });
    });
  }

  /* -- Current year -------------------------------------------------------- */
  function initYear() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-year]"), function (el) {
      el.textContent = String(new Date().getFullYear());
    });
  }

  /* -- Live price slots ---------------------------------------------------
     Program Policies 2(b): a Site may only show prices and availability if
     Amazon serves the link that displays them, or if the pricing comes from
     Creators API or PA API. There is no static price anywhere in this site.
     If a price endpoint is configured, this fills the slots from it; if it is
     not configured, the slots keep saying where the price is.
     ------------------------------------------------------------------- */
  function initPriceSlots() {
    var cfg = window.AFFIL3 || {};
    if (!cfg.pricesEndpoint) return;
    var slots = document.querySelectorAll("[data-price-slot]");
    if (!slots.length) return;
    var asins = [];
    Array.prototype.forEach.call(slots, function (s) {
      var asin = s.getAttribute("data-price-slot");
      if (asin && asins.indexOf(asin) === -1) asins.push(asin);
    });
    fetch(cfg.pricesEndpoint + "?asins=" + encodeURIComponent(asins.join(",")),
      { credentials: "omit" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (!data || !data.prices) return;
        Array.prototype.forEach.call(slots, function (s) {
          var asin = s.getAttribute("data-price-slot");
          var entry = data.prices[asin];
          if (!entry || !entry.price) return;
          s.setAttribute("data-state", "ready");
          s.innerHTML = "";
          var strong = document.createElement("strong");
          strong.textContent = entry.price;
          s.appendChild(strong);
          var note = document.createElement("span");
          note.textContent = entry.currency ? " " + entry.currency : "";
          s.appendChild(note);
        });
      })
      .catch(function () { /* leave the slots as they are */ });
  }

  /* -- Boot ---------------------------------------------------------------- */
  function boot() {
    Array.prototype.forEach.call(document.querySelectorAll("table.data"), function (t) {
      initSort(t);
      initFilters(t);
    });
    initToTop();
    initSignup();
    initYear();
    initPriceSlots();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
