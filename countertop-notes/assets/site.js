(() => {
  const navDetails = document.querySelectorAll('.nav-details');
  document.addEventListener('click', (event) => {
    for (const details of navDetails) {
      if (!details.contains(event.target)) details.open = false;
    }
  });

  const form = document.querySelector('[data-path-choice]');
  if (!form) return;

  const key = 'countertop-notes:review-priority';
  const status = form.querySelector('[data-choice-status]');
  const radios = [...form.querySelectorAll('input[name="path"]')];
  const selectedTitle = () => form.querySelector('input[name="path"]:checked')?.closest('label')?.querySelector('strong')?.textContent.trim() || 'No path selected';

  try {
    const saved = localStorage.getItem(key);
    const savedRadio = radios.find((radio) => radio.value === saved);
    if (savedRadio) {
      savedRadio.checked = true;
      if (status) status.textContent = `Saved locally in this browser: ${selectedTitle()}`;
    }
  } catch {
    if (status) status.textContent = 'Browser storage is unavailable; you can still compare the options on this page.';
  }

  form.addEventListener('change', () => {
    if (status) status.textContent = `Selected for review: ${selectedTitle()}. Save to keep this preference on this browser.`;
  });

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const selected = form.querySelector('input[name="path"]:checked');
    if (!selected) {
      if (status) status.textContent = 'Choose a review priority first.';
      return;
    }
    try {
      localStorage.setItem(key, selected.value);
      if (status) status.textContent = `Saved locally in this browser: ${selectedTitle()}. No content or links were changed.`;
    } catch {
      if (status) status.textContent = 'This browser could not save the preference. No content or links were changed.';
    }
  });
})();
