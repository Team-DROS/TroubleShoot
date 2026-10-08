"""Explicit-consent read-only API integration check; never creates a service fault."""
import argparse
import json
import secrets
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from fastapi.testclient import TestClient
from troubleshoot.api.app import create_app
from troubleshoot.runtime.session import SessionManager
from troubleshoot.runtime.native import native_executor_from_env
from troubleshoot.providers.gemma_api import GemmaAPI

parser = argparse.ArgumentParser()
parser.add_argument("--consent-cloud-text", action="store_true", required=True)
args = parser.parse_args()
native = native_executor_from_env()
if native is None:
    raise SystemExit("Windows helper required")
manager = SessionManager({"gemma_api": GemmaAPI()}, executor=native, tool_seconds=45, run_seconds=180)
token = secrets.token_urlsafe(32)
with TestClient(create_app(manager, token), base_url="http://127.0.0.1:8765") as client:
    headers = {"Authorization": "Bearer " + token}
    response = client.post("/api/runs", headers=headers, json={
        "complaint": "Check the print Spooler service health. Diagnose only; do not change anything. Report whether service state alone proves successful printing.",
        "mode": "diagnose", "provider": "gemma_api", "cloud_consent": True,
        "target": asdict(native.system_target)})
    response.raise_for_status()
    run = response.json()["run_id"]
    stream = client.get("/api/runs/" + run + "/events", headers=headers)
    stream.raise_for_status()
    events = [json.loads(line[6:]) for line in stream.text.splitlines() if line.startswith("data: ")]
    result = {"time_utc": datetime.now(timezone.utc).isoformat(), "provider": "gemma_api",
              "model": "gemma-4-26b-a4b-it", "environment": "Windows host read-only; no guest fault",
              "cloud_consent": "explicit run consent", "events": events}
    Path("artifacts/private").mkdir(parents=True, exist_ok=True)
    Path("artifacts/private/hosted-diagnosis.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    for item in events:
        if item["type"] != "observation":
            print(item["type"], item["payload"])
