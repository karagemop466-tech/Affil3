/* ==========================================================================
   Counter & Crumb — privacy-preserving event capture.

   What this collects:
     - a rotating, per-session pseudonymous id (never linked to a person)
     - the event name, the page path, and the fields listed for that event
   What this never collects:
     - IP addresses, user agents, cookies, advertising ids, email addresses
     - anything that identifies a person

   The id is hashed server-side with a salt that never reaches the browser, so the
   stored record cannot be reversed into the value sent from here.

   Do Not Track and Global Privacy Control are honoured: if either is set, no
   event leaves the browser.
   ========================================================================== */
(function () {
  "use strict";

  var CFG = window.AFFIL3 || {};
  var ENDPOINT = CFG.endpoint || "/api/collect";
  var EVENTS = (CFG.events || []).map(function (e) { return e.id; });
  var ID_KEY = "affil3.sid";
  var queue = [];
  var dnt =
    (typeof navigator !== "undefined" &&
      (navigator.doNotTrack === "1" ||
        navigator.doNotTrack === "yes" ||
        (typeof window.doNotTrack !== "undefined" && window.doNotTrack === "1") ||
        navigator.globalPrivacyControl === true)) ||
    false;

  function sid() {
    try {
      var v = sessionStorage.getItem(ID_KEY);
      if (!v) {
        var buf = new Uint8Array(16);
        (window.crypto || window.msCrypto).getRandomValues(buf);
        v = Array.prototype.map
          .call(buf, function (b) { return ("0" + b.toString(16)).slice(-2); })
          .join("");
        sessionStorage.setItem(ID_KEY, v);
      }
      return v;
    } catch (e) {
      return "no-store";
    }
  }

  function path() {
    return window.location.pathname;
  }

  function referrer() {
    try {
      var r = document.referrer;
      if (!r) return "";
      var u = new URL(r, window.location.href);
      return u.hostname === window.location.hostname ? "internal" : u.hostname;
    } catch (e) {
      return "";
    }
  }

  function payload(event, fields) {
    var p = { v: 1, sid: sid(), ev: event, path: path(), ts: new Date().toISOString() };
    for (var k in fields) {
      if (Object.prototype.hasOwnProperty.call(fields, k) && fields[k] !== undefined && fields[k] !== null) {
        p[k] = fields[k];
      }
    }
    return p;
  }

  function send(body) {
    if (dnt) return;
    var blob = new Blob([body], { type: "application/json" });
    try {
      if (navigator.sendBeacon) {
        navigator.sendBeacon(ENDPOINT, blob);
        return;
      }
    } catch (e) { /* fall through */ }
    try {
      fetch(ENDPOINT, {
        method: "POST",
        body: blob,
        headers: { "Content-Type": "application/json" },
        keepalive: true,
        mode: "cors",
        credentials: "omit"
      }).catch(function () { queue.push(body); });
    } catch (e) {
      queue.push(body);
    }
  }

  function track(event, fields) {
    if (dnt) return;
    if (EVENTS.length && EVENTS.indexOf(event) === -1) return;
    send(JSON.stringify(payload(event, fields || {})));
  }

  /* -- page view ---------------------------------------------------------- */
  track("page_view", {
    referrer: referrer(),
    viewport: window.innerWidth < 700 ? "narrow" : window.innerWidth < 1100 ? "mid" : "wide"
  });

  /* -- outbound affiliate click ------------------------------------------- */
  document.addEventListener(
    "click",
    function (e) {
      var a = e.target && e.target.closest ? e.target.closest("a[data-product]") : null;
      if (!a) return;
      track("outbound_click", {
        product_id: a.getAttribute("data-product") || "",
        asin: a.getAttribute("data-asin") || "",
        placement: a.getAttribute("data-placement") || "unknown"
      });
    },
    true
  );

  /* -- guide read depth ---------------------------------------------------- */
  var depthMarks = {};
  var deepPage = document.querySelector("[data-guide]") || document.querySelector("[data-comparison]");
  if (deepPage) {
    var reportDepth = function () {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      if (h <= 0) return;
      var pct = Math.min(100, Math.round((window.scrollY / h) * 100));
      [25, 50, 75, 100].forEach(function (mark) {
        if (pct >= mark && !depthMarks[mark]) {
          depthMarks[mark] = true;
          track("guide_progress", { depth: mark });
        }
      });
    };
    var ticking = false;
    window.addEventListener(
      "scroll",
      function () {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(function () {
          reportDepth();
          ticking = false;
        });
      },
      { passive: true }
    );
    window.addEventListener("beforeunload", reportDepth);
  }

  /* -- comparison / register table interaction ---------------------------- */
  document.addEventListener("click", function (e) {
    var th = e.target && e.target.closest ? e.target.closest("th[aria-sort]") : null;
    if (th) {
      var table = th.closest("table");
      track("table_use", {
        table_id: (table && table.id) || "unknown",
        action: "sort",
        filter: th.getAttribute("data-col") || ""
      });
    }
    var filter = e.target && e.target.closest ? e.target.closest("[data-filter-select]") : null;
    if (filter) {
      var tbl = filter.getAttribute("data-filter-select");
      track("table_use", {
        table_id: tbl || "unknown",
        action: "filter",
        filter: filter.getAttribute("data-filter-name") || filter.value || ""
      });
    }
  });

  /* -- reader capture ------------------------------------------------------ */
  document.addEventListener("submit", function (e) {
    var form = e.target;
    if (!form.matches || !form.matches("[data-signup]")) return;
    track("reader_signup", { placement: form.getAttribute("data-signup") || "footer" });
  });

  window.AFFIL3_TRACK = track;
})();
