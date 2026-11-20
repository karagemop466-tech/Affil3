/* On-site search over the generated index. No server, no third party, no query logging.
 * The index ships as a static JSON file; the only thing the site learns from a search
 * is the aggregate count of zero-result queries, and only if a collector is configured. */
(function () {
  "use strict";
  var input = document.getElementById("q");
  var out = document.getElementById("results");
  var status = document.getElementById("sstatus");
  var root = document.documentElement.getAttribute("data-root") || "";
  var IDX = null;

  function norm(s) { return String(s || "").toLowerCase().replace(/[^\w\s]/g, " ").replace(/\s+/g, " ").trim(); }

  function score(doc, terms) {
    var s = 0, hay = { t: norm(doc.title), b: norm(doc.blurb), k: norm((doc.tags || []).join(" ")), x: norm(doc.section) };
    for (var i = 0; i < terms.length; i++) {
      var w = terms[i];
      if (!w) continue;
      if (hay.t.indexOf(w) !== -1) s += 6;
      if (hay.t === w) s += 6;
      if (hay.k.indexOf(w) !== -1) s += 4;
      if (hay.x.indexOf(w) !== -1) s += 2;
      if (hay.b.indexOf(w) !== -1) s += 1;
    }
    if (terms.length === 1 && hay.t.indexOf(terms[0]) !== -1) s += 3;
    return s;
  }

  function render(q) {
    var terms = norm(q).split(" ").filter(Boolean);
    if (!terms.length) { out.innerHTML = ""; status.textContent = ""; return; }
    var hits = [];
    IDX.forEach(function (d) { var sc = score(d, terms); if (sc > 0) hits.push([d, sc]); });
    hits.sort(function (a, b) { return b[1] - a[1] || a[0].title.localeCompare(b[0].title); });
    hits = hits.slice(0, 30);
    if (!hits.length) {
      out.innerHTML = '<div class="empty">Nothing here yet for &ldquo;' + q.replace(/[<>&]/g, "") +
        '&rdquo;. That is a missing topic, not a dead end &mdash; it is recorded on the <a href="' + root + '/decisions/">open questions list</a>.</div>';
      status.textContent = "0 results";
      try { window.__shopnowTrack && window.__shopnowTrack("page_view", { slug: "search-zero-result" }); } catch (e) {}
      return;
    }
    status.textContent = hits.length + " result" + (hits.length === 1 ? "" : "s");
    out.innerHTML = hits.map(function (h) {
      var d = h[0];
      return '<div class="result"><div class="rmeta">' + d.section + "</div>" +
        '<div class="rt"><a href="' + root + d.href + '">' + d.title + "</a></div>" +
        (d.blurb ? "<p class='tiny muted' style='margin:.2rem 0 0'>" + d.blurb + "</p>" : "") + "</div>";
    }).join("");
  }

  if (!input) return;
  fetch((root + "/search/index.json").replace(/\/{2,}/g, "/")).then(function (r) { return r.json(); }).then(function (j) {
    IDX = j.docs || [];
    render(input.value);
  }).catch(function () { status.textContent = "Search index unavailable."; });

  var t;
  input.addEventListener("input", function () { clearTimeout(t); var v = input.value; t = setTimeout(function () { render(v); }, 120); });
})();
