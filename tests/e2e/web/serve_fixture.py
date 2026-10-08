"""Manual browser test only: python tests/e2e/web/serve_fixture.py.

Always labeled synthetic; never imported by the production launcher.
"""

import secrets
import sys
from pathlib import Path

import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "api"))
from fixtures import FixtureExecutor, FixtureProvider
from troubleshoot.api.app import create_app
from troubleshoot.runtime.session import SessionManager


if __name__ == "__main__":
    token = secrets.token_urlsafe(32)
    manager = SessionManager({"ollama": FixtureProvider(action=False)}, FixtureExecutor(), simulation=True)
    print("SYNTHETIC browser fixture: http://127.0.0.1:8766", flush=True)
    print(f"Local test session token: {token}", flush=True)
    uvicorn.run(create_app(manager, token, port=8766), host="127.0.0.1", port=8766,
                access_log=False, proxy_headers=False)
