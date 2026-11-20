import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { createServer } from './server.mjs';

const directory = await fs.mkdtemp(path.join(os.tmpdir(), 'counter-notes-analytics-'));
const dataPath = path.join(directory, 'aggregates.json');
const allowedOrigin = 'https://counter-notes.example';
const reportToken = 'test-report-token';
const fixedNow = () => new Date('2026-11-20T12:00:00.000Z');
const server = createServer({ dataPath, allowedOrigin, reportToken, now: fixedNow });

try {
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const address = server.address();
  const baseUrl = `http://127.0.0.1:${address.port}`;

  const pageView = await fetch(`${baseUrl}/api/events`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', origin: allowedOrigin },
    body: JSON.stringify({ event: 'page_view', contentId: 'home', channel: 'unknown' }),
  });
  assert.equal(pageView.status, 204);

  const outbound = await fetch(`${baseUrl}/api/events`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', origin: allowedOrigin },
    body: JSON.stringify({ event: 'outbound_click', contentId: 'product-shelf', linkId: 'product-01', channel: 'organic' }),
  });
  assert.equal(outbound.status, 204);

  const badOrigin = await fetch(`${baseUrl}/api/events`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', origin: 'https://not-allowed.example' },
    body: JSON.stringify({ event: 'page_view', contentId: 'home', channel: 'unknown' }),
  });
  assert.equal(badOrigin.status, 403);

  const rejectsSensitiveFields = await fetch(`${baseUrl}/api/events`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', origin: allowedOrigin },
    body: JSON.stringify({ event: 'page_view', contentId: 'home', channel: 'unknown', fullUrl: 'https://example.test/?email=reader@example.test' }),
  });
  assert.equal(rejectsSensitiveFields.status, 400);

  const unauthorizedImport = await fetch(`${baseUrl}/api/reports/associates`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({
      reportDate: '2026-11-19', channel: 'organic', clicks: 0,
      reportedOrders: 0, provenance: 'test report',
    }),
  });
  assert.equal(unauthorizedImport.status, 401);

  const report = {
    reportDate: '2026-11-19',
    channel: 'organic',
    eligibleSessions: null,
    clicks: 7,
    reportedOrders: 1,
    provenance: 'Associates Central daily report, 2026-11-19',
  };
  const imported = await fetch(`${baseUrl}/api/reports/associates`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', authorization: `Bearer ${reportToken}` },
    body: JSON.stringify(report),
  });
  assert.equal(imported.status, 201);

  const duplicate = await fetch(`${baseUrl}/api/reports/associates`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', authorization: `Bearer ${reportToken}` },
    body: JSON.stringify(report),
  });
  assert.equal(duplicate.status, 409);

  const stored = JSON.parse(await fs.readFile(dataPath, 'utf8'));
  assert.equal(stored.length, 3);
  assert.equal(stored.find((row) => row.event === 'page_view').count, 1);
  assert.equal(stored.find((row) => row.event === 'outbound_click').linkId, 'product-01');
  assert.equal(stored.find((row) => row.event === 'reported_order_import').reportedOrders, 1);
  assert.equal(JSON.stringify(stored).includes('not-allowed.example'), false);
  assert.equal(JSON.stringify(stored).includes('reader@example.test'), false);
  assert.equal(stored.some((row) => 'ipAddress' in row || 'userAgent' in row || 'referrer' in row || 'fullUrl' in row), false);

  console.log('analytics tests passed');
} finally {
  await new Promise((resolve) => server.close(resolve));
  await fs.rm(directory, { recursive: true, force: true });
}
