/* ShopNow 047 - progressive enhancement only. Every page is complete and usable without this file. */
(function () {
  "use strict";

  // --- copy a generated Special Link (fires the intent_confirm event) ---
  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-copy-link]");
    if (!btn) return;
    var url = btn.getAttribute("data-copy-link");
    var done = function (ok) {
      var label = btn.querySelector(".cl-text") || btn;
      var prev = label.textContent;
      label.textContent = ok ? "Copied" : "Press Ctrl+C";
      btn.classList.add("copied");
      window.setTimeout(function () { label.textContent = prev; btn.classList.remove("copied"); }, 1800);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(function () { done(true); }, function () { done(false); });
    } else {
      var ta = document.createElement("textarea");
      ta.value = url; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.left = "-9999px";
      document.body.appendChild(ta); ta.select();
      var ok = false; try { ok = document.execCommand("copy"); } catch (err) { ok = false; }
      document.body.removeChild(ta); done(ok);
    }
    if (window.__shopnowTrack) window.__shopnowTrack("intent_confirm", {
      product_id: btn.getAttribute("data-product") || null,
      link_format: "special_tagged_dp"
    });
  });

  // --- expand/collapse long register rows on the dashboard ---
  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-toggle]");
    if (!t) return;
    var sel = t.getAttribute("data-toggle");
    document.querySelectorAll(sel).forEach(function (n) {
      n.hidden = n.hidden === false ? true : false;
    });
    t.setAttribute("aria-expanded", String(t.getAttribute("aria-expanded") !== "true"));
  });

  // --- filter rows on the dashboard / flagged page by text ---
  document.addEventListener("input", function (e) {
    var f = e.target.closest("[data-filter-table]");
    if (!f) return;
    var q = f.value.trim().toLowerCase();
    var table = document.querySelector(f.getAttribute("data-filter-table"));
    if (!table) return;
    var shown = 0;
    table.querySelectorAll("tbody tr").forEach(function (tr) {
      var hit = !q || tr.textContent.toLowerCase().indexOf(q) !== -1;
      tr.hidden = !hit;
      if (hit) shown++;
    });
    var out = f.parentNode.querySelector("[data-filter-count]");
    if (out) out.textContent = q ? shown + " of " + table.querySelectorAll("tbody tr").length + " rows" : "";
  });
})();
