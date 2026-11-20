/**
 * The Crisp Index — privacy-preserving click counter (Cloudflare Worker).
 * Accepts POST /e with {event, path, ts, ref?}; stores aggregates only.
 * No IP, no user agent, no cookies. See README.md for the privacy contract.
 */
const EVENTS = ["page_view", "outbound_click", "guide_read", "newsletter_signup", "feedback_click"];

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (request.method === "POST" && url.pathname === "/e") {
      let body;
      try { body = await request.json(); } catch (_) {
        return new Response("bad json", { status: 400 });
      }
      const event = String(body.event || "");
      if (!EVENTS.includes(event)) return new Response("unknown event", { status: 400 });
      const path = String(body.path || "").slice(0, 200);
      const ref = body.ref ? String(body.ref).slice(0, 120) : undefined;

      // Aggregate counter only — attach a KV/D1 binding in wrangler.toml to persist.
      const key = `tci:${event}:${path}`;
      if (globalThis.TCI_KV) {
        const n = parseInt((await globalThis.TCI_KV.get(key)) || "0", 10);
        await globalThis.TCI_KV.put(key, String(n + 1));
        if (ref) {
          const rk = `tci:${event}:${path}:ref:${ref}`;
          const rn = parseInt((await globalThis.TCI_KV.get(rk)) || "0", 10);
          await globalThis.TCI_KV.put(rk, String(rn + 1));
        }
      }
      return new Response("ok", {
        status: 204,
        headers: {
          "access-control-allow-origin": "*",
          "cache-control": "no-store"
        }
      });
    }
    if (url.pathname === "/stats") {
      return new Response(JSON.stringify({ status: "wire TCI_KV to list keys" }), {
        headers: { "content-type": "application/json" }
      });
    }
    return new Response("tci-count", { status: 200 });
  }
};
