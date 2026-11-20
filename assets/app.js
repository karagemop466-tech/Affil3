/* Counter Notes measurement: five event types, no cookies, identifiers, IP storage, or cross-device profile.
   Until a reviewed first-party endpoint is deployed, events stay in this browser's localStorage only.
   They are not site-wide analytics and must not be described as such. */
(() => {
  'use strict';
  const EVENT_TYPES = new Set(['page_view', 'guide_open', 'outbound_click', 'suggestion_vote', 'reader_capture']);
  const STORE = 'counter-notes-events-v1';
  const ENDPOINT = window.COUNTER_NOTES_ANALYTICS_ENDPOINT || ''; // Intentionally unset: GitHub Pages does not run an API.
  const page = document.body.dataset.page || location.pathname;

  try {
    const votes = JSON.parse(localStorage.getItem('counter-notes-suggestions-v1') || '{}');
    document.querySelectorAll('[data-suggestion]').forEach(card => card.querySelectorAll('[data-vote]').forEach(button => {
      button.setAttribute('aria-pressed', String(votes[card.dataset.suggestion] === button.dataset.vote));
    }));
    const interests = new Set(JSON.parse(localStorage.getItem('counter-notes-reader-capture-v1') || '[]'));
    document.querySelectorAll('[data-capture]').forEach(button => button.setAttribute('aria-pressed', String(interests.has(button.dataset.capture))));
  } catch (_) { /* local preference restore is optional */ }

  function record(type, detail = {}) {
    if (!EVENT_TYPES.has(type)) return;
    const event = {
      event: type,
      at: new Date().toISOString(),
      page: String(page).slice(0, 120),
      detail: Object.fromEntries(Object.entries(detail).filter(([, value]) => typeof value === 'string').map(([key, value]) => [key, value.slice(0, 100)]))
    };
    try {
      const old = JSON.parse(localStorage.getItem(STORE) || '[]');
      const events = Array.isArray(old) ? old.slice(-499) : [];
      events.push(event);
      localStorage.setItem(STORE, JSON.stringify(events));
    } catch (_) { /* private browsing/storage restrictions should never break page reading */ }
    if (ENDPOINT) {
      try {
        fetch(ENDPOINT, {
          method: 'POST',
          mode: 'cors',
          credentials: 'omit',
          cache: 'no-store',
          keepalive: true,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(event)
        }).catch(() => {});
      } catch (_) { /* analytics is nonessential */ }
    }
  }

  record('page_view');
  document.querySelectorAll('a[href^="guides/"]').forEach(link => link.addEventListener('click', () => record('guide_open', { guide: link.getAttribute('href') })));
  document.querySelectorAll('a[data-outbound="true"]').forEach(link => {
    link.rel = 'sponsored noopener noreferrer';
    link.addEventListener('click', () => record('outbound_click', { destination: link.hostname || 'unknown' }));
  });
  document.querySelectorAll('[data-capture]').forEach(button => button.addEventListener('click', () => {
    const topic = button.dataset.capture;
    const selected = button.getAttribute('aria-pressed') === 'true';
    button.setAttribute('aria-pressed', String(!selected));
    try {
      const interests = new Set(JSON.parse(localStorage.getItem('counter-notes-reader-capture-v1') || '[]'));
      if (selected) interests.delete(topic); else interests.add(topic);
      localStorage.setItem('counter-notes-reader-capture-v1', JSON.stringify([...interests]));
    } catch (_) { /* no-op */ }
    record('reader_capture', { topic, choice: selected ? 'removed' : 'selected' });
    const status = document.querySelector('.capture-status');
    if (status) status.textContent = selected ? 'Interest removed from this device.' : `Noted: ${topic.replaceAll('-', ' ')}. Saved on this device only.`;
  }));

  document.querySelectorAll('[data-suggestion]').forEach(card => {
    card.querySelectorAll('[data-vote]').forEach(button => button.addEventListener('click', () => {
      const suggestion = card.dataset.suggestion;
      const vote = button.dataset.vote;
      card.querySelectorAll('[data-vote]').forEach(peer => peer.setAttribute('aria-pressed', String(peer === button && button.getAttribute('aria-pressed') !== 'true')));
      const active = button.getAttribute('aria-pressed') === 'true';
      try {
        const votes = JSON.parse(localStorage.getItem('counter-notes-suggestions-v1') || '{}');
        if (active) votes[suggestion] = vote;
        else delete votes[suggestion];
        localStorage.setItem('counter-notes-suggestions-v1', JSON.stringify(votes));
      } catch (_) { /* no-op */ }
      record('suggestion_vote', { suggestion, choice: active ? vote : 'cleared' });
      const output = document.getElementById('decision-output');
      if (output) output.textContent = 'Your selection is saved in this browser only. It has not been sent to the editorial team.';
    }));
  });

  const showVotes = document.querySelector('[data-show-decisions]');
  if (showVotes) showVotes.addEventListener('click', () => {
    let votes = {};
    try { votes = JSON.parse(localStorage.getItem('counter-notes-suggestions-v1') || '{}'); } catch (_) { /* ignore */ }
    const labels = Object.entries(votes).map(([id, choice]) => {
      const card = [...document.querySelectorAll('[data-suggestion]')].find(item => item.dataset.suggestion === id);
      const title = card?.querySelector('h2');
      return title ? `${title.textContent} — ${choice}` : '';
    }).filter(Boolean);
    const output = document.getElementById('decision-output');
    if (output) output.textContent = labels.length ? `Your local shortlist: ${labels.join('; ')}. This is a private, device-local note, not a team submission.` : 'No suggestions selected yet. Choose “Prioritize” or “Not yet” on any card.';
  });
})();
