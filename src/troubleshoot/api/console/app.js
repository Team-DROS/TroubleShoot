const $ = id => document.getElementById(id);
let token = "", status = null, runId = null, approval = null, starting = false, lastEventId = "0";

function showError(message) { $("error").textContent = message; $("error").hidden = false; }
function clearError() { $("error").hidden = true; }

async function api(path, options = {}) {
  const response = await fetch(path, { ...options, headers: {
    Authorization: `Bearer ${token}`, "Content-Type": "application/json", ...options.headers,
  }});
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.error || `Request failed (${response.status})`);
  }
  return response;
}

function updateControls() {
  const provider = status?.providers[$("provider").value];
  $("provider-status").textContent = provider
    ? `Model: ${provider.model || "not configured"} · ${provider.readiness}${status.simulation ? " · SYNTHETIC FIXTURE" : ""}`
    : "Connect to check provider readiness.";
  $("start").disabled = starting || Boolean(runId) || !provider?.configured ||
    ($("provider").value === "gemma_api" && !$("cloud").checked);
  $("start").textContent = $("mode").value === "repair" ? "Start repair review" : "Start diagnosis";
  $("stop").disabled = !runId;
  $("connect").querySelector("button").disabled = Boolean(runId);
  for (const id of ["provider", "mode", "target", "cloud", "complaint"]) $(id).disabled = Boolean(runId);
}

$("connect").addEventListener("submit", async event => {
  event.preventDefault(); clearError(); token = $("token").value.trim();
  try {
    status = await (await api("/api/status")).json();
    const targets = await (await api("/api/targets")).json();
    $("target").replaceChildren(new Option("No window selected", ""));
    for (const item of targets.targets) $("target").add(new Option(item.label, JSON.stringify(item.target)));
    const system = targets.targets.find(item => item.scope === "system");
    if (system) $("target").value = JSON.stringify(system.target);
    $("target-status").textContent = targets.available ? "Select a permitted target for observed actions." : "Native window integration is pending.";
    $("status").textContent = status.simulation ? "Connected · SYNTHETIC FIXTURE; no real repair" : "Connected to the local API";
    $("token").value = "";
  } catch (error) { token = ""; status = null; $("status").textContent = "Connection failed"; showError(error.message); }
  updateControls();
});
for (const id of ["provider", "mode", "cloud"]) $(id).addEventListener("change", updateControls);

function receive(item) {
  lastEventId = item.id;
  const row = document.createElement("li");
  const safePayload = { ...item.payload }; delete safePayload.token;
  row.textContent = `${item.type} · ${JSON.stringify(safePayload)}`;
  $("timeline").append(row); $("empty").hidden = true;
  if (item.type === "approval") {
    approval = item.payload; $("approval").hidden = false;
    $("action-detail").textContent = JSON.stringify(safePayload, null, 2);
    $("approval-time").textContent = `Approve within ${Math.max(0, item.payload.freshness_seconds ?? 5).toFixed(1)} seconds. After that the action expires; start a new run. Native checks can shorten this window.`;
    $("approve").disabled = false; $("reject").disabled = false;
  }
  if (item.type === "error") showError(item.payload.code);
  if (item.type === "complete") {
    $("result").hidden = false;
    $("verdict").textContent = `${item.payload.verdict}${item.payload.simulation ? " (synthetic fixture)" : ""}`;
    $("recovery").textContent = `Recovery: ${item.payload.recovery}`;
    $("limitations").textContent = item.payload.limitations.join(" ");
    runId = null; approval = null; $("approval").hidden = true; $("reconnect").hidden = true; updateControls();
  }
}

// Fetch streaming preserves the Authorization header; no token in URLs/cookies.
async function streamEvents(id) {
  const response = await api(`/api/runs/${id}/events`, { headers: { "Last-Event-ID": lastEventId } });
  if (!response.body) throw new Error("Event stream unavailable; Stop remains available.");
  const reader = response.body.getReader(), decoder = new TextDecoder();
  let buffer = "";
  try {
    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value, { stream: !done });
      let end;
      while ((end = buffer.indexOf("\n\n")) !== -1) {
        const block = buffer.slice(0, end); buffer = buffer.slice(end + 2);
        const data = block.split("\n").filter(line => line.startsWith("data: ")).map(line => line.slice(6)).join("\n");
        if (data) receive(JSON.parse(data));
      }
      if (done) break;
    }
    if (runId === id) throw new Error("Event stream ended before completion; use Stop to cancel this run.");
  } finally { reader.releaseLock(); }
}

$("run-form").addEventListener("submit", async event => {
  event.preventDefault(); if (runId || starting) return; clearError(); starting = true; lastEventId = "0";
  $("start").disabled = true;
  $("timeline").replaceChildren(); $("empty").hidden = false; $("result").hidden = true;
  try {
    const result = await (await api("/api/runs", { method: "POST", body: JSON.stringify({
      complaint: $("complaint").value, mode: $("mode").value, provider: $("provider").value,
      cloud_consent: $("cloud").checked, vision_enabled: false, cloud_images_consent: false,
      target: $("target").value ? JSON.parse($("target").value) : null,
    }) })).json();
    runId = result.run_id; starting = false; updateControls(); await streamEvents(runId);
  } catch (error) { showError(error.message); $("reconnect").hidden = !runId; }
  finally { starting = false; updateControls(); }
});

$("reconnect").addEventListener("click", async () => {
  if (!runId) return;
  $("reconnect").hidden = true; clearError();
  try { await streamEvents(runId); }
  catch (error) { showError(error.message); $("reconnect").hidden = !runId; }
});

async function decide(approve) {
  if (!approval || !runId) return;
  $("approve").disabled = true; $("reject").disabled = true;
  try {
    await api(`/api/runs/${runId}/decision`, { method: "POST", body: JSON.stringify({
      token: approval.token, action_id: approval.action.action_id, approve,
    }) });
    approval = null; $("approval").hidden = true;
  } catch (error) { showError(error.message); }
}
$("approve").addEventListener("click", () => decide(true));
$("reject").addEventListener("click", () => decide(false));
$("stop").addEventListener("click", async () => {
  if (!runId) return;
  try {
    const result = await (await api(`/api/runs/${runId}/cancel`, { method: "POST", body: "{}" })).json();
    approval = null; $("approval").hidden = true;
    $("status").textContent = `Stop requested · recovery: ${result.recovery}. Waiting for completion.`;
    if (result.state === "complete") { runId = null; updateControls(); }
  } catch (error) { showError(error.message); }
});

let installPrompt;
window.addEventListener("beforeinstallprompt", event => {
  event.preventDefault(); installPrompt = event; $("install").hidden = false;
});
$("install").addEventListener("click", async () => {
  if (!installPrompt) return;
  await installPrompt.prompt(); installPrompt = null; $("install").hidden = true;
});
if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});

const initialSession = new URLSearchParams(location.hash.slice(1)).get("session");
if (initialSession) {
  history.replaceState(null, "", location.pathname);
  $("token").value = initialSession;
  $("connect").requestSubmit();
}
