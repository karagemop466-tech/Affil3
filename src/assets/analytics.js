/* Affil3 measurement (privacy-preserving). Sends five allowlisted events to the
 * endpoint in <meta name="analytics-endpoint">. If that is empty, nothing is sent.
 * No cookies, no local storage, no IP or user-agent stored by this script.
 * Browsers with Do Not Track enabled are not counted. Links are never redirected:
 * the click is recorded and the browser follows the link directly to Amazon. */
(function () {
  'use strict';
  var meta = document.querySelector('meta[name="analytics-endpoint"]');
  var endpoint = meta ? meta.getAttribute('content') : '';
  if (!endpoint) return;
  if (navigator.doNotTrack === '1' || window.doNotTrack === '1') return;

  var ALLOWED = { page_view: 1, category_view: 1, product_view: 1, outbound_click: 1, guide_read_75: 1 };
  var body = document.body;

  function referrerHost() {
    try {
      if (!document.referrer) return '';
      var h = new URL(document.referrer).hostname;
      return h === location.hostname ? '' : h;
    } catch (e) { return ''; }
  }

  function send(name, props) {
    if (!ALLOWED[name]) return;
    var payload = JSON.stringify({ event: name, props: props || {}, path: location.pathname });
    try {
      if (navigator.sendBeacon) {
        navigator.sendBeacon(endpoint, new Blob([payload], { type: 'application/json' }));
      } else {
        fetch(endpoint, { method: 'POST', body: payload, keepalive: true, headers: { 'content-type': 'application/json' } });
      }
    } catch (e) { /* measurement must never break the page */ }
  }

  // page_view, and category_view on category pages
  send('page_view', { referrer_host: referrerHost() });
  if (body.getAttribute('data-category')) send('category_view', { category: body.getAttribute('data-category') });

  // product_view: once per product shown on this page
  var seen = {};
  var views = document.querySelectorAll('[data-product-view]');
  for (var i = 0; i < views.length; i++) {
    var id = views[i].getAttribute('data-product-view');
    if (id && !seen[id]) { seen[id] = 1; send('product_view', { product_id: id }); }
  }

  // outbound_click: recorded on click; the link itself is not redirected
  document.addEventListener('click', function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest('a[data-outbound]') : null;
    if (!a) return;
    var dest = '';
    try { dest = new URL(a.href).hostname; } catch (e) { dest = ''; }
    send('outbound_click', { product_id: a.getAttribute('data-product') || '', destination_host: dest, placement: a.getAttribute('data-placement') || '' });
  }, true);

  // guide_read_75: once per guide page when the reader passes 75% of the page
  var guide = body.getAttribute('data-guide');
  if (guide) {
    var fired = false;
    window.addEventListener('scroll', function () {
      if (fired) return;
      var doc = document.documentElement;
      var max = (doc.scrollHeight - window.innerHeight);
      if (max <= 0 || (window.scrollY + window.innerHeight) / doc.scrollHeight >= 0.75) {
        fired = true;
        send('guide_read_75', { guide: guide });
      }
    }, { passive: true });
  }
})();
