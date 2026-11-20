(() => {
  const page = document.body?.dataset.page || '';
  const pageType = document.body?.dataset.pageType || '';
  const root = document.querySelector('meta[name="site-root"]')?.content || './';
  const runtimeUrl = new URL(`${root}data/analytics-runtime.json`, window.location.href);
  const allowed = new Set(['page_view', 'guide_open', 'site_search', 'outbound_click', 'reader_signup']);
  let runtime = null;

  const send = (eventName, extra = {}) => {
    if (!runtime?.enabled || !runtime.endpoint || !allowed.has(eventName)) return;
    const payload = { event: eventName, page };
    if (eventName === 'site_search' && Number.isFinite(extra.result_count)) {
      payload.result_count = Math.max(0, Math.min(1000, Math.floor(extra.result_count)));
    }
    if (eventName === 'outbound_click' && typeof extra.product_id === 'string') {
      payload.product_id = extra.product_id.slice(0, 64);
    }
    if (eventName === 'reader_signup') {
      if (extra.confirmed !== true) return;
      payload.confirmed = true;
    }

    fetch(new URL(runtime.endpoint, window.location.href), {
      method: 'POST',
      mode: 'same-origin',
      credentials: 'omit',
      cache: 'no-store',
      keepalive: true,
      referrerPolicy: 'no-referrer',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).catch(() => {});
  };

  const ready = fetch(runtimeUrl, { credentials: 'omit', cache: 'no-store', referrerPolicy: 'no-referrer' })
    .then((response) => response.ok ? response.json() : null)
    .then((config) => {
      runtime = config && config.enabled === true ? config : null;
      if (!runtime) return false;
      send('page_view');
      if (pageType === 'article') send('guide_open');
      return true;
    })
    .catch(() => false);

  document.addEventListener('click', (event) => {
    const anchor = event.target.closest?.('a[data-product-link]');
    if (!anchor) return;
    send('outbound_click', { product_id: anchor.dataset.productLink });
  }, { capture: true });

  window.countertopAnalytics = { track: send, ready };
})();
