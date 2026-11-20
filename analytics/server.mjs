import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_DATA_PATH = path.resolve(HERE, '../analytics-data/aggregates.json');
const CLIENT_EVENTS = new Set([
  'page_view',
  'guide_engagement',
  'outbound_click',
  'reader_capture_intent',
]);
const CHANNELS = new Set(['direct', 'organic', 'paid', 'social', 'newsletter', 'unknown']);
const MAX_BODY_BYTES = 4096;

function json(response, status, body) {
  response.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'no-referrer',
  });
  response.end(JSON.stringify(body));
}

function validToken(value) {
  return typeof value === 'string' && /^[a-z0-9][a-z0-9._-]{0,79}$/i.test(value);
}

function validDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const parsed = new Date(`${value}T00:00:00.000Z`);
  return !Number.isNaN(parsed.valueOf()) && parsed.toISOString().slice(0, 10) === value;
}

async function readJsonBody(request) {
  if (!String(request.headers['content-type'] || '').toLowerCase().startsWith('application/json')) {
    const error = new Error('unsupported_content_type');
    error.status = 415;
    throw error;
  }

  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > MAX_BODY_BYTES) {
      const error = new Error('payload_too_large');
      error.status = 413;
      throw error;
    }
    chunks.push(chunk);
  }

  try {
    const value = JSON.parse(Buffer.concat(chunks).toString('utf8'));
    if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('invalid_object');
    return value;
  } catch {
    const error = new Error('invalid_json');
    error.status = 400;
    throw error;
  }
}

function hasOnlyKeys(object, allowed) {
  return Object.keys(object).every((key) => allowed.has(key));
}

function utcDate(now) {
  return now.toISOString().slice(0, 10);
}

export function createServer({
  dataPath = DEFAULT_DATA_PATH,
  allowedOrigin = '',
  reportToken = '',
  now = () => new Date(),
} = {}) {
  const resolvedDataPath = path.resolve(dataPath);
  let recordsPromise;
  let writeQueue = Promise.resolve();

  async function loadRecords() {
    if (!recordsPromise) {
      recordsPromise = fs.readFile(resolvedDataPath, 'utf8')
        .then((text) => {
          const parsed = JSON.parse(text);
          return Array.isArray(parsed) ? parsed : [];
        })
        .catch((error) => {
          if (error.code === 'ENOENT') return [];
          throw error;
        });
    }
    return recordsPromise;
  }

  function updateRecords(updater) {
    const operation = writeQueue.then(async () => {
      const records = await loadRecords();
      const result = await updater(records);
      await fs.mkdir(path.dirname(resolvedDataPath), { recursive: true });
      const tempPath = `${resolvedDataPath}.${process.pid}.tmp`;
      await fs.writeFile(tempPath, `${JSON.stringify(records, null, 2)}\n`, { mode: 0o600 });
      await fs.rename(tempPath, resolvedDataPath);
      return result;
    });
    writeQueue = operation.catch(() => {});
    return operation;
  }

  function recordClientEvent(event, nowValue) {
    const date = utcDate(nowValue);
    const key = [date, event.event, event.channel, event.contentId || '', event.linkId || ''].join('|');
    return updateRecords((records) => {
      const existing = records.find((row) => row.aggregateKey === key);
      if (existing) {
        existing.count += 1;
        existing.lastRecordedAt = nowValue.toISOString();
        return existing;
      }
      const row = {
        aggregateKey: key,
        date,
        event: event.event,
        source: 'site_event',
        channel: event.channel,
        contentId: event.contentId || null,
        linkId: event.linkId || null,
        count: 1,
        recordedAt: nowValue.toISOString(),
        lastRecordedAt: nowValue.toISOString(),
      };
      records.push(row);
      return row;
    });
  }

  function addReportImport(report, nowValue) {
    const duplicate = (records) => records.some((row) =>
      row.event === 'reported_order_import' &&
      row.date === report.reportDate &&
      row.channel === report.channel &&
      row.provenance === report.provenance
    );

    return updateRecords((records) => {
      if (duplicate(records)) {
        const error = new Error('duplicate_report');
        error.status = 409;
        throw error;
      }
      const row = {
        date: report.reportDate,
        event: 'reported_order_import',
        source: 'amazon_associates_central',
        channel: report.channel,
        eligibleSessions: report.eligibleSessions ?? null,
        clicks: report.clicks,
        reportedOrders: report.reportedOrders,
        provenance: report.provenance,
        count: 1,
        recordedAt: nowValue.toISOString(),
      };
      records.push(row);
      return row;
    });
  }

  const server = http.createServer(async (request, response) => {
    const requestUrl = new URL(request.url || '/', 'http://analytics.invalid');
    const pathname = requestUrl.pathname;

    if (request.method === 'GET' && pathname === '/api/health') {
      return json(response, 200, {
        ok: true,
        storage: 'daily-aggregate-json',
        clientCollectionEnabled: Boolean(allowedOrigin),
        reportImportEnabled: Boolean(reportToken),
      });
    }

    if (request.method === 'POST' && pathname === '/api/events') {
      if (!allowedOrigin) return json(response, 503, { error: 'client_collection_not_configured' });
      if (request.headers.origin !== allowedOrigin) return json(response, 403, { error: 'origin_not_allowed' });

      try {
        const body = await readJsonBody(request);
        const allowedKeys = new Set(['event', 'contentId', 'linkId', 'channel']);
        if (!hasOnlyKeys(body, allowedKeys) || !CLIENT_EVENTS.has(body.event)) {
          return json(response, 400, { error: 'invalid_event' });
        }
        if (!CHANNELS.has(body.channel)) return json(response, 400, { error: 'invalid_channel' });
        if (body.contentId !== undefined && !validToken(body.contentId)) {
          return json(response, 400, { error: 'invalid_content_id' });
        }
        if (body.linkId !== undefined && !validToken(body.linkId)) {
          return json(response, 400, { error: 'invalid_link_id' });
        }
        if (body.event === 'outbound_click' && !body.linkId) {
          return json(response, 400, { error: 'link_id_required' });
        }
        if (body.event !== 'outbound_click' && body.linkId !== undefined) {
          return json(response, 400, { error: 'link_id_not_allowed' });
        }
        if (body.event === 'guide_engagement' && !body.contentId) {
          return json(response, 400, { error: 'content_id_required' });
        }

        await recordClientEvent(body, now());
        response.writeHead(204, {
          'Cache-Control': 'no-store',
          'X-Content-Type-Options': 'nosniff',
          'Referrer-Policy': 'no-referrer',
        });
        return response.end();
      } catch (error) {
        return json(response, error.status || 400, { error: error.status ? error.message : 'invalid_request' });
      }
    }

    if (request.method === 'POST' && pathname === '/api/reports/associates') {
      if (!reportToken) return json(response, 503, { error: 'report_import_not_configured' });
      const authorization = String(request.headers.authorization || '');
      if (authorization !== `Bearer ${reportToken}`) return json(response, 401, { error: 'unauthorized' });

      try {
        const body = await readJsonBody(request);
        const allowedKeys = new Set(['reportDate', 'channel', 'eligibleSessions', 'clicks', 'reportedOrders', 'provenance']);
        if (!hasOnlyKeys(body, allowedKeys) || !validDate(body.reportDate) || !CHANNELS.has(body.channel)) {
          return json(response, 400, { error: 'invalid_report' });
        }
        const nonnegativeInteger = (value) => Number.isSafeInteger(value) && value >= 0;
        if (!nonnegativeInteger(body.clicks) || !nonnegativeInteger(body.reportedOrders)) {
          return json(response, 400, { error: 'invalid_report_totals' });
        }
        if (body.eligibleSessions !== undefined && body.eligibleSessions !== null && !nonnegativeInteger(body.eligibleSessions)) {
          return json(response, 400, { error: 'invalid_eligible_sessions' });
        }
        if (typeof body.provenance !== 'string' || body.provenance.trim().length < 1 || body.provenance.length > 120) {
          return json(response, 400, { error: 'provenance_required' });
        }

        const row = await addReportImport(body, now());
        return json(response, 201, { accepted: true, date: row.date, source: row.source });
      } catch (error) {
        return json(response, error.status || 400, { error: error.status ? error.message : 'invalid_request' });
      }
    }

    return json(response, 404, { error: 'not_found' });
  });

  return server;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const allowedOrigin = process.env.ANALYTICS_ALLOWED_ORIGIN || '';
  const reportToken = process.env.ASSOCIATES_REPORT_TOKEN || '';
  if (process.env.NODE_ENV === 'production' && (!allowedOrigin || !reportToken)) {
    console.error('Production startup requires ANALYTICS_ALLOWED_ORIGIN and ASSOCIATES_REPORT_TOKEN.');
    process.exit(1);
  }
  const port = Number(process.env.PORT || 8787);
  const host = process.env.HOST || '0.0.0.0';
  const server = createServer({
    dataPath: process.env.ANALYTICS_DATA_PATH || DEFAULT_DATA_PATH,
    allowedOrigin,
    reportToken,
  });
  server.listen(port, host, () => {
    const address = server.address();
    console.log(`Aggregate analytics API listening on ${host}:${address.port}`);
  });
}
