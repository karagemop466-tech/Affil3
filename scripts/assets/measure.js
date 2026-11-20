// Privacy-preserving event hook.
// Sends nothing while ENDPOINT is empty (the current state: no endpoint is configured).
// When enabled it sends only: event name, page path, optional product id, timestamp.
// This code sets no cookies, no local storage identifiers, and no IP or user-agent field.
(function () {
  var ENDPOINT = ''; // Set by the owner once an endpoint exists (see Suggestions S-02).
  var EVENTS = ['page_view', 'product_view', 'guide_view', 'outbound_click', 'feed_click']; // proposed, not confirmed

  function send(name, extra) {
    if (!ENDPOINT || EVENTS.indexOf(name) === -1) return;
    var payload = { event: name, path: location.pathname, ts: Date.now() };
    if (extra && extra.product_id) payload.product_id = extra.product_id;
    try {
      if (navigator.sendBeacon) {
        navigator.sendBeacon(ENDPOINT, new Blob([JSON.stringify(payload)], { type: 'application/json' }));
      }
    } catch (e) { /* ignore: measurement must never break the page */ }
  }

  send('page_view');
  if (document.body.classList.contains('product')) send('product_view');
  if (document.body.classList.contains('guide')) send('guide_view');

  document.addEventListener('click', function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest('a') : null;
    if (!a) return;
    if (a.getAttribute('data-event') === 'outbound_click') {
      send('outbound_click', { product_id: a.getAttribute('data-product-id') });
    }
    var href = a.getAttribute('href') || '';
    if (href.indexOf('feed.xml') !== -1) send('feed_click');
  });
})();
