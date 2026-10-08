"""Run from the checkout: python -m troubleshoot.api."""

import argparse
import os
import secrets
import threading
import webbrowser

import uvicorn

from troubleshoot.api.app import create_app
from troubleshoot.providers.gemma_api import GemmaAPI
from troubleshoot.runtime.session import SessionManager
from troubleshoot.runtime.native import native_executor_from_env


def main():
    parser = argparse.ArgumentParser(description="TroubleShoot loopback UI/API")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true", help="Open the authenticated assistant in your browser")
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be between 1024 and 65535")
    token = os.getenv("TROUBLESHOOT_SESSION_TOKEN") or secrets.token_urlsafe(32)
    manager = SessionManager(providers={"gemma_api": GemmaAPI()},
                             executor=native_executor_from_env(), tool_seconds=45, run_seconds=300)
    app = create_app(manager, token, port=args.port)
    print(f"Open http://127.0.0.1:{args.port}")
    if args.open:
        threading.Timer(1.5, lambda: webbrowser.open(f"http://127.0.0.1:{args.port}/#session={token}")).start()
    else:
        print(f"Local session token (paste into UI): {token}")
    print("Hosted Gemma is the only enabled provider. Native approval has a five-second freshness limit; hosted mode requires consent.", flush=True)
    uvicorn.run(app, host="127.0.0.1", port=args.port, access_log=False, proxy_headers=False)


if __name__ == "__main__":
    main()
