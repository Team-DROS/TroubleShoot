"""Run from the checkout: python -m troubleshoot.api."""

import argparse
import os
import secrets

import uvicorn

from troubleshoot.api.app import create_app
from troubleshoot.providers.gemma_api import GemmaAPI
from troubleshoot.runtime.session import SessionManager


def main():
    parser = argparse.ArgumentParser(description="TroubleShoot loopback UI/API")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be between 1024 and 65535")
    token = os.getenv("TROUBLESHOOT_SESSION_TOKEN") or secrets.token_urlsafe(32)
    manager = SessionManager(providers={"gemma_api": GemmaAPI()})
    app = create_app(manager, token, port=args.port)
    print(f"Open http://127.0.0.1:{args.port}")
    print(f"Local session token (paste into UI): {token}")
    print("Local provider/native executor integration pending. Hosted mode requires explicit consent.", flush=True)
    uvicorn.run(app, host="127.0.0.1", port=args.port, access_log=False, proxy_headers=False)


if __name__ == "__main__":
    main()
