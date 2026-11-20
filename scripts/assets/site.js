// Table row filter. Each input filters the rows of the table with the matching id.
(function () {
  function bind(input) {
    var id = input.getAttribute('data-filter');
    var table = document.querySelector('table[data-table="' + id + '"]');
    if (!table) return;
    input.addEventListener('input', function () {
      var q = input.value.trim().toLowerCase();
      var rows = table.tBodies[0] ? table.tBodies[0].rows : [];
      for (var i = 0; i < rows.length; i++) {
        rows[i].style.display = !q || rows[i].textContent.toLowerCase().indexOf(q) !== -1 ? '' : 'none';
      }
    });
  }
  var inputs = document.querySelectorAll('input[data-filter]');
  for (var i = 0; i < inputs.length; i++) bind(inputs[i]);
})();
