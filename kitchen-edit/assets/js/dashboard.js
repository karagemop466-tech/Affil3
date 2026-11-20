/* ShopNow Kitchen Edit — dashboard tools: event queue viewer/export + Associates link-builder.
   Runs only on dashboard/index.html. */
(function () {
  "use strict";
  var CFG = window.SHOPNOW_CONFIG || {};

  /* Events queue */
  var qEl = document.getElementById("event-queue-body");
  var countEl = document.getElementById("event-queue-count");
  function refreshQueue() {
    var arr = (window.shopnowQueue && window.shopnowQueue.all()) || [];
    if (countEl) countEl.textContent = String(arr.length);
    if (!qEl) return;
    qEl.innerHTML = "";
    arr.slice(-12).reverse().forEach(function (e) {
      var tr = document.createElement("tr");
      var t = document.createElement("td"); t.textContent = e.ts;
      var n = document.createElement("td"); n.textContent = e.event;
      var p = document.createElement("td"); p.textContent = e.path;
      var d = document.createElement("td"); d.textContent = JSON.stringify(e.payload);
      tr.appendChild(t); tr.appendChild(n); tr.appendChild(p); tr.appendChild(d);
      qEl.appendChild(tr);
    });
    if (!arr.length) {
      var tr = document.createElement("tr");
      var td = document.createElement("td"); td.colSpan = 4;
      td.textContent = "Queue is empty in this browser. Events appear here as you browse the site.";
      tr.appendChild(td); qEl.appendChild(tr);
    }
  }
  refreshQueue();

  var exportBtn = document.getElementById("export-events");
  if (exportBtn) {
    exportBtn.addEventListener("click", function () {
      var arr = (window.shopnowQueue && window.shopnowQueue.all()) || [];
      var blob = new Blob([JSON.stringify({ exported_at: new Date().toISOString(), events: arr }, null, 2)], { type: "application/json" });
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "shopnow-events-" + new Date().toISOString().slice(0, 10) + ".json";
      document.body.appendChild(a); a.click(); a.remove();
      if (typeof window.shopnowTrack === "function") {
        window.shopnowTrack("dashboard_event_exported", { count: arr.length });
      }
      refreshQueue();
    });
  }
  var clearBtn = document.getElementById("clear-events");
  if (clearBtn) {
    clearBtn.addEventListener("click", function () {
      if (window.shopnowQueue) window.shopnowQueue.clear();
      refreshQueue();
    });
  }

  /* Associates link-builder — validates the 10-character ASIN format (S05) and
     composes a formatted link with the tracking ID. Final link must be generated
     inside Associates Central; this tool is a pre-check, not a link generator. */
  var asinEl = document.getElementById("lb-asin");
  var outEl = document.getElementById("lb-out");
  var msgEl = document.getElementById("lb-msg");
  function asinOk(v) { return /^B0[0-9A-Z]{8}$/.test(v) || /^[0-9A-Z]{10}$/.test(v); }
  function build() {
    if (!asinEl || !outEl || !msgEl) return;
    var v = (asinEl.value || "").trim().toUpperCase();
    if (!v) {
      msgEl.textContent = "";
      outEl.textContent = "—";
      outEl.className = "";
      return;
    }
    if (!asinOk(v)) {
      msgEl.textContent = "Format check fails: Amazon defines an ASIN as a 10-character alphanumeric code (typically B0 + 8 characters). Submitted-style 9-character identifiers will not compose a valid /dp/ URL. Source: sell.amazon.com/blog/what-is-an-asin (S05).";
      msgEl.className = "err";
      outEl.textContent = "—";
      outEl.className = "";
      return;
    }
    msgEl.textContent = "Format check passes (10 characters). Next step is the manual gate G5: generate the actual Special Link inside Associates Central (SiteStripe or Link Builder), confirm the destination lands on this ASIN, and confirm a test click appears in your Associates reports — then record it in the product's intent record.";
    msgEl.className = "ok";
    outEl.textContent = "https://www.amazon.com/dp/" + v + "/?tag=" + (CFG.trackingId || "");
    outEl.className = "ok";
  }
  if (asinEl) {
    asinEl.addEventListener("input", build);
    build();
  }
})();
