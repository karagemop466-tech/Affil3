/* ShopNow Kitchen Edit — site configuration (single source of truth for client JS) */
window.SHOPNOW_CONFIG = {
  siteName: "ShopNow Kitchen Edit",
  trackingId: "shopnow047c-20",          // supplied in project brief; enrollment unverified (FLG-001)
  baseUrl: "https://karagemop466-tech.github.io/Affil3/",
  // Self-hosted analytics endpoint. EMPTY = events queue in the visitor's browser only
  // and never leave it. Decision pending: SG-08 / FLG-002.
  analyticsEndpoint: "",
  eventsQueueKey: "shopnow_events_v1",
  eventsQueueCap: 500,
  // Kill switch from data/products.json (require_verified_links). Flip ONLY in the data file;
  // this copy is informational for client tools.
  requireVerifiedLinks: false
};
