(() => {
  const status = document.querySelector('[data-measure-status]');
  const summary = document.querySelector('[data-measure-summary]');
  const root = document.querySelector('meta[name="site-root"]')?.content || './';
  if (!status || !summary) return;

  const runtimeUrl = new URL(`${root}data/analytics-runtime.json`, window.location.href);
  fetch(runtimeUrl, { credentials: 'omit', cache: 'no-store', referrerPolicy: 'no-referrer' })
    .then((response) => response.ok ? response.json() : null)
    .then((config) => {
      if (!config?.enabled || !config.summaryEndpoint) {
        status.textContent = 'Endpoint not connected; this static page is not collecting site events.';
        return null;
      }
      return fetch(new URL(config.summaryEndpoint, window.location.href), { credentials: 'omit', cache: 'no-store', referrerPolicy: 'no-referrer' });
    })
    .then((response) => response?.ok ? response.json() : null)
    .then((data) => {
      if (!data) return;
      status.textContent = 'Self-hosted endpoint connected. The figures below are aggregate site events only, not Amazon orders.';
      const rows = Object.entries(data.events || {});
      summary.replaceChildren();
      if (rows.length === 0) {
        const item = document.createElement('p');
        item.textContent = 'No aggregate events have been recorded yet.';
        summary.append(item);
        return;
      }
      for (const [name, value] of rows) {
        const item = document.createElement('p');
        item.textContent = `${name}: ${Number(value) || 0}`;
        summary.append(item);
      }
    })
    .catch(() => {
      status.textContent = 'Endpoint not connected; this static page is not collecting site events.';
    });
})();
