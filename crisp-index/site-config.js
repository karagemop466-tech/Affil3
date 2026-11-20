/*
 * The Crisp Index — site configuration.
 *
 * GATED SLOTS (see Flagged for Review page):
 *  - analyticsEndpoint: deploy tools/analytics-endpoint/ (Cloudflare Worker or
 *    the Python reference server) and set its URL here to release the click
 *    counter. Currently null = dry-run, nothing is transmitted (FLG-006).
 *  - captureEndpoint: newsletter capture backend (FLG-008 / SUG-005).
 *  - searchConsoleToken: Google site verification token when the owner creates
 *    the property (FLG-007 / SG-29). Leave null; the template reads it only to
 *    document the slot.
 */
window.TCI_CONFIG = {
  analyticsEndpoint: null,
  captureEndpoint: null,
  searchConsoleToken: null
};
