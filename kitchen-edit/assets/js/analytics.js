/* ShopNow Kitchen Edit — privacy-preserving event collector.
   Implements the five defined events in data/events-schema.json.
   No cookies, no fingerprinting, no cross-site identifiers, no PII fields.
   Events queue in localStorage; POST only when analyticsEndpoint is configured. */
(function () {
  "use strict";
  var CFG = window.SHOPNOW_CONFIG || {};
  var KEY = CFG.eventsQueueKey || "shopnow_events_v1";
  var CAP = CFG.eventsQueueCap || 500;

  function queue() {
    try {
      var raw = window.localStorage.getItem(KEY);
      var arr = raw ? JSON.parse(raw) : [];
      if (!Array.isArray(arr)) arr = [];
      return arr;
    } catch (e) { return []; }
  }
  function save(arr) {
    try {
      if (arr.length > CAP) arr = arr.slice(arr.length - CAP);
      window.localStorage.setItem(KEY, JSON.stringify(arr));
    } catch (e) { /* storage unavailable — collector degrades silently */ }
  }
  function track(name, payload) {
    var evt = {
      event: name,
      ts: new Date().toISOString(),
      path: (location.pathname || "").replace(/^.*\/Affil3/, "") || "/",
      payload: payload || {}
    };
    var arr = queue();
    arr.push(evt);
    save(arr);
    var ep = CFG.analyticsEndpoint;
    if (ep && typeof navigator !== "undefined" && navigator.sendBeacon) {
      try {
        navigator.sendBeacon(ep, new Blob([JSON.stringify(evt)], { type: "application/json" }));
      } catch (e) { /* endpoint may be down; queue retains the copy */ }
    }
    document.dispatchEvent(new CustomEvent("shopnow:tracked", { detail: evt }));
    return evt;
  }

  window.shopnowTrack = track;
  window.shopnowQueue = { all: queue, clear: function () { save([]); } };

  /* 1 — page_view */
  if (document.visibilityState !== "prerender") {
    track("page_view", { title: document.title, referrer: document.referrer || "" });
  }
})();
