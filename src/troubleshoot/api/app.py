"""Single-user, process-local API. The launcher binds only 127.0.0.1."""

import asyncio
import json
import secrets
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

from troubleshoot.contracts import ContractError, RunRequest, Target, fields
from troubleshoot.runtime.ports import RuntimeFailure


def create_app(manager, session_token, *, port=8765, web_root=None):
    if not isinstance(session_token, str) or len(session_token) < 32 or not session_token.isascii():
        raise ValueError("Session token must be at least 32 ASCII characters")
    authority = f"127.0.0.1:{port}"
    origin = f"http://{authority}"
    root = Path(web_root) if web_root else Path(__file__).resolve().parents[3] / "web"
    if web_root is None and not root.is_dir():
        root = Path(sys.prefix) / "share" / "troubleshoot" / "web"

    @asynccontextmanager
    async def lifespan(app):
        yield
        await manager.close()

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    app.state.manager = manager

    @app.middleware("http")
    async def protect(request, call_next):
        if request.headers.get("host") != authority:
            return JSONResponse({"error": "invalid_host"}, status_code=403)
        if request.headers.get("origin") not in (None, origin):
            return JSONResponse({"error": "invalid_origin"}, status_code=403)
        if request.headers.get("sec-fetch-site") == "cross-site":
            return JSONResponse({"error": "cross_site_denied"}, status_code=403)
        if request.url.path.startswith("/api/"):
            supplied = request.headers.get("authorization", "")
            if not secrets.compare_digest(supplied.encode(), f"Bearer {session_token}".encode()):
                return JSONResponse({"error": "unauthorized"}, status_code=401)
        response = await call_next(request)
        response.headers.update({
            "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer", "X-Frame-Options": "DENY",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; "
                "connect-src 'self'; img-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
        })
        return response

    @app.exception_handler(RuntimeFailure)
    async def runtime_error(request, exc):
        status = 404 if exc.code == "run_not_found" else (
            409 if exc.code == "invalid_approval" else 503)
        return JSONResponse({"error": exc.code}, status_code=status)

    @app.exception_handler(ContractError)
    async def contract_error(request, exc):
        return JSONResponse({"error": "invalid_request"}, status_code=400)

    async def body(request):
        if request.headers.get("content-type", "").split(";")[0] != "application/json":
            raise ContractError("JSON required")
        data = bytearray()
        async for chunk in request.stream():
            data.extend(chunk)
            if len(data) > 16_384:
                raise ContractError("Request too large")
        try:
            payload = json.loads(data)
        except (ValueError, UnicodeError):
            raise ContractError("Invalid JSON") from None
        if not isinstance(payload, dict):
            raise ContractError("Object required")
        return payload

    @app.get("/api/status")
    async def status():
        return manager.status()

    @app.get("/api/targets")
    async def targets():
        if manager.executor is None:
            return {"targets": [], "available": False}
        try:
            async with asyncio.timeout(manager.tool_seconds):
                items = await manager.executor.targets()
        except Exception:
            raise RuntimeFailure("target_inventory_unavailable") from None
        return {"targets": items[:50], "available": True}

    @app.post("/api/runs", status_code=202)
    async def start(request: Request):
        payload = await body(request)
        target = payload.pop("target", None)
        try:
            options = RunRequest(**payload)
        except TypeError:
            raise ContractError("Invalid run fields") from None
        run = manager.create(options, Target.from_dict(target) if target is not None else None)
        return {"run_id": run.id, "simulation": manager.simulation}

    @app.get("/api/runs/{run_id}")
    async def run_status(run_id: str):
        run = manager.get(run_id)
        return {"run_id": run.id, "state": run.state, "recovery": run.recovery,
                "cancel_requested": run.cancelled.is_set()}

    @app.post("/api/runs/{run_id}/cancel")
    async def cancel(run_id: str, request: Request):
        fields(await body(request), set())
        return manager.cancel(run_id)

    @app.post("/api/runs/{run_id}/decision")
    async def decision(run_id: str, request: Request):
        payload = fields(await body(request), {"token", "action_id", "approve"})
        return manager.decide(run_id, **payload)

    @app.get("/api/runs/{run_id}/events")
    async def events(run_id: str, request: Request):
        run = manager.get(run_id)
        try:
            cursor = int(request.headers.get("last-event-id", "0"))
        except ValueError:
            raise ContractError("Invalid cursor") from None
        if not 0 <= cursor <= len(run.events):
            raise ContractError("Invalid cursor")

        async def stream():
            index = cursor
            heartbeat = 0
            while True:
                if await request.is_disconnected():
                    return
                while index < len(run.events):
                    item = run.events[index]
                    yield f"id: {item['id']}\nevent: {item['type']}\ndata: {json.dumps(item)}\n\n"
                    index += 1
                if run.state == "complete":
                    return
                heartbeat += 1
                if heartbeat % 100 == 0:
                    yield ": heartbeat\n\n"
                await asyncio.sleep(0.1)

        return StreamingResponse(stream(), media_type="text/event-stream",
                                 headers={"X-Accel-Buffering": "no"})

    @app.get("/")
    async def index():
        return FileResponse(root / "index.html")

    @app.get("/app.js")
    async def script():
        return FileResponse(root / "app.js", media_type="text/javascript")

    @app.get("/style.css")
    async def style():
        return FileResponse(root / "style.css", media_type="text/css")

    return app
