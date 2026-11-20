/* Countertop Journal: privacy-preserving measurement.
 * - Sends nothing unless the page declares an endpoint (meta[name=affil3-endpoint]).
 * - Honours Do Not Track and Global Privacy Control: when either is set, nothing is sent.
 * - Sets no cookies and writes nothing to browser storage. No identifiers.
 * - Payload: {e: event name, p: pathname (no query, no hash), t: product id or ''}.
 * - Five events only: page_view, disclosure_impression, product_impression, guide_view, outbound_click.
 */
(function () {
  'use strict';
  var meta = document.querySelector('meta[name="affil3-endpoint"]');
  var endpoint = meta ? meta.getAttribute('content') : '';
  if (!endpoint) { return; }
  if (navigator.doNotTrack === '1' || window.doNotTrack === '1' || navigator.globalPrivacyControl === true) { return; }

  var ALLOWED = { page_view: 1, disclosure_impression: 1, product_impression: 1, guide_view: 1, outbound_click: 1 };
  var path = location.pathname;

  function send(name, product) {
    if (!ALLOWED[name]) { return; }
    var body = JSON.stringify({ e: name, p: path, t: product || '' });
    try {
      if (navigator.sendBeacon && navigator.sendBeacon(endpoint, new Blob([body], { type: 'text/plain' }))) { return; }
    } catch (err) { /* fall through */ }
    try {
      fetch(endpoint, { method: 'POST', body: body, keepalive: true, mode: 'no-cors', credentials: 'omit',
                        headers: { 'Content-Type': 'text/plain' } });
    } catch (err) { /* measurement must never break the page */ }
  }

  send('page_view');
  if (document.body && document.body.classList.contains('guide-page')) { send('guide_view'); }

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && en.intersectionRatio >= 0.5) {
          var el = en.target;
          if (el.id === 'disclosure') { send('disclosure_impression'); }
          else if (el.getAttribute('data-product')) { send('product_impression', el.getAttribute('data-product')); }
          io.unobserve(el);
        }
      });
    }, { threshold: [0.5] });
    var d = document.getElementById('disclosure');
    if (d) { io.observe(d); }
    document.querySelectorAll('.pcard[data-product]').forEach(function (c) { io.observe(c); });
  }

  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[rel~="sponsored"]') : null;
    if (a) { send('outbound_click', a.getAttribute('data-product') || ''); }
  }, true);
})();
