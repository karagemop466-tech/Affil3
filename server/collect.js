#!/usr/bin/env node
/**
 * Crisp & Counter — self-hosted, privacy-preserving event collector.
 * Zero dependencies. Node 18+.
 *
 * POST /collect   body: { e, p, t, path, s }   -> 204
 * GET  /health                              -> 200
 *
 * Privacy: we do not read or store IP addresses, user agents, cookies or any
 * query string. The session token `s` is generated client-side, never shared
 * with third parties, and rotates whenever browser storage is cleared.
 *
 * Deploy: `PORT=8787 node server/collect.js` behind any HTTPS reverse proxy,
 * then set <meta name="ck-endpoint" content="https://your.host/collect"> in
 * the site (one line in scripts/build_site.py) and rebuild.
 */
"use strict";
const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT || 8787;
const OUT = process.env.CK_LOG || path.join(__dirname, "events.jsonl");
const ALLOWED = new Set(["page_view", "product_impression", "outbound_click", "guide_read", "feedback_submit"]);

const server = http.createServer((req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  if (req.method === "OPTIONS") return res.writeHead(204).end();
  if (req.method === "GET" && req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    return res.end(JSON.stringify({ ok: true, events: ALLOWED.size, privacy: "no-ip-no-ua-no-cookies" }));
  }
  if (req.method === "POST" && req.url === "/collect") {
    let body = "";
    req.on("data", (c) => { body += c; if (body.length > 4096) req.destroy(); });
    req.on("end", () => {
      let ev;
      try { ev = JSON.parse(body); } catch (e) { return res.writeHead(400).end(); }
      if (!ALLOWED.has(ev.e)) return res.writeHead(400).end();
      const record = {
        e: ev.e,
        p: ev.p && typeof ev.p === "object" ? ev.p : {},
        t: typeof ev.t === "string" ? ev.t : new Date().toISOString(),
        path: String(ev.path || "").slice(0, 200),
        s: String(ev.s || "").slice(0, 40),
      };
      fs.appendFile(OUT, JSON.stringify(record) + "\n", () => {
        res.writeHead(204).end();
      });
    });
    return;
  }
  res.writeHead(404).end();
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`ck collector listening on :${PORT} -> ${OUT}`);
});
