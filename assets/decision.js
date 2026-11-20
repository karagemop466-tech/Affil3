// Decision worksheet for the suggestions board. Runs entirely in the reader's browser:
// it never sends anything, never stores anything, and never changes the site.
// It only turns the reader's own choices into a plain-text draft they can copy.
(function () {
  var board = document.querySelector('[data-decision-board]');
  if (!board) return;

  var cards = Array.prototype.slice.call(board.querySelectorAll('.choice-card'));
  if (!cards.length) return;

  // 1. Give each option a radio button, so a choice is explicit and single-select.
  cards.forEach(function (card) {
    var id = card.id || '';
    var list = card.querySelector('.opts');
    if (!list || !id) return;
    Array.prototype.slice.call(list.querySelectorAll('li')).forEach(function (li, i) {
      var opt = li.querySelector('strong');
      if (!opt) return;
      var key = opt.textContent.replace('.', '').trim();
      var input = document.createElement('input');
      input.type = 'radio';
      input.name = 'decision-' + id;
      input.value = key;
      input.className = 'decision-radio';
      input.setAttribute('aria-label', id + ' option ' + key);
      li.insertBefore(input, opt);
    });
  });

  // 2. Build the draft from the current selection.
  function draft() {
    var lines = ['ShopNow Kitchen — decision draft', ''];
    var picked = 0;
    cards.forEach(function (card) {
      var id = card.id || '';
      var chosen = card.querySelector('input[name="decision-' + id + '"]:checked');
      var topic = card.querySelector('.kicker');
      var topicText = topic ? topic.textContent.replace(/^\S+\s*·\s*/, '').trim() : id;
      if (!chosen) {
        lines.push('- ' + id + ' (' + topicText + '): no option chosen');
        return;
      }
      picked += 1;
      var li = chosen.closest('li');
      var text = li ? li.textContent.replace(/^\s*\S+\.\s*/, '').trim() : chosen.value;
      var tradeoff = li ? li.querySelector('.muted.small') : null;
      lines.push('- ' + id + ' (' + topicText + '): ' + chosen.value + ' — ' + text);
      if (tradeoff) lines.push('    tradeoff: ' + tradeoff.textContent.replace(/^Tradeoff:\s*/, '').trim());
    });
    lines.push('');
    lines.push(picked + ' of ' + cards.length + ' decisions chosen.');
    lines.push('This draft is a note, not an instruction: nothing is implemented automatically.');
    return lines.join('\n');
  }

  var out = board.querySelector('[data-decision-output]');
  var status = board.querySelector('[data-decision-status]');

  function refresh() {
    if (!out) return;
    out.value = draft();
    if (status) status.textContent = 'Updated from your selections above.';
  }

  board.addEventListener('change', refresh);

  // 3. Copy to clipboard when the reader wants it. Falls back to selecting the text.
  var copy = board.querySelector('[data-decision-copy]');
  if (copy) {
    copy.addEventListener('click', function () {
      if (!out) return;
      out.focus();
      out.select();
      var done = function () {
        if (status) status.textContent = 'Draft copied. Paste it wherever the decision is made.';
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(out.value).then(done, function () {
          if (status) status.textContent = 'Copy blocked by the browser — the text is selected, press Ctrl/Cmd+C.';
        });
      } else if (status) {
        status.textContent = 'Copy blocked by the browser — the text is selected, press Ctrl/Cmd+C.';
      }
    });
  }

  refresh();
})();
