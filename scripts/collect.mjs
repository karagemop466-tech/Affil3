#!/usr/bin/env node
/*
 * ShopNow 047 - self-hosted event collector for the five defined events.
 *
 * Why this exists: GitHub Pages serves static files, so a click counter has nowhere to land.
 * Rather than wire the site to a third-party analytics vendor (which would drag a consent
 * policy and a cross-site script onto a page whose whole brand is checkability), the collector
 * is 100 lines you can read, on a box you own, writing append-only NDJSON.
 *
 *   node scripts/collect.mjs --port 8788 --out data/events.ndjson
 *
 * The site points at it only when register/site.json carries a collector_url; with none set,
 * nothing is transmitted and events stay in the reader's own tab.
 *
 * Deliberate omissions: no IP logging (the access log the platform keeps is a separate choice),
 * no user-agent parsing, no cookies, no per-user identity, no dashboard.
 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import url from "node:url";
import zlib from "node:zlib";

const HERE = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), "..");
const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf("--" + k); return i === -1 ? d : argv[i + 1]; };
const PORT = Number(arg("port", 8788));
const OUT = path.resolve(HERE, arg("out", "data/events.ndjson"));
const ALLOW = arg("origin", "*");
const MAX_BYTES = 4096;
const RATE_PER_MIN = Number(arg("rate", 120));

const KNOWN = new Set(["page_view", "guide_view", "outbound_click", "intent_confirm", "register_gap_view"]);

fs.mkdirSync(path.dirname(OUT), { recursive: true });

/* tiny fixed-window limiter: a static site's collector is a public endpoint, and public
   endpoints get sprayed. Over-limit is a 429, silently, because a rejected event is a
   better outcome than a disk filled by someone else. */
const hits = new Map();
function limited(ip) {
  const min = Math.floor(Date.now() / 60000);
  const cur = hits.get(ip) || { min, n: 0 };
  if (cur.min !== min) { cur.min = min; cur.n = 0; }
  cur.n++; hits.set(ip, cur);
  if (hits.size > 5000) hits.clear();
  return cur.n > RATE_PER_MIN;
}

const cors = (res) => {
  res.setHeader("Access-Control-Allow-Origin", ALLOW);
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS");
  res.setHeader("Vary", "Origin");
};

const server = http.createServer((req, res) => {
  const u = new URL(req.url, "http://localhost");
  cors(res);
  if (req.method === "OPTIONS") { res.writeHead(204); return res.end(); }

  if (u.pathname === "/health") { res.writeHead(200, { "Content-Type": "text/plain" }); return res.end("ok\n"); }

  if (u.pathname === "/summary") {
    const day = (u.searchParams.get("day") || new Date().toISOString().slice(0, 10));
    const counts = {};
    let total = 0;
    try {
      for (const line of fs.readFileSync(OUT, "utf8").split("\n")) {
        if (!line.trim()) continue;
        let e; try { e = JSON.parse(line); } catch { continue; }
        if (!String(e.t || "").startsWith(day)) continue;
        counts[e.e] = (counts[e.e] || 0) + 1; total++;
      }
    } catch (e) { /* no file yet = zero day */ }
    res.writeHead(200, { "Content-Type": "application/json", "Cache-Control": "no-store" });
    return res.end(JSON.stringify({ day, total, counts, ledger_note: "Counts are of events received, not of readers or of purchases. Earnings appear only in register/ledger.json, from Amazon's own reports." }));
  }

  if (u.pathname === "/export") {
    if (!fs.existsSync(OUT)) { res.writeHead(404); return res.end("no events yet\n"); }
    res.writeHead(200, { "Content-Type": "application/x-ndjson", "Content-Disposition": "attachment; filename=events.ndjson" });
    return fs.createReadStream(OUT).pipe(res);
  }

  if (u.pathname !== "/event" || req.method !== "POST") { res.writeHead(404, { "Content-Type": "text/plain" }); return res.end("not found\n"); }

  const gz = /gzip/i.test(req.headers["content-encoding"] || "");
  const chunks = []; let n = 0; let aborted = false;
  req.on("data", (c) => { if (aborted) return; n += c.length; if (n > MAX_BYTES) { aborted = true; res.writeHead(413); res.end("too large\n"); req.destroy(); return; } chunks.push(c); });
  req.on("end", () => {
    if (aborted) return;
    let body;
    try { body = gz ? zlib.gunzipSync(Buffer.concat(chunks)).toString("utf8") : Buffer.concat(chunks).toString("utf8"); }
    catch { res.writeHead(400); return res.end("bad encoding\n"); }
    let e;
    try { e = JSON.parse(body); } catch { res.writeHead(400); return res.end("bad json\n"); }
    if (!KNOWN.has(e.e)) { res.writeHead(400); return res.end("unknown event\n"); }
    if (limited(req.socket.remoteAddress || "unknown")) { res.writeHead(429); return res.end("slow down\n"); }
    const rec = {
      e: e.e,
      t: typeof e.t === "string" && e.t.length < 40 ? e.t : new Date().toISOString(),
      p: typeof e.p === "string" ? e.p.slice(0, 200) : null,
      s: typeof e.s === "string" ? e.s.slice(0, 64) : null,
      received_at: new Date().toISOString()
    };
    for (const k of ["product_id", "asin_observed", "placement", "link_format", "guide_slug", "cluster", "flag_id", "field_names", "slug"]) {
      if (e[k] != null && String(e[k]).length < 200) rec[k] = String(e[k]);
    }
    fs.appendFile(OUT, JSON.stringify(rec) + "\n", (err) => {
      if (err) { res.writeHead(500); return res.end("write failed\n"); }
      res.writeHead(204); res.end();
    });
  });
  req.on("error", () => {});
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`collector: http://0.0.0.0:${PORT}/event  ->  ${path.relative(HERE, OUT)}`);
  console.log(`           GET /summary?day=YYYY-MM-DD · GET /export · GET /health`);
  console.log(`           retention: append-only NDJSON, no deletion job, no PII fields accepted.`);
});
