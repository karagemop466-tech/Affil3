import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const siteRoot = path.join(projectRoot, 'countertop-notes');
const productsDoc = JSON.parse(await fs.readFile(path.join(projectRoot, 'site-src/data/products.json'), 'utf8'));
const manifest = JSON.parse(await fs.readFile(path.join(projectRoot, 'site-src/pages.json'), 'utf8'));
const allowedEvents = new Set(['page_view', 'guide_open', 'site_search', 'outbound_click', 'reader_signup']);
const allowedProductIds = new Set(productsDoc.products.map((product) => product.id));
const allowedPages = new Set(manifest.pages.map((page) => page.path));
const storePath = path.resolve(process.env.ANALYTICS_STORE || path.join(projectRoot, '.local/analytics.json'));
const host = process.env.HOST || '0.0.0.0';
const port = Number(process.env.PORT || 4173);
const retentionDays = Math.min(365, Math.max(1, Number(process.env.ANALYTICS_RETENTION_DAYS || 90)));
// Static Pages and the default preview stay off. Enable only an explicitly configured, separately hosted API.
const analyticsEnabled = process.env.ANALYTICS_ENABLED === 'true';
const allowedOrigins = new Set((process.env.ANALYTICS_ALLOWED_ORIGINS || '')
  .split(',')
  .map((origin) => origin.trim())
  .filter(Boolean)
  .map((origin) => {
    const parsed = new URL(origin);
    if (!['http:', 'https:'].includes(parsed.protocol)) throw new Error('ANALYTICS_ALLOWED_ORIGINS must use HTTP(S) origins.');
    return parsed.origin;
  }));
const maxBodyBytes = 4096;
const maxRequestsPerMinute = 120;
const rateBuckets = new Map();
let writeQueue = Promise.resolve();

const mimeTypes = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.xml': 'application/xml; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
  '.ico': 'image/x-icon'
};

function securityHeaders(res) {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('Referrer-Policy', 'no-referrer');
  res.setHeader('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
  res.setHeader('Cross-Origin-Resource-Policy', 'same-origin');
  res.setHeader('Content-Security-Policy', "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'; object-src 'none'");
}

function jsonResponse(res, status, value) {
  securityHeaders(res);
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff'
  });
  res.end(JSON.stringify(value));
}

function sameOriginRequest(req) {
  const fetchSite = req.headers['sec-fetch-site'];
  if (fetchSite && fetchSite !== 'same-origin' && fetchSite !== 'none') return false;
  const originHeader = req.headers.origin;
  const requestHost = req.headers.host;
  if (!originHeader || !requestHost) return false;
  try {
    const origin = new URL(originHeader);
    if (!['http:', 'https:'].includes(origin.protocol)) return false;
    const scheme = req.socket.encrypted ? 'https:' : 'http:';
    const requestOrigin = new URL(`${scheme}//${requestHost}`).origin;
    // Reverse proxies must be configured with their exact public origin; arbitrary HTTPS origins are not trusted.
    return origin.origin === requestOrigin || allowedOrigins.has(origin.origin);
  } catch {
    return false;
  }
}

function allowRate(req) {
  const now = Date.now();
  const key = req.socket.remoteAddress || 'unknown';
  const current = rateBuckets.get(key);
  if (!current || now - current.startedAt > 60_000) {
    rateBuckets.set(key, { startedAt: now, count: 1 });
    return true;
  }
  current.count += 1;
  return current.count <= maxRequestsPerMinute;
}

function utcDay() {
  return new Date().toISOString().slice(0, 10);
}

function parseEvent(payload) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) return null;
  if (!allowedEvents.has(payload.event)) return null;
  if (typeof payload.page !== 'string' || !allowedPages.has(payload.page)) return null;
  const allowedFields = payload.event === 'site_search'
    ? new Set(['event', 'page', 'result_count'])
    : payload.event === 'outbound_click'
      ? new Set(['event', 'page', 'product_id'])
      : payload.event === 'reader_signup'
        ? new Set(['event', 'page', 'confirmed'])
        : new Set(['event', 'page']);
  if (Object.keys(payload).some((field) => !allowedFields.has(field))) return null;
  if (payload.event === 'reader_signup' && payload.confirmed !== true) return null;
  const event = { name: payload.event, page: payload.page };
  if (payload.event === 'site_search') {
    if (!Number.isInteger(payload.result_count) || payload.result_count < 0 || payload.result_count > 1000) return null;
  }
  if (payload.event === 'outbound_click') {
    if (typeof payload.product_id !== 'string' || !allowedProductIds.has(payload.product_id)) return null;
    event.productId = payload.product_id;
  }
  return event;
}

async function readJsonBody(req) {
  if (!String(req.headers['content-type'] || '').toLowerCase().includes('application/json')) {
    throw Object.assign(new Error('Content-Type must be application/json.'), { statusCode: 415 });
  }
  let size = 0;
  const chunks = [];
  for await (const chunk of req) {
    size += chunk.length;
    if (size > maxBodyBytes) throw Object.assign(new Error('Request body is too large.'), { statusCode: 413 });
    chunks.push(chunk);
  }
  try {
    return JSON.parse(Buffer.concat(chunks).toString('utf8'));
  } catch {
    throw Object.assign(new Error('Invalid JSON.'), { statusCode: 400 });
  }
}

async function loadStore() {
  try {
    const value = JSON.parse(await fs.readFile(storePath, 'utf8'));
    if (value && value.schemaVersion === 1 && Array.isArray(value.counts)) return value;
  } catch {
    // An absent or unreadable store starts empty; no request body or network address is logged.
  }
  return { schemaVersion: 1, counts: [] };
}

function enqueueWrite(operation) {
  const result = writeQueue.then(operation);
  writeQueue = result.catch(() => {});
  return result;
}

async function recordEvent(event) {
  return enqueueWrite(async () => {
    const store = await loadStore();
    const day = utcDay();
    const cutoff = new Date(Date.now() - retentionDays * 86_400_000).toISOString().slice(0, 10);
    store.counts = store.counts.filter((row) => row.date >= cutoff);
    const match = store.counts.find((row) => row.date === day && row.event === event.name && row.page === event.page && row.productId === (event.productId || ''));
    if (match) match.count += 1;
    else store.counts.push({ date: day, event: event.name, page: event.page, productId: event.productId || '', count: 1 });
    await fs.mkdir(path.dirname(storePath), { recursive: true });
    const tempPath = `${storePath}.tmp`;
    await fs.writeFile(tempPath, JSON.stringify(store, null, 2), { mode: 0o600 });
    await fs.rename(tempPath, storePath);
  });
}

async function readSummary() {
  await writeQueue;
  const store = await loadStore();
  const events = {};
  for (const row of store.counts) events[row.event] = (events[row.event] || 0) + row.count;
  return { events, retentionDays, generatedOn: new Date().toISOString().slice(0, 10) };
}

async function serveStatic(req, res, pathname) {
  let decoded;
  try {
    decoded = decodeURIComponent(pathname);
  } catch {
    jsonResponse(res, 400, { error: 'Malformed path.' });
    return;
  }
  const relative = decoded.replace(/^\/+/, '');
  let filePath = path.resolve(siteRoot, relative || 'index.html');
  if (!filePath.startsWith(`${siteRoot}${path.sep}`) && filePath !== siteRoot) {
    jsonResponse(res, 403, { error: 'Forbidden.' });
    return;
  }
  try {
    let stat = await fs.stat(filePath);
    if (stat.isDirectory()) {
      filePath = path.join(filePath, 'index.html');
      stat = await fs.stat(filePath);
    }
    if (!stat.isFile()) throw new Error('Not a file');
    const ext = path.extname(filePath).toLowerCase();
    securityHeaders(res);
    res.writeHead(200, {
      'Content-Type': mimeTypes[ext] || 'application/octet-stream',
      'Content-Length': stat.size,
      'Cache-Control': ext === '.html' || ext === '.json' ? 'no-cache' : 'public, max-age=3600'
    });
    if (req.method === 'HEAD') res.end();
    else res.end(await fs.readFile(filePath));
  } catch {
    const notFound = path.join(siteRoot, '404.html');
    try {
      const body = await fs.readFile(notFound);
      securityHeaders(res);
      res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
      res.end(req.method === 'HEAD' ? undefined : body);
    } catch {
      jsonResponse(res, 404, { error: 'Not found.' });
    }
  }
}

const server = http.createServer(async (req, res) => {
  const requestUrl = new URL(req.url || '/', `http://${req.headers.host || 'localhost'}`);
  const pathname = requestUrl.pathname;
  if (pathname.endsWith('/data/analytics-runtime.json')) {
    jsonResponse(res, 200, analyticsEnabled
      ? { enabled: true, endpoint: '/api/events', summaryEndpoint: '/api/summary' }
      : { enabled: false, endpoint: '', summaryEndpoint: '' });
    return;
  }
  if (pathname === '/api/health') {
    jsonResponse(res, 200, { ok: true, storage: 'daily aggregate counts', retentionDays, analyticsEnabled });
    return;
  }
  if (pathname === '/api/summary') {
    if (!analyticsEnabled) {
      jsonResponse(res, 503, { error: 'Analytics is disabled.' });
      return;
    }
    if (req.method !== 'GET') {
      res.setHeader('Allow', 'GET');
      jsonResponse(res, 405, { error: 'Method not allowed.' });
      return;
    }
    jsonResponse(res, 200, await readSummary());
    return;
  }
  if (pathname === '/api/events') {
    if (!analyticsEnabled) {
      jsonResponse(res, 503, { error: 'Analytics is disabled.' });
      return;
    }
    if (req.method !== 'POST') {
      res.setHeader('Allow', 'POST');
      jsonResponse(res, 405, { error: 'Method not allowed.' });
      return;
    }
    if (!sameOriginRequest(req)) {
      jsonResponse(res, 403, { error: 'Same-origin requests only.' });
      return;
    }
    if (!allowRate(req)) {
      jsonResponse(res, 429, { error: 'Rate limit exceeded.' });
      return;
    }
    try {
      const payload = await readJsonBody(req);
      const event = parseEvent(payload);
      if (!event) {
        jsonResponse(res, 400, { error: 'Unsupported event or invalid fields.' });
        return;
      }
      await recordEvent(event);
      jsonResponse(res, 202, { accepted: true });
    } catch (error) {
      jsonResponse(res, error.statusCode || 500, { error: error.statusCode ? error.message : 'Unable to record aggregate event.' });
    }
    return;
  }
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    res.setHeader('Allow', 'GET, HEAD');
    jsonResponse(res, 405, { error: 'Method not allowed.' });
    return;
  }
  await serveStatic(req, res, pathname);
});

server.listen(port, host, () => {
  console.log(`Countertop Notes preview and self-hosted aggregate endpoint listening on http://${host}:${port}`);
  console.log(`Analytics runtime: ${analyticsEnabled ? 'enabled by explicit configuration' : 'disabled (default)'} · store: ${storePath} · retention: ${retentionDays} days · IP addresses are not persisted by this application.`);
});

server.on('error', (error) => {
  console.error(error);
  process.exitCode = 1;
});
