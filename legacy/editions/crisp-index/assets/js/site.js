/* The Crisp Index — site behaviour (no cookies, no storage) */
(function () {
  "use strict";

  // Mobile nav
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".main-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // Reader capture: gated until captureEndpoint is configured (FLG-008).
  // Nothing is collected or transmitted while the endpoint is null.
  var captureForm = document.querySelector(".capture-form");
  if (captureForm) {
    captureForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var note = captureForm.parentElement.querySelector(".capture-note");
      var endpoint = (window.TCI_CONFIG || {}).captureEndpoint || null;
      var email = captureForm.querySelector("input[type=email]");
      if (!endpoint) {
        if (note) {
          note.textContent =
            "Reader capture opens with our first dispatch — no address is collected before then. " +
            "Status is tracked in the Suggestions & decisions queue.";
        }
        if (email) email.value = "";
        return;
      }
      fetch(endpoint, {
        method: "POST",
        keepalive: true,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email ? email.value : "" })
      }).then(function () {
        if (note) note.textContent = "Thanks — you're on the list.";
        if (email) email.value = "";
      }).catch(function () {
        if (note) note.textContent = "That did not go through — please try again shortly.";
      });
    });
  }
})();
