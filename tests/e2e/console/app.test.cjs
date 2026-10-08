// UI behavior tests with a synthetic DOM/transport; not a live browser or repair test.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');

function harness(fetch) {
  const elements = new Map();
  function element(id) {
    if (!elements.has(id)) elements.set(id, {
      value: '', hidden: false, disabled: false, checked: false, textContent: '', children: [], handlers: {},
      addEventListener(name, fn) { this.handlers[name] = fn; },
      querySelector() { return element(id + '-button'); },
      replaceChildren(...items) { this.children = items; },
      append(item) { this.children.push(item); }, add(item) { this.children.push(item); },
    });
    return elements.get(id);
  }
  element('provider').value = 'ollama'; element('mode').value = 'diagnose';
  const context = vm.createContext({
    document: { getElementById: element, createElement: () => ({ textContent: '', children: [], append(...items) { this.children.push(...items); } }) },
    Option: function(text, value) { this.textContent = text; this.value = value; },
    fetch, TextDecoder, console, URLSearchParams,
    window: { addEventListener() {} }, navigator: {},
    location: { hash: "", pathname: "/" }, history: { replaceState() {} },
  });
  vm.runInContext(fs.readFileSync(path.join(__dirname, '../../../src/troubleshoot/api/console/app.js'), 'utf8'), context);
  return { element, run: source => vm.runInContext(source, context) };
}

test('unavailable local provider cannot start and hosted needs consent', () => {
  const h = harness();
  h.run(`status = {simulation:false, providers:{ollama:{configured:false,readiness:'unavailable'},gemma_api:{configured:true,readiness:'unverified',model:'gemma-4-26b-a4b-it'}}}; updateControls()`);
  assert.equal(h.element('start').disabled, true);
  h.element('provider').value = 'gemma_api'; h.run('updateControls()');
  assert.equal(h.element('start').disabled, true);
  h.element('cloud').checked = true; h.run('updateControls()');
  assert.equal(h.element('start').disabled, false);
});

test('partial and unresolved remain explicit with recovery and limitations', () => {
  for (const verdict of ['partial', 'unresolved', 'cancelled', 'error']) {
    const h = harness();
    h.run(`runId='synthetic'; receive({id:'1',type:'complete',payload:{verdict:'${verdict}',recovery:'pending',limitations:['Synthetic only'],simulation:true}})`);
    assert.equal(h.element('verdict').textContent, `${verdict} (synthetic fixture)`);
    assert.equal(h.element('recovery').textContent, 'Recovery: pending');
    assert.equal(h.element('limitations').textContent, 'Synthetic only');
    assert.equal(h.element('stop').disabled, true);
  }
});

test('approval payload uses text and does not render token in timeline', () => {
  const h = harness();
  h.run(`receive({id:'1',type:'approval',payload:{token:'secret-token',action:{action_id:'synthetic',operation:'<img onerror=bad>'}}})`);
  assert.equal(h.element('approval').hidden, false);
  assert.ok(h.element('action-detail').textContent.includes('<img onerror=bad>'));
  assert.ok(!h.element('timeline').children[0].textContent.includes('secret-token'));
});

test('broken SSE exposes reconnect and retains Stop', async () => {
  const h = harness(async url => url === '/api/runs'
    ? { ok: true, json: async () => ({ run_id: 'synthetic' }) }
    : { ok: true, body: { getReader: () => ({ read: async () => ({ done: true }), releaseLock() {} }) } });
  h.element('complaint').value = 'Synthetic';
  await h.element('run-form').handlers.submit({ preventDefault() {} });
  assert.match(h.element('error').textContent, /ended before completion/);
  assert.equal(h.element('reconnect').hidden, false);
  assert.equal(h.element('stop').disabled, false);
});

test('SSE handles split Unicode chunks and terminal event', async () => {
  const payload = 'id: 1\nevent: complete\ndata: '+JSON.stringify({id:'1',type:'complete',payload:{verdict:'unresolved',recovery:'none',limitations:['Synthetic ✓'],simulation:true}})+'\n\n';
  const bytes = new TextEncoder().encode(payload);
  const chunks = Array.from(bytes, byte => new Uint8Array([byte]));
  const h = harness(async () => ({ ok: true, body: { getReader: () => ({
    read: async () => chunks.length ? { value: chunks.shift(), done: false } : { done: true }, releaseLock() {},
  }) } }));
  await h.run(`runId='synthetic'; streamEvents('synthetic')`);
  assert.equal(h.element('limitations').textContent, 'Synthetic ✓');
  assert.equal(h.element('result').hidden, false);
});


test('diagnosis text is visible and per-run cloud consent resets after completion', () => {
  const h = harness();
  h.element('cloud').checked = true;
  h.run(`receive({id:'1',type:'plan',payload:{summary:'Spooler is running; print not verified.',action:null}})`);
  assert.match(h.element('diagnosis').textContent, /print not verified/);
  h.run(`receive({id:'2',type:'complete',payload:{verdict:'unresolved',recovery:'none',limitations:[],simulation:false}})`);
  assert.equal(h.element('cloud').checked, false);
});

test('offline state disables new inference and explains the helper requirement', () => {
  const h = harness();
  h.element('provider').value = 'gemma_api'; h.element('cloud').checked = true;
  h.run(`status={providers:{gemma_api:{configured:true}}}; navigator.onLine=false; networkChanged()`);
  assert.equal(h.element('start').disabled, true);
  assert.match(h.element('connection-notice').textContent, /Windows helper/);
});


test('successful diagnosis without an action is not presented as a failed repair', () => {
  const h = harness();
  h.run(`receive({id:'1',type:'plan',payload:{summary:'Fresh system facts',action:null}});
    receive({id:'2',type:'complete',payload:{verdict:'unresolved',recovery:'none',limitations:['No symptom verified'],simulation:false}})`);
  assert.equal(h.element('verdict').textContent, 'Diagnosis complete · no changes made');
  assert.equal(h.element('limitations').textContent, 'No symptom verified');
});

test('repair mode and errors never get a successful diagnosis label', () => {
  for (const mode of ['diagnose', 'repair']) {
    const h = harness(); h.element('mode').value = mode;
    h.run(`receive({id:'1',type:'plan',payload:{summary:'Facts',action:null}})`);
    if (mode === 'diagnose') h.run(`receive({id:'2',type:'error',payload:{code:'hosted_unavailable'}})`);
    h.run(`receive({id:'3',type:'complete',payload:{verdict:'unresolved',recovery:'none',limitations:[],simulation:false}})`);
    assert.equal(h.element('verdict').textContent, 'unresolved');
  }
});
