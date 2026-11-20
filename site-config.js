// Static GitHub Pages deployment: collection stays disabled because Pages has no server-side API.
// When the static site and analytics/server.mjs are deployed together on a supported host,
// configure this through that host's build/deployment process; never put report tokens here.
window.COUNTER_NOTES_CONFIG = Object.freeze({
  analyticsEndpoint: "",
  analyticsCollection: false,
  reportImport: false
});
