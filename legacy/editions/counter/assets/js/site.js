/* Crisp & Counter — small site behaviors. */
(function () {
  "use strict";
  // Reflect analytics activity in the console for first-party debugging only.
  document.addEventListener("ck:track", function (e) {
    if (window.console && console.debug) console.debug("[ck]", e.detail.name, e.detail.payload);
  });
})();
