/*
 * Counter Desk — privacy-preserving outbound click counter.
 *
 * Five events, no cookies, no local storage, no identifiers, no IP stored by the
 * collector. If no endpoint is configured, the script does nothing at all: it
 * fails open and the page never waits on the network.
 *
 * The outbound link is NOT routed through this script. The browser follows the
 * Amazon link directly, because Program Policies 6(v) treats a redirecting link
 * as cloaking and 6(w) bars link shortening that obscures the Amazon destination.
 */
(function () {
  'use strict';

  var ALLOWED = {
    page_view: ['page_path', 'page_type'],
    category_view: ['category'],
    product_view: ['product_id', 'category'],
    outbound_click: ['product_id', 'placement'],
    guide_read_75: ['guide_slug']
  };

  var meta = document.querySelector('meta[name="analytics-endpoint"]');
  var endpoint = meta && meta.getAttribute('content') ? meta.getAttribute('content').trim() : '';
  if (!endpoint || !/^https:\/\//.test(endpoint)) return; // inactive by design

  var fired = {};

  function send(event, props) {
    if (!Object.prototype.hasOwnProperty.call(ALLOWED, event)) return;
    var clean = {};
    var allowed = ALLOWED[event];
    for (var i = 0; i < allowed.length; i++) {
      var k = allowed[i];
      if (props && typeof props[k] === 'string' && props[k].length <= 120) clean[k] = props[k];
    }
    var body = JSON.stringify({ event: event, properties: clean, ts: new Date().toISOString() });
    try {
      if (navigator.sendBeacon) {
        navigator.sendBeacon(endpoint, new Blob([body], { type: 'application/json' }));
      } else {
        fetch(endpoint, { method: 'POST', body: body, headers: { 'Content-Type': 'application/json' }, keepalive: true });
      }
    } catch (e) {
      /* measurement must never break a page */
    }
  }

  function body() {
    return document.body ? document.body.dataset || {} : {};
  }

  var d = body();

  // 1. page_view
  if (!fired.page_view) { fired.page_view = true; send('page_view', { page_path: location.pathname, page_type: d.page || '' }); }

  // 2. category_view
  if (d.category) send('category_view', { category: d.category });

  // 3. product_view
  if (d.productView) send('product_view', { product_id: d.productView, category: d.category || '' });

  // 4. outbound_click — recorded, then the browser follows the link untouched.
  document.addEventListener('click', function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest('a[data-outbound]') : null;
    if (!a) return;
    send('outbound_click', { product_id: a.getAttribute('data-product') || '', placement: a.getAttribute('data-placement') || '' });
  }, { capture: true });

  // 5. guide_read_75 — once per guide, when 75% of the article has been passed.
  if (d.guide) {
    var article = document.querySelector('article.article') || document.querySelector('main');
    if (article) {
      var onScroll = function () {
        if (fired.guide_read_75) return;
        var r = article.getBoundingClientRect();
        var passed = (window.innerHeight - r.top) / r.height;
        if (passed >= 0.75) {
          fired.guide_read_75 = true;
          send('guide_read_75', { guide_slug: d.guide });
          window.removeEventListener('scroll', onScroll, { passive: true });
        }
      };
      window.addEventListener('scroll', onScroll, { passive: true });
      onScroll();
    }
  }
})();
