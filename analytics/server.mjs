import http from 'node:http';
import { readFile, writeFile, mkdir, rename } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';

// Minimal self-hosted aggregate counter. It stores no cookies, IP addresses, user agents,
// referrers, query strings, full URLs or per-event records. Counts are grouped by UTC day,
// event name and a page slug. Configure a fixed ALLOWED_ORIGIN for the static site.
const PORT = Number(process.env.PORT || 8787);
const ALLOWED_ORIGIN = process.env.ALLOWED_ORIGIN || '';
const SUMMARY_TOKEN = process.env.SUMMARY_TOKEN || '';
const STORE_PATH = resolve(process.env.ANALYTICS_STORE || './data/aggregate-counts.json');
const ALLOWED_EVENTS = new Set(['page_view', 'guide_open', 'outbound_click', 'suggestion_vote', 'reader_capture']);
const ALLOWED_PAGES = new Set(['home', 'editorial', 'flagged-review', 'methodology', 'guide-basket-oven', 'guide-capacity', 'guide-cleanup', 'guide-functions']);
const counts = new Map();

async function load() {
  try {
    const rows = JSON.parse(await readFile(STORE_PATH, 'utf8'));
    const cutoff = new Date(Date.now() - 90 * 86400000).toISOString().slice(0, 10);
    for (const row of Array.isArray(rows) ? rows : []) {
      if (row && typeof row.day === 'string' && row.day >= cutoff && ALLOWED_EVENTS.has(row.event) && ALLOWED_PAGES.has(row.page) && Number.isSafeInteger(row.count) && row.count > 0) {
        counts.set(`${row.day}|${row.event}|${row.page}`, row.count);
      }
    }
  } catch (error) { if (error.code !== 'ENOENT') console.error('Could not load aggregate counts:', error.message); }
}

async function persist() {
  await mkdir(dirname(STORE_PATH), { recursive: true });
  const rows = [...counts].map(([key, count]) => {
    const [day, event, page] = key.split('|');
    return { day, event, page, count };
  });
  const temp = `${STORE_PATH}.tmp`;
  await writeFile(temp, JSON.stringify(rows, null, 2), { mode: 0o600 });
  await rename(temp, STORE_PATH);
}

function send(res, status, body, origin = '') {
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff',
    ...(origin ? { 'Access-Control-Allow-Origin': origin, 'Vary': 'Origin' } : {})
  });
  res.end(JSON.stringify(body));
}

const server = http.createServer(async (req, res) => {
  const origin = req.headers.origin || '';
  if (req.method === 'OPTIONS' && req.url === '/api/events') {
    if (!ALLOWED_ORIGIN || origin !== ALLOWED_ORIGIN) return send(res, 403, { error: 'origin_not_allowed' });
    res.writeHead(204, { 'Access-Control-Allow-Origin': ALLOWED_ORIGIN, 'Access-Control-Allow-Methods': 'POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Max-Age': '600', 'Vary': 'Origin' });
    return res.end();
  }
  if (req.url === '/health' && req.method === 'GET') return send(res, 200, { ok: true, storage: 'aggregate-only' });
  if (req.url === '/api/events' && req.method === 'POST') {
    if (!ALLOWED_ORIGIN || origin !== ALLOWED_ORIGIN) return send(res, 403, { error: 'origin_not_allowed' });
    if (!req.headers['content-type']?.toLowerCase().startsWith('application/json')) return send(res, 415, { error: 'json_required' }, ALLOWED_ORIGIN);
    let raw = '';
    for await (const chunk of req) {
      raw += chunk;
      if (raw.length > 2048) { req.destroy(); return; }
    }
    let payload;
    try { payload = JSON.parse(raw); } catch { return send(res, 400, { error: 'invalid_json' }, ALLOWED_ORIGIN); }
    if (!ALLOWED_EVENTS.has(payload?.event) || !ALLOWED_PAGES.has(payload?.page)) return send(res, 400, { error: 'unsupported_event_or_page' }, ALLOWED_ORIGIN);
    const day = new Date().toISOString().slice(0, 10);
    const key = `${day}|${payload.event}|${payload.page}`;
    counts.set(key, (counts.get(key) || 0) + 1);
    try { await persist(); } catch (error) { return send(res, 500, { error: 'aggregate_write_failed' }, ALLOWED_ORIGIN); }
    return send(res, 202, { accepted: true }, ALLOWED_ORIGIN);
  }
  if (req.url === '/api/summary' && req.method === 'GET') {
    if (!SUMMARY_TOKEN || req.headers.authorization !== `Bearer ${SUMMARY_TOKEN}`) return send(res, 401, { error: 'unauthorized' });
    return send(res, 200, [...counts].map(([key, count]) => {
      const [day, event, page] = key.split('|');
      return { day, event, page, count };
    }));
  }
  return send(res, 404, { error: 'not_found' });
});

await load();
server.listen(PORT, '0.0.0.0', () => console.log(`Aggregate analytics endpoint listening on 0.0.0.0:${PORT}; CORS origin configured: ${Boolean(ALLOWED_ORIGIN)}`));
