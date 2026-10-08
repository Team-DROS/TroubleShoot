"""Integrated policy checks using unchanged owner executors and a synthetic worker.

No Windows service or window is modified by these tests.
"""

import asyncio
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from troubleshoot.contracts import RunRequest
from troubleshoot.runtime.native import NativeExecutorAdapter
from troubleshoot.runtime.ports import RuntimeFailure
from troubleshoot.runtime.session import SessionManager
from troubleshoot.windows.registry import WindowsExecutor
from fixtures import FixtureExecutor, FixtureProvider


class SyntheticWorker:
    def __init__(self):
        self.service = "Stopped"
        self.calls = []

    def run(self, worker, operation, payload):
        self.calls.append(operation)
        stamp = datetime.now(timezone.utc).isoformat()
        if operation == "system_snapshot":
            return {"observed_at": stamp, "os": "SYNTHETIC"}
        if operation == "spooler_status":
            return {"observed_at": stamp, "name": "Spooler", "status": self.service}
        if operation == "start_spooler":
            self.service = "Running"
            return {"observed_at": stamp, "changed": True}
        raise AssertionError(f"Unexpected synthetic operation: {operation}")


class ServiceProvider(FixtureProvider):
    async def decide(self, request):
        decision = await super().decide(request)
        decision["action"]["operation"] = "start_spooler"
        return decision


class NativeIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name)
        self.worker = SyntheticWorker()
        self.executor = NativeExecutorAdapter(WindowsExecutor(self.worker, self.path),
                                               recovery_dir=self.path)
        self.manager = SessionManager({"ollama": ServiceProvider()}, self.executor, simulation=True)

    async def asyncTearDown(self):
        await self.manager.close()
        self.directory.cleanup()

    async def approval_run(self):
        run = self.manager.create(RunRequest("Synthetic printer symptom", mode="repair"), self.executor.system_target)
        for _ in range(1000):
            if run.state == "awaiting_approval" or run.task.done():
                return run
            await asyncio.sleep(.001)
        self.fail("No native approval was requested")

    async def test_native_fingerprint_requires_human_approval_and_service_is_partial(self):
        with patch.object(self.executor, '_private_recovery_directory'):
            run = await self.approval_run()
            self.assertNotIn("start_spooler", self.worker.calls)
            event = next(e for e in run.events if e["type"] == "approval")
            self.assertEqual(len(event["payload"]["native_fingerprint"]), 64)
            self.manager.decide(run.id, run.approval["token"], "fixture-action", True)
            await asyncio.wait_for(run.task, 2)
        self.assertEqual(self.worker.service, "Running")
        self.assertEqual(run.events[-1]["payload"]["verdict"], "partial")
        self.assertEqual(len(list(self.path.glob('*.json'))), 0)

    async def test_native_rejection_changes_nothing(self):
        with patch.object(self.executor, '_private_recovery_directory'):
            run = await self.approval_run()
            self.manager.decide(run.id, run.approval["token"], "fixture-action", False)
            await asyncio.wait_for(run.task, 2)
        self.assertNotIn("start_spooler", self.worker.calls)
        self.assertEqual(self.worker.service, "Stopped")

    async def test_native_cancel_changes_nothing(self):
        with patch.object(self.executor, '_private_recovery_directory'):
            run = await self.approval_run()
            self.manager.cancel(run.id)
            await asyncio.wait_for(run.task, 2)
        self.assertEqual(run.events[-1]["payload"]["verdict"], "cancelled")
        self.assertNotIn("start_spooler", self.worker.calls)

    async def test_startup_recovery_blocks_new_repairs(self):
        (self.path / 'interrupted.json').write_text('{"state":"pending"}')
        with self.assertRaises(RuntimeFailure):
            self.manager.create(RunRequest("Synthetic", mode="repair"), self.executor.system_target)
        self.assertEqual(self.worker.calls, [])

    async def test_restore_and_unconsented_capture_are_never_model_actions(self):
        self.assertNotIn("restore_spooler_stopped", self.executor.operations)
        self.assertNotIn("capture_target", self.executor.operations)
        self.assertNotIn("graceful_close", self.executor.operations)
        self.assertEqual(set(self.executor.operations_for(self.executor.system_target)),
                         {"system_snapshot", "network_snapshot", "spooler_status", "start_spooler"})

    async def test_realistic_inference_delay_refreshes_observation(self):
        executor = FixtureExecutor()
        manager = SessionManager({"ollama": FixtureProvider(delay=5.1)}, executor, simulation=True)
        try:
            run = manager.create(RunRequest("Synthetic slow inference", mode="repair"), executor.target)
            for _ in range(100):
                if run.state == "awaiting_approval":
                    break
                await asyncio.sleep(.06)
            self.assertIsNotNone(run.approval)
            manager.decide(run.id, run.approval["token"], "fixture-action", True)
            await asyncio.wait_for(run.task, 2)
            self.assertEqual(run.events[-1]["payload"]["verdict"], "resolved")
            self.assertEqual(executor.observations, 3)
        finally:
            await manager.close()
