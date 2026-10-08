"""Run from the checkout: python -m troubleshoot.api."""

import argparse
import errno
import os
import secrets
import socket
import threading
import webbrowser

import uvicorn

from troubleshoot.api.app import create_app
from troubleshoot.providers.gemma_api import GemmaAPI
from troubleshoot.runtime.session import SessionManager
from troubleshoot.runtime.native import native_executor_from_env


def reserve_listener(port, *, fallback=False):
    """Reserve loopback before creating a session; never attach to an unknown listener."""
    ports = range(port, min(port + 20, 65535) + 1) if fallback else (port,)
    for candidate in ports:
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if os.name == "nt":
                listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            listener.bind(("127.0.0.1", candidate))
            listener.listen(128)
            listener.setblocking(False)
            return listener
        except OSError as exc:
            listener.close()
            if exc.errno not in (errno.EADDRINUSE, errno.EACCES) and getattr(exc, "winerror", None) not in (10048, 10013):
                raise
    raise OSError(errno.EADDRINUSE, "No available loopback port in the bounded range")


class BrowserServer(uvicorn.Server):
    launch_url = None

    async def startup(self, sockets=None):
        await super().startup(sockets=sockets)
        if self.started and self.launch_url:
            threading.Thread(target=webbrowser.open, args=(self.launch_url,), daemon=True).start()


def main():
    parser = argparse.ArgumentParser(description="TroubleShoot loopback UI/API")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true", help="Open the authenticated assistant in your browser")
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be between 1024 and 65535")
    try:
        listener = reserve_listener(args.port, fallback=args.open)
    except OSError:
        parser.exit(1, "Cannot reserve the loopback port. Choose a different --port.\n")
    selected_port = listener.getsockname()[1]
    if selected_port != args.port:
        print(f"Port {args.port} is busy; using {selected_port}.", flush=True)
    token = os.getenv("TROUBLESHOOT_SESSION_TOKEN") or secrets.token_urlsafe(32)
    manager = SessionManager(providers={"gemma_api": GemmaAPI()},
                             executor=native_executor_from_env(), tool_seconds=45, run_seconds=300)
    app = create_app(manager, token, port=selected_port)
    print(f"Open http://127.0.0.1:{selected_port}")
    if not args.open:
        print(f"Local session token (paste into UI): {token}")
    print("Hosted Gemma is the only enabled provider. Native approval has a five-second freshness limit; hosted mode requires consent.", flush=True)
    server = BrowserServer(uvicorn.Config(app, host="127.0.0.1", port=selected_port,
                                           access_log=False, proxy_headers=False))
    if args.open:
        server.launch_url = f"http://127.0.0.1:{selected_port}/#session={token}"
    try:
        server.run(sockets=[listener])
    finally:
        listener.close()


if __name__ == "__main__":
    main()
