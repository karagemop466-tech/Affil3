/* Affil3 — privacy-preserving measurement (frontend only).
   Five defined events (measurement plan — see /about.html):
   1. session_start   2. outbound_click   3. product_impression   4. guide_view   5. disclosure_impression
   No cookies. No personal data. Events are held in localStorage until they can be
   posted to the self-hosted endpoint at /analytics/collect. That endpoint is NOT
   operational on GitHub Pages (static hosting) — see flagged.html (FLG-004). */
(function () {
  var ENDPOINT = '/analytics/collect';
  var STORAGE_KEY = 'affil3_pending_events';
  var SESSION_KEY = 'affil3_session_id';

  function sessionId() {
    var id;
    try { id = localStorage.getItem(SESSION_KEY); } catch (e) { id = null; }
    if (!id) {
      id = (crypto && crypto.randomUUID) ? crypto.randomUUID() : Math.random().toString(36).slice(2) + Date.now().toString(36);
      try { localStorage.setItem(SESSION_KEY, id); } catch (e) {}
    }
    return id;
  }

  var queue = [];
  try { queue = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); } catch (e) { queue = []; }
  if (!Array.isArray(queue)) queue = [];

  function enqueue(event) {
    queue.push({ ts: new Date().toISOString(), sid: sessionId(), page: location.pathname, event: event.event, target: event.target || '', text: event.text || '', sponsored: !!event.sponsored });
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(queue)); } catch (e) {}
    flush();
  }

  function flush() {
    if (queue.length === 0) return;
    var payload = queue.splice(0);
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(queue)); } catch (e) {}
    var body = JSON.stringify({ events: payload });
    var sent = false;
    if (navigator && navigator.sendBeacon) {
      sent = navigator.sendBeacon(ENDPOINT, new Blob([body], { type: 'application/json' }));
    }
    if (!sent && fetch) {
      fetch(ENDPOINT, { method: 'POST', body: body, keepalive: true, credentials: 'omit', headers: { 'Content-Type': 'application/json' } })
        .catch(function () {
          // Endpoint not operational yet: put events back so they can be retried later.
          queue.unshift.apply(queue, payload);
          try { localStorage.setItem(STORAGE_KEY, JSON.stringify(queue)); } catch (e) {}
        });
    }
  }

  // 1. session_start on every page.
  enqueue({ event: 'session_start' });

  // 4. disclosure_impression — disclosure strip is present above the fold on every page.
  enqueue({ event: 'disclosure_impression' });

  // 4. guide_view on guide pages.
  if (document.body.classList.contains('guide-page')) {
    enqueue({ event: 'guide_view' });
  }

  // 2. outbound_click counter on every outbound link (marked rel="sponsored" where affiliate).
  document.addEventListener('click', function (e) {
    var link = e.target.closest && e.target.closest('a[href]');
    if (!link) return;
    var href = link.getAttribute('href');
    if (!href) return;
    var url;
    try { url = new URL(href, location.href); } catch (err) { return; }
    if (url.origin !== location.origin) {
      enqueue({ event: 'outbound_click', target: href, text: (link.textContent || '').trim().slice(0, 120), sponsored: (link.rel && link.rel.indexOf('sponsored') !== -1) });
      // Beacon/fire-and-forget: navigation proceeds without delay.
    }
  });

  // 3. product_impression is defined but not auto-fired: it requires a confirmed ASIN
  // (see product-intent confirmation record on /products.html). No values are inferred.
})();