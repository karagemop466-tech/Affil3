import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const serverFile = path.join(projectRoot, 'server/index.mjs');
const publicRuntimePath = path.join(projectRoot, '_site/data/analytics-runtime.json');
const temporaryDirectory = await fs.mkdtemp(path.join(os.tmpdir(), 'countertop-notes-test-'));
const storeFile = path.join(temporaryDirectory, 'analytics.json');

async function findPort() {
  return new Promise((resolve, reject) => {
    const listener = net.createServer();
    listener.once('error', reject);
    listener.listen(0, '127.0.0.1', () => {
      const address = listener.address();
      listener.close((error) => error ? reject(error) : resolve(address.port));
    });
  });
}

function startServer(port, enabled) {
  let output = '';
  const child = spawn(process.execPath, [serverFile], {
    cwd: projectRoot,
    env: {
      ...process.env,
      HOST: '127.0.0.1',
      PORT: String(port),
      ANALYTICS_STORE: storeFile,
      ANALYTICS_RETENTION_DAYS: '90',
      ANALYTICS_ENABLED: enabled ? 'true' : 'false'
    },
    stdio: ['ignore', 'pipe', 'pipe']
  });
  child.stdout.on('data', (chunk) => { output += chunk.toString(); });
  child.stderr.on('data', (chunk) => { output += chunk.toString(); });
  return { child, getOutput: () => output, base: `http://127.0.0.1:${port}` };
}

async function waitForHealth(server) {
  const deadline = Date.now() + 8000;
  while (Date.now() < deadline) {
    if (server.child.exitCode !== null) throw new Error(`Analytics server exited early.\n${server.getOutput()}`);
    try {
      const response = await fetch(`${server.base}/api/health`);
      if (response.ok) return response.json();
    } catch {
      // Wait briefly for the local child process to bind its port.
    }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error(`Analytics server did not become healthy.\n${server.getOutput()}`);
}

async function stopServer(server) {
  if (server?.child.exitCode === null) {
    server.child.kill('SIGTERM');
    await new Promise((resolve) => server.child.once('exit', resolve));
  }
}

async function postEvent(server, payload, headers = {}) {
  return fetch(`${server.base}/api/events`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Origin: server.base, 'Sec-Fetch-Site': 'same-origin', ...headers },
    body: JSON.stringify(payload)
  });
}

let server;
try {
  const publicRuntime = JSON.parse(await fs.readFile(publicRuntimePath, 'utf8'));
  assert.equal(publicRuntime.enabled, false, 'The built GitHub Pages runtime must remain disabled.');
  assert.equal(publicRuntime.endpoint, '');
  assert.equal(publicRuntime.summaryEndpoint, '');

  server = startServer(await findPort(), false);
  const disabledHealth = await waitForHealth(server);
  assert.equal(disabledHealth.analyticsEnabled, false);
  assert.equal(disabledHealth.retentionDays, 90);
  const disabledRuntime = await fetch(`${server.base}/data/analytics-runtime.json`);
  assert.equal(disabledRuntime.status, 200);
  assert.deepEqual(await disabledRuntime.json(), { enabled: false, endpoint: '', summaryEndpoint: '' });
  assert.equal((await postEvent(server, { event: 'page_view', page: 'index.html' })).status, 503);
  assert.equal((await fetch(`${server.base}/api/summary`)).status, 503);
  await stopServer(server);

  server = startServer(await findPort(), true);
  const enabledHealth = await waitForHealth(server);
  assert.equal(enabledHealth.analyticsEnabled, true);

  const runtimeResponse = await fetch(`${server.base}/data/analytics-runtime.json`);
  assert.equal(runtimeResponse.status, 200);
  assert.deepEqual(await runtimeResponse.json(), { enabled: true, endpoint: '/api/events', summaryEndpoint: '/api/summary' });

  const validPageView = await postEvent(server, { event: 'page_view', page: 'index.html' });
  assert.equal(validPageView.status, 202);

  const validClick = await postEvent(server, { event: 'outbound_click', page: 'desk/products.html', product_id: 'submitted-01' });
  assert.equal(validClick.status, 202);

  const invalidPersonalField = await postEvent(server, { event: 'site_search', page: 'guides/index.html', result_count: 1, query: 'private text' });
  assert.equal(invalidPersonalField.status, 400);

  const invalidProduct = await postEvent(server, { event: 'outbound_click', page: 'desk/products.html', product_id: 'not-a-record' });
  assert.equal(invalidProduct.status, 400);

  const unconfirmedSignup = await postEvent(server, { event: 'reader_signup', page: 'index.html' });
  assert.equal(unconfirmedSignup.status, 400);
  const confirmedSignup = await postEvent(server, { event: 'reader_signup', page: 'index.html', confirmed: true });
  assert.equal(confirmedSignup.status, 202);

  const missingOrigin = await postEvent(server, { event: 'page_view', page: 'index.html' }, { Origin: '', 'Sec-Fetch-Site': 'none' });
  assert.equal(missingOrigin.status, 403);
  const crossOrigin = await postEvent(server, { event: 'page_view', page: 'index.html' }, { Origin: 'https://attacker.invalid', 'Sec-Fetch-Site': 'cross-site' });
  assert.equal(crossOrigin.status, 403);

  const summaryResponse = await fetch(`${server.base}/api/summary`);
  assert.equal(summaryResponse.status, 200);
  const summary = await summaryResponse.json();
  assert.equal(summary.events.page_view, 1);
  assert.equal(summary.events.outbound_click, 1);
  assert.equal(summary.events.reader_signup, 1);

  const stored = await fs.readFile(storeFile, 'utf8');
  assert(!stored.includes('private text'));
  assert(!stored.includes('attacker.invalid'));
  assert(!stored.includes('127.0.0.1'));
  assert(!stored.includes('shopnow047c-20'));
  console.log('Analytics checks passed: public artifact and default preview disabled, explicit opt-in required, aggregates only, event allow-list, and cross-site guard.');
} finally {
  await stopServer(server);
  await fs.rm(temporaryDirectory, { recursive: true, force: true });
}
