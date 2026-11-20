/* Counterwise front-end. Layered behaviour only: the page is complete and every link works with
   JavaScript switched off. No cookies, no fingerprinting, no third-party request.
   Collection is armed only when the build injects a non-empty endpoint (data/config.json →
   measurement.endpoint). While it is unarmed, events queue in this tab's localStorage so that
   nothing is silently discarded and nothing is quietly sent either. */

(function () {
  "use strict";

  var body = document.body;
  var data = body.dataset || {};
  var ENDPOINT = data.analyticsEndpoint || "";
  var COLLECTING = ENDPOINT.length > 0;
  var QUEUE_KEY = "cw.queue.v1";
  var STATE_KEY = "cw.checklist.v1";
  var PAGE = data.page || location.pathname;
  var KIND = data.pageKind || "other";

  var ALLOWED = (data.allowedEvents || "").split(",").filter(Boolean);

  // Respect do-not-track and Global Privacy Control before anything else runs.
  var OPTED_OUT =
    navigator.doNotTrack === "1" ||
    window.doNotTrack === "1" ||
    navigator.msDoNotTrack === "1" ||
    navigator.globalPrivacyControl === true;

  function read(key) {
    try {
      var raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function write(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (e) {
      return false; // private mode, quota, or a locked-down browser: fail silently, never break the page
    }
  }

  function send(name, props) {
    if (OPTED_OUT) return;
    if (ALLOWED.length && ALLOWED.indexOf(name) === -1) return; // schema is data/events.json, enforced here too
    var payload = {
      event: name,
      page: PAGE,
      ts: new Date().toISOString(),
      props: props || {}
    };
    if (!COLLECTING) {
      var q = read(QUEUE_KEY) || [];
      if (q.length < 200) {
        q.push(payload);
        write(QUEUE_KEY, q);
      }
      return;
    }
    var blob = new Blob([JSON.stringify(payload)], { type: "application/json" });
    if (navigator.sendBeacon) {
      navigator.sendBeacon(ENDPOINT + "/e", blob);
      return;
    }
    try {
      fetch(ENDPOINT + "/e", {
        method: "POST",
        body: blob,
        keepalive: true,
        credentials: "omit",
        headers: { "Content-Type": "application/json" }
      }).catch(function () {});
    } catch (e) {
      /* the page must never fail because a counter did */
    }
  }

  // ---------------------------------------------------------------- EV-01 page_view
  if (!COLLECTING) {
    var queued = read(QUEUE_KEY);
    if (queued && queued.length) {
      var views = 0;
      for (var i = 0; i < queued.length; i++) if (queued[i].event === "page_view") views++;
      if (views >= 3) {
        // Already enough local history to be noise; stop growing the queue.
        send = function () {};
      }
    }
  }
  send("page_view", { kind: KIND });

  // ------------------------------------------------------- EV-02 product_link_click
  // Every outbound product link is marked in the build. We record the click; we never change it.
  document.addEventListener(
    "click",
    function (ev) {
      var a = ev.target && ev.target.closest ? ev.target.closest("a[data-outbound]") : null;
      if (!a) return;
      send("product_link_click", {
        product_id: a.dataset.product || "",
        link_state: a.dataset.linkState || "pending-test",
        placement: a.dataset.placement || "inline"
      });
    },
    { capture: true }
  );

  // --------------------------------------------------- EV-04 checklist_item_toggled
  var saved = read(STATE_KEY) || {};
  var boxes = document.querySelectorAll(".checklist input[type=checkbox]");

  function refreshProgress(list) {
    var done = 0;
    for (var i = 0; i < list.length; i++) if (list[i].checked) done++;
    var line = list.length ? list[0].closest(".checklist").querySelector(".progress") : null;
    if (line) line.textContent = done + " of " + list.length + " done · kept in this browser only";
  }

  for (var b = 0; b < boxes.length; b++) {
    (function (box) {
      var key = (box.dataset.checklist || "x") + ":" + (box.dataset.item || String(Math.random()));
      box.dataset.ckey = key;
      if (saved[key]) box.checked = true;
      box.addEventListener("change", function () {
        var state = read(STATE_KEY) || {};
        if (box.checked) state[key] = 1;
        else delete state[key];
        write(STATE_KEY, state);
        refreshProgress(boxes);
        send("checklist_item_toggled", {
          checklist: box.dataset.checklist || "",
          item: box.dataset.item || "",
          checked: !!box.checked
        });
      });
    })(boxes[b]);
  }
  if (boxes.length) refreshProgress(boxes);

  // --------------------------------------------------------- EV-03 comparison_started
  var form = document.querySelector("[data-compare-form]");
  if (form) {
    var rows = Array.prototype.slice.call(document.querySelectorAll("[data-compare-row]"));
    var selects = form.querySelectorAll("select");

    function apply() {
      var picks = [];
      for (var s = 0; s < selects.length; s++) if (selects[s].value) picks.push(selects[s].value);
      var shown = 0;
      rows.forEach(function (tr) {
        var have = (tr.getAttribute("data-products") || "").split(/\s+/);
        var ok = !picks.length || picks.every(function (p) { return have.indexOf(p) !== -1; });
        tr.hidden = !ok;
        if (ok) shown++;
      });
      var note = form.parentNode.querySelector("[data-compare-count]");
      if (note) note.textContent = picks.length
        ? shown + " row" + (shown === 1 ? "" : "s") + " match " + picks.join(" + ") + "."
        : "";
      if (picks.length === 2) {
        send("comparison_started", { product_ids: picks, cluster: form.dataset.cluster || "" });
      }
    }

    for (var s = 0; s < selects.length; s++) selects[s].addEventListener("change", apply);
    apply();
  }

  // ------------------------------------------------------- EV-05 email_signup_submitted
  var signup = document.querySelector("[data-signup]");
  if (signup) {
    signup.addEventListener("submit", function (ev) {
      ev.preventDefault(); // static hosting cannot store an address; say so instead of pretending
      var enabled = signup.dataset.captureEnabled === "1";
      var out = signup.parentNode.querySelector("[data-signup-outcome]");
      if (out) {
        out.hidden = false;
        out.textContent = enabled
          ? "Submitted. This build expects a capture endpoint to be configured; check the metrics page to confirm it accepted the address."
          : "Nothing was sent and nothing was stored: reader capture is not enabled on this deployment. The decision to enable it is S-10 on the suggestions board.";
      }
      send("email_signup_submitted", { capture_enabled: !!enabled, outcome: enabled ? "queued" : "disabled-noop" });
    });
  }

  // --------------------------------------------------------- queue hand-off on enable
  // If an operator later sets an endpoint, the queued local history is delivered once and cleared.
  if (COLLECTING && !OPTED_OUT) {
    var backlog = read(QUEUE_KEY);
    if (backlog && backlog.length) {
      var i2 = 0;
      (function flush() {
        if (i2 >= backlog.length) {
          try { localStorage.removeItem(QUEUE_KEY); } catch (e) {}
          return;
        }
        var item = backlog[i2++];
        var blob = new Blob([JSON.stringify(item)], { type: "application/json" });
        fetch(ENDPOINT + "/e", { method: "POST", body: blob, credentials: "omit", headers: { "Content-Type": "application/json" } })
          .then(flush)
          .catch(flush);
      })();
    }
  }

  body.setAttribute("data-cw-ready", COLLECTING && !OPTED_OUT ? "collecting" : "local-only");
})();
