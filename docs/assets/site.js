/* Highlight the active navigation link for the current page. */
(function () {
  "use strict";
  var path = location.pathname.split("/").filter(Boolean).pop() || "index.html";
  document.querySelectorAll(".nav-primary a").forEach(function (a) {
    var href = a.getAttribute("href");
    if (!href) return;
    var hrefPart = href.split("/").pop() || "index.html";
    if (hrefPart === path || (path === "index.html" && hrefPart === "index.html" && location.pathname.endsWith("/"))) {
      a.classList.add("active");
    }
  });
})();
