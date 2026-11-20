(() => {
  const form = document.querySelector('[data-guide-search]');
  const list = document.querySelector('[data-guide-list]');
  const count = document.querySelector('[data-search-count]');
  const input = form?.querySelector('input[name="q"]');
  if (!form || !list || !count || !input) return;

  const cards = [...list.querySelectorAll('[data-search-card]')];
  const filter = () => {
    const query = input.value.trim().toLocaleLowerCase();
    let visible = 0;
    for (const card of cards) {
      const matches = !query || `${card.dataset.searchText || ''} ${card.textContent}`.toLocaleLowerCase().includes(query);
      card.hidden = !matches;
      if (matches) visible += 1;
    }
    count.textContent = query
      ? `${visible} ${visible === 1 ? 'guide' : 'guides'} shown. Search text stays in this browser.`
      : `${visible} guides in this first issue.`;
    return visible;
  };

  input.addEventListener('input', filter);
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const resultCount = filter();
    window.countertopAnalytics?.track('site_search', { result_count: resultCount });
  });
})();
