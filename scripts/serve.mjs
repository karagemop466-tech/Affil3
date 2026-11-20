#!/usr/bin/env node
/*
 * Preview server for local review. It serves docs/ under the same path prefix GitHub Pages uses
 * (/Affil3), because every generated link is absolute-from-the-root with that prefix - so what you
 * see here is byte-for-byte what Pages will serve, with no "works locally, broken in production".
 *
 *   node scripts/serve.mjs --port 8080
 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import url from "node:url";

const HERE = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), "..");
const DOCROOT = path.join(HERE, "docs");
const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf("--" + k); return i === -1 ? d : argv[i + 1]; };
const PORT = Number(arg("port", 8080));
const PREFIX = arg("prefix", "/Affil3");

const TYPES = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".json": "application/json", ".xml": "application/xml", ".svg": "image/svg+xml", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".txt": "text/plain; charset=utf-8", ".md": "text/markdown; charset=utf-8", ".ico": "image/x-icon" };

http.createServer((req, res) => {
  let p = decodeURIComponent(new URL(req.url, "http://x").pathname);
  if (PREFIX && p === PREFIX) { res.writeHead(302, { Location: PREFIX + "/" }); return res.end(); }
  if (PREFIX && p.startsWith(PREFIX)) p = p.slice(PREFIX.length) || "/";
  let file = path.join(DOCROOT, p === "/" ? "index.html" : p);
  if (!file.startsWith(DOCROOT)) { res.writeHead(403); return res.end("no\n"); }
  try {
    if (fs.statSync(file).isDirectory()) file = path.join(file, "index.html");
    const body = fs.readFileSync(file);
    res.writeHead(200, { "Content-Type": TYPES[path.extname(file)] || "application/octet-stream", "Cache-Control": "no-store" });
    res.end(body);
  } catch {
    const withHtml = file + ".html";
    try {
      const body = fs.readFileSync(withHtml);
      res.writeHead(200, { "Content-Type": TYPES[".html"] });
      return res.end(body);
    } catch {
      try { res.writeHead(404, { "Content-Type": TYPES[".html"] }); res.end(fs.readFileSync(path.join(DOCROOT, "404.html"))); }
      catch { res.writeHead(404); res.end("not found\n"); }
    }
  }
}).listen(PORT, "0.0.0.0", () => console.log(`preview: http://0.0.0.0:${PORT}${PREFIX}/  (serving ${path.relative(HERE, DOCROOT)}/)`));
