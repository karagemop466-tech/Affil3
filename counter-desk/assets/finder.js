/*
 * Counter-Space & Fit Finder.
 *
 * Pure client-side arithmetic over dimension values that are already published on
 * each product page and cited to a manufacturer source. No new data is invented:
 * the data comes from a JSON island embedded in the page by the build. If the
 * island is missing the tool simply renders nothing, and the static table of
 * published dimensions remains the fallback.
 */
(function () {
  'use strict';
  var island = document.getElementById('fit-data');
  if (!island) return;

  var products;
  try { products = JSON.parse(island.textContent); } catch (e) { return; }
  if (!Array.isArray(products) || !products.length) return;

  var form = document.getElementById('fit-form');
  var out = document.getElementById('fit-out');
  if (!form || !out) return;

  var inputs = {
    depth: form.querySelector('#fit-depth'),
    width: form.querySelector('#fit-width'),
    height: form.querySelector('#fit-height')
  };

  var clearance = 2; // inches of breathing room around the box, decided here and stated on the page

  function inches(el) {
    var v = parseFloat(el && el.value);
    return isFinite(v) && v > 0 ? v : null;
  }

  function render() {
    var want = { depth: inches(inputs.depth), width: inches(inputs.width), height: inches(inputs.height) };
    if (!want.depth && !want.width && !want.height) {
      out.innerHTML = '<p class="fit-empty">Enter at least one measurement above. The tool compares it with the manufacturer figures for each appliance and never rounds in your favour.</p>';
      return;
    }

    var rows = products.filter(function (p) {
      return p.depth_in || p.width_in || p.height_in;
    }).map(function (p) {
      var checks = [];
      var fails = 0;
      var unknowns = [];

      ['depth', 'width', 'height'].forEach(function (axis) {
        var have = want[axis];
        var need = p[axis + '_in'];
        if (!have) return;
        if (!need) { unknowns.push(axis); return; }
        var total = need + clearance;
        var ok = have >= total;
        if (!ok) fails++;
        checks.push({
          ok: ok,
          text: (ok ? 'Fits' : 'Too ' + (axis === 'height' ? 'tall' : 'tight') + ' on ' + axis) +
            ': ' + need + ' in + ' + clearance + ' in clearance = ' + total + ' in needed, you have ' + have + ' in'
        });
      });

      return { p: p, fails: fails, checks: checks, unknowns: unknowns };
    });

    rows.sort(function (a, b) {
      if (a.fails !== b.fails) return a.fails - b.fails;
      return a.p.name.localeCompare(b.p.name);
    });

    out.innerHTML = '<div class="fit-result">' + rows.map(function (r) {
      var verdict = r.fails === 0 ? 'yes' : 'no';
      var label = r.fails === 0 ? 'Clears your space' : (r.fails === 1 ? 'One measurement short' : r.fails + ' measurements short');
      var why = r.checks.map(function (c) { return c.text; }).join(' · ');
      if (r.unknowns.length) {
        why += (why ? ' · ' : '') + 'No published ' + r.unknowns.join(' or ') + ' figure, so that axis was not checked (see the product page).';
      }
      return '<div class="fit-row ' + verdict + '">' +
        '<span class="name"><a href="' + r.p.url + '">' + r.p.name + '</a></span>' +
        '<span class="pill ' + (verdict === 'yes' ? 'good' : 'bad') + '">' + label + '</span>' +
        '<span class="why">' + why + '</span>' +
        '</div>';
    }).join('') + '</div>' +
      '<p class="fine" style="margin-top:12px">' + clearance + ' inches of clearance is added around every published dimension, because a machine that fits exactly has no room for a vent, a hand or a door. Dimensions are the manufacturers\' own figures, linked on each product page; where two official pages disagree, the larger figure is used.</p>';
  }

  form.addEventListener('submit', function (e) { e.preventDefault(); render(); });
  form.addEventListener('input', render);
  render();
})();
