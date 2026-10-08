import asyncio
import unittest

from troubleshoot.contracts import RunRequest
from troubleshoot.runtime.ports import RuntimeFailure
from troubleshoot.runtime.session import SessionManager
from fixtures import FixtureExecutor, FixtureProvider


class SessionTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.executor = FixtureExecutor()
        self.provider = FixtureProvider()
        self.manager = SessionManager({"ollama": self.provider}, self.executor, simulation=True)

    async def asyncTearDown(self):
        await self.manager.close()

    async def start(self, mode="repair"):
        run = self.manager.create(RunRequest("Synthetic complaint", mode=mode), self.executor.target)
        for _ in range(100):
            if run.state != "running":
                return run
            await asyncio.sleep(0.001)
        self.fail("Run did not reach approval/complete")

    def approve(self, run, value=True):
        self.manager.decide(run.id, run.approval["token"], "fixture-action", value)

    async def completed(self, run):
        await asyncio.wait_for(run.task, 2)
        return run.events[-1]["payload"]

    async def test_approved_action_uses_fresh_checks(self):
        run = await self.start()
        self.approve(run)
        self.assertEqual((await self.completed(run))["verdict"], "resolved")
        self.assertEqual(self.executor.executions, 1)
        self.assertEqual(self.executor.observations, 2)

    async def test_diagnose_never_mutates(self):
        run = await self.start("diagnose")
        self.assertEqual((await self.completed(run))["verdict"], "error")
        self.assertEqual(self.executor.executions, 0)

    async def test_token_replay_and_action_mismatch(self):
        run = await self.start()
        token = run.approval["token"]
        for bad_token, action in (("wrong", "fixture-action"), (token, "other")):
            with self.assertRaises(RuntimeFailure):
                self.manager.decide(run.id, bad_token, action, True)
        self.approve(run)
        with self.assertRaises(RuntimeFailure):
            self.manager.decide(run.id, token, "fixture-action", True)
        await self.completed(run)

    async def test_cross_run_approval(self):
        first, second = await self.start(), await self.start()
        with self.assertRaises(RuntimeFailure):
            self.manager.decide(second.id, first.approval["token"], "fixture-action", True)
        self.manager.cancel(first.id)
        self.manager.cancel(second.id)

    async def test_expiry(self):
        self.manager.approval_seconds = .01
        run = await self.start()
        token = run.approval["token"]
        self.assertEqual((await self.completed(run))["verdict"], "unresolved")
        with self.assertRaises(RuntimeFailure):
            self.manager.decide(run.id, token, "fixture-action", True)
        self.assertEqual(self.executor.executions, 0)

    async def test_reject(self):
        run = await self.start()
        self.approve(run, False)
        self.assertEqual((await self.completed(run))["verdict"], "unresolved")
        self.assertEqual(self.executor.executions, 0)

    async def test_cancel_pending_approval(self):
        run = await self.start()
        self.manager.cancel(run.id)
        self.assertEqual((await self.completed(run))["verdict"], "cancelled")
        self.assertEqual(self.executor.executions, 0)

    async def test_cancel_during_execution_preserves_recovery(self):
        self.executor.delay, self.executor.recovery = .02, "pending"
        run = await self.start()
        self.approve(run)
        await self.executor.started.wait()
        self.manager.cancel(run.id)
        result = await self.completed(run)
        self.assertEqual((result["verdict"], result["recovery"]), ("cancelled", "pending"))

    async def test_target_geometry_changes_block_execution(self):
        run = await self.start()
        self.executor.changed = True
        self.approve(run)
        self.assertEqual((await self.completed(run))["verdict"], "error")
        self.assertEqual(self.executor.executions, 0)

    async def test_action_tampering_rejected(self):
        run = await self.start()
        run.approval["action"]["arguments"]["command"] = "injected"
        with self.assertRaises(RuntimeFailure):
            self.approve(run)
        self.assertEqual(self.executor.executions, 0)

    async def test_pending_recovery_blocks_later_repairs(self):
        self.executor.error = True
        run = await self.start()
        self.approve(run)
        await self.completed(run)
        with self.assertRaises(RuntimeFailure) as caught:
            await self.start()
        self.assertEqual(caught.exception.code, "recovery_required")

    async def test_model_failure_redacted_and_no_fallback(self):
        self.provider.error = True
        run = await self.start()
        result = await self.completed(run)
        self.assertEqual(result["verdict"], "error")
        self.assertNotIn("secret", str(run.events))
        self.assertEqual(self.provider.calls, 1)

    async def test_tool_failure_retains_pending_recovery(self):
        self.executor.error = True
        run = await self.start()
        self.approve(run)
        result = await self.completed(run)
        self.assertEqual((result["verdict"], result["recovery"]), ("error", "pending"))

    async def test_partial_and_unresolved_are_not_success(self):
        for checks, expected in (([True, False], "partial"), ([False], "unresolved"), ([], "unresolved")):
            self.executor.passes = checks
            run = await self.start()
            self.approve(run)
            self.assertEqual((await self.completed(run))["verdict"], expected)

    async def test_missing_local_provider_never_uses_hosted(self):
        self.manager.providers = {"gemma_api": self.provider}
        with self.assertRaises(RuntimeFailure):
            self.manager.create(RunRequest("Synthetic"))
        self.assertEqual(self.provider.calls, 0)

    async def test_no_action_is_not_claimed_repaired(self):
        self.provider.action = False
        run = await self.start()
        self.assertEqual((await self.completed(run))["verdict"], "unresolved")
